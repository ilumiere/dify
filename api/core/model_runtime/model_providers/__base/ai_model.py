import decimal
import os
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Optional

from pydantic import ConfigDict

from core.helper.position_helper import get_position_map, sort_by_position_map
from core.model_runtime.entities.common_entities import I18nObject
from core.model_runtime.entities.defaults import PARAMETER_RULE_TEMPLATE
from core.model_runtime.entities.model_entities import (
    AIModelEntity,
    DefaultParameterName,
    FetchFrom,
    ModelType,
    PriceConfig,
    PriceInfo,
    PriceType,
)
from core.model_runtime.errors.invoke import InvokeAuthorizationError, InvokeError
from core.model_runtime.model_providers.__base.tokenizers.gpt2_tokenzier import GPT2Tokenizer
from core.tools.utils.yaml_utils import load_yaml_file


class AIModel(ABC):
    """
    所有模型的基类。

    该类定义了模型的基本属性和方法，包括模型的类型、模型架构、启动时间等。
    它还包含了一些抽象方法，需要在子类中实现，如验证模型凭证和映射模型调用错误。
    """

    model_type: ModelType
    """
    模型的类型。
    """

    model_schemas: Optional[list[AIModelEntity]] = None
    """
    模型的架构列表，可选。
    """

    started_at: float = 0
    """
    模型启动的时间戳，默认为0。
    """

    # pydantic 配置
    model_config = ConfigDict(protected_namespaces=())
    """
    pydantic 配置，用于定义模型的配置选项。
    """

    @abstractmethod
    def validate_credentials(self, model: str, credentials: Mapping) -> None:
        """
        验证模型的凭证。

        :param model: 模型名称。
        :param credentials: 模型的凭证，通常是一个字典或映射对象。
        :return: 无返回值。
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        将模型调用错误映射到统一的错误类型。

        键是抛给调用者的错误类型，值是模型抛出的错误类型，需要转换为统一的错误类型供调用者使用。

        :return: 调用错误映射字典。
        """
        raise NotImplementedError

    def _transform_invoke_error(self, error: Exception) -> InvokeError:
        """
        将模型调用错误转换为统一的错误类型。

        :param error: 模型调用错误。
        :return: 统一的错误类型。
        """
        provider_name = self.__class__.__module__.split(".")[-3]
        """
        获取提供者的名称。
        """

        for invoke_error, model_errors in self._invoke_error_mapping.items():
            """
            遍历错误映射字典，查找匹配的错误类型。
            """
            if isinstance(error, tuple(model_errors)):
                """
                如果错误类型匹配，则根据错误类型返回相应的统一错误。
                """
                if invoke_error == InvokeAuthorizationError:
                    return invoke_error(
                        description=(
                            f"[{provider_name}] Incorrect model credentials provided, please check and try again."
                        )
                    )

                return invoke_error(description=f"[{provider_name}] {invoke_error.description}, {str(error)}")

        return InvokeError(description=f"[{provider_name}] Error: {str(error)}")
        """
        如果没有匹配的错误类型，则返回一个通用的调用错误。
        """

    def get_price(self, model: str, credentials: dict, price_type: PriceType, tokens: int) -> PriceInfo:
        """
        获取给定模型和令牌数的定价信息。

        :param model: 模型名称。
        :param credentials: 模型的凭证，通常是一个字典。
        :param price_type: 价格类型，如输入或输出。
        :param tokens: 令牌数。
        :return: 价格信息。
        """
        # 获取模型架构
        model_schema = self.get_model_schema(model, credentials)
        """
        从模型架构中获取模型的定价信息。
        """

        # 从预定义的模型架构中获取价格信息
        price_config: Optional[PriceConfig] = None
        if model_schema and model_schema.pricing:
            price_config = model_schema.pricing
        """
        如果模型架构存在且包含定价信息，则获取定价配置。
        """

        # 获取单价
        unit_price = None
        if price_config:
            if price_type == PriceType.INPUT:
                unit_price = price_config.input
            elif price_type == PriceType.OUTPUT and price_config.output is not None:
                unit_price = price_config.output
        """
        根据价格类型获取相应的单价。
        """

        if unit_price is None:
            return PriceInfo(
                unit_price=decimal.Decimal("0.0"),
                unit=decimal.Decimal("0.0"),
                total_amount=decimal.Decimal("0.0"),
                currency="USD",
            )
        """
        如果单价为空，则返回默认的价格信息。
        """

        # 计算总金额
        if not price_config:
            raise ValueError(f"Price config not found for model {model}")
        total_amount = tokens * unit_price * price_config.unit
        total_amount = total_amount.quantize(decimal.Decimal("0.0000001"), rounding=decimal.ROUND_HALF_UP)
        """
        计算总金额，并进行四舍五入。
        """

        return PriceInfo(
            unit_price=unit_price,
            unit=price_config.unit,
            total_amount=total_amount,
            currency=price_config.currency,
        )
        """
        返回包含单价、单位、总金额和货币类型的价格信息。
        """
    def predefined_models(self) -> list[AIModelEntity]:
        """
        获取给定提供者的所有预定义模型。

        该函数的主要用途是从指定路径加载预定义模型的配置文件（YAML格式），并将这些配置文件转换为AIModelEntity对象列表。
        如果模型架构已经缓存，则直接返回缓存的模型架构。

        :return: 返回一个包含所有预定义模型的AIModelEntity对象列表。
        """
        # 如果模型架构已经缓存，则直接返回缓存的模型架构
        if self.model_schemas:
            return self.model_schemas

        model_schemas = []

        # 获取模块名称
        model_type = self.__class__.__module__.split(".")[-1]

        # 获取提供者名称
        provider_name = self.__class__.__module__.split(".")[-3]

        # 获取当前类的路径
        current_path = os.path.abspath(__file__)
        # 获取当前路径的父路径
        # 通过两次使用 os.path.dirname，代码获取了当前文件的父目录的父目录路径，然后与 provider_name 和 model_type 拼接，形成了最终的路径。
        provider_model_type_path = os.path.join(
            os.path.dirname(os.path.dirname(current_path)), provider_name, model_type
        )

        # 获取provider_model_type_path下所有不以__开头的YAML文件路径
        model_schema_yaml_paths = [
            os.path.join(provider_model_type_path, model_schema_yaml)
            for model_schema_yaml in os.listdir(provider_model_type_path)
            if not model_schema_yaml.startswith("__")
            and not model_schema_yaml.startswith("_")
            and os.path.isfile(os.path.join(provider_model_type_path, model_schema_yaml))
            and model_schema_yaml.endswith(".yaml")
        ]

        # 获取_position.yaml文件路径
        position_map = get_position_map(provider_model_type_path)

        # 遍历所有model_schema_yaml_paths
        for model_schema_yaml_path in model_schema_yaml_paths:
            # 从YAML文件中读取数据
            yaml_data = load_yaml_file(model_schema_yaml_path)

            new_parameter_rules = []
            for parameter_rule in yaml_data.get("parameter_rules", []):
                if "use_template" in parameter_rule:
                    try:
                        default_parameter_name = DefaultParameterName.value_of(parameter_rule["use_template"])
                        default_parameter_rule = self._get_default_parameter_rule_variable_map(default_parameter_name)
                        copy_default_parameter_rule = default_parameter_rule.copy()
                        copy_default_parameter_rule.update(parameter_rule)
                        parameter_rule = copy_default_parameter_rule
                    except ValueError:
                        pass

                if "label" not in parameter_rule:
                    parameter_rule["label"] = {"zh_Hans": parameter_rule["name"], "en_US": parameter_rule["name"]}

                new_parameter_rules.append(parameter_rule)

            yaml_data["parameter_rules"] = new_parameter_rules

            if "label" not in yaml_data:
                yaml_data["label"] = {"zh_Hans": yaml_data["model"], "en_US": yaml_data["model"]}

            yaml_data["fetch_from"] = FetchFrom.PREDEFINED_MODEL.value

            try:
                # 将yaml_data转换为实体
                model_schema = AIModelEntity(**yaml_data)
            except Exception as e:
                model_schema_yaml_file_name = os.path.basename(model_schema_yaml_path).rstrip(".yaml")
                raise Exception(
                    f"Invalid model schema for {provider_name}.{model_type}.{model_schema_yaml_file_name}: {str(e)}"
                )

            # 缓存模型架构
            model_schemas.append(model_schema)

        # 根据位置重新排序模型架构
        model_schemas = sort_by_position_map(position_map, model_schemas, lambda x: x.model)

        # 缓存模型架构
        self.model_schemas = model_schemas

        return model_schemas
    def get_model_schema(self, model: str, credentials: Optional[Mapping] = None) -> Optional[AIModelEntity]:
        """
        根据模型名称和凭证获取模型架构。

        :param model: 模型名称，字符串类型，用于标识要获取的模型。
        :param credentials: 模型凭证，字典类型，可选参数，用于获取自定义模型架构。
        :return: 返回模型架构，类型为 AIModelEntity，如果未找到则返回 None。
        """
        # 获取预定义的模型列表
        models = self.predefined_models()

        # 将预定义的模型列表转换为字典，键为模型名称，值为模型对象
        model_map = {model.model: model for model in models}

        # 检查传入的模型名称是否在预定义模型字典中
        if model in model_map:
            # 如果在，则返回对应的模型架构
            return model_map[model]

        # 如果传入了凭证，尝试从凭证中获取自定义模型架构
        if credentials:
            model_schema = self.get_customizable_model_schema_from_credentials(model, credentials)
            # 如果成功获取到自定义模型架构，则返回该架构
            if model_schema:
                return model_schema

        # 如果未找到模型架构，则返回 None
        return None
    def get_customizable_model_schema_from_credentials(
        self, model: str, credentials: Mapping
    ) -> Optional[AIModelEntity]:
        """
        从凭证中获取可自定义的模型架构。

        该函数的主要用途是根据传入的模型名称和凭证，获取对应的可自定义模型架构。

        :param model: 模型名称，字符串类型，用于标识要获取的模型。
        :param credentials: 模型凭证，字典类型，包含用于获取自定义模型架构的必要信息。
        :return: 返回模型架构，类型为 AIModelEntity，如果未找到则返回 None。
        """
        # 调用内部方法 _get_customizable_model_schema 获取可自定义的模型架构
        return self._get_customizable_model_schema(model, credentials)

    def _get_customizable_model_schema(self, model: str, credentials: Mapping) -> Optional[AIModelEntity]:
        """
        获取可自定义的模型架构并填充模板。

        该函数的主要用途是根据传入的模型名称和凭证，获取对应的可自定义模型架构，并填充默认参数规则。

        :param model: 模型名称，字符串类型，用于标识要获取的模型。
        :param credentials: 模型凭证，字典类型，包含用于获取自定义模型架构的必要信息。
        :return: 返回填充后的模型架构，类型为 AIModelEntity，如果未找到则返回 None。
        """
        # 获取可自定义的模型架构
        schema = self.get_customizable_model_schema(model, credentials)

        # 如果未找到模型架构，则返回 None
        if not schema:
            return None

        # 填充模板
        new_parameter_rules = []
        for parameter_rule in schema.parameter_rules:
            # 如果参数规则使用了模板
            if parameter_rule.use_template:
                try:
                    # 获取默认参数名称
                    default_parameter_name = DefaultParameterName.value_of(parameter_rule.use_template)
                    # 获取默认参数规则
                    default_parameter_rule = self._get_default_parameter_rule_variable_map(default_parameter_name)

                    # 如果参数规则没有最大值且默认参数规则中有最大值，则填充最大值
                    if not parameter_rule.max and "max" in default_parameter_rule:
                        parameter_rule.max = default_parameter_rule["max"]
                    # 如果参数规则没有最小值且默认参数规则中有最小值，则填充最小值
                    if not parameter_rule.min and "min" in default_parameter_rule:
                        parameter_rule.min = default_parameter_rule["min"]
                    # 如果参数规则没有默认值且默认参数规则中有默认值，则填充默认值
                    if not parameter_rule.default and "default" in default_parameter_rule:
                        parameter_rule.default = default_parameter_rule["default"]
                    # 如果参数规则没有精度且默认参数规则中有精度，则填充精度
                    if not parameter_rule.precision and "precision" in default_parameter_rule:
                        parameter_rule.precision = default_parameter_rule["precision"]
                    # 如果参数规则没有必填项且默认参数规则中有必填项，则填充必填项
                    if not parameter_rule.required and "required" in default_parameter_rule:
                        parameter_rule.required = default_parameter_rule["required"]
                    # 如果参数规则没有帮助信息且默认参数规则中有帮助信息，则填充帮助信息
                    if not parameter_rule.help and "help" in default_parameter_rule:
                        parameter_rule.help = I18nObject(
                            en_US=default_parameter_rule["help"]["en_US"],
                        )
                    # 如果参数规则的帮助信息中没有英文且默认参数规则中有英文帮助信息，则填充英文帮助信息
                    if (
                        parameter_rule.help
                        and not parameter_rule.help.en_US
                        and ("help" in default_parameter_rule and "en_US" in default_parameter_rule["help"])
                    ):
                        parameter_rule.help.en_US = default_parameter_rule["help"]["en_US"]
                    # 如果参数规则的帮助信息中没有简体中文且默认参数规则中有简体中文帮助信息，则填充简体中文帮助信息
                    if (
                        parameter_rule.help
                        and not parameter_rule.help.zh_Hans
                        and ("help" in default_parameter_rule and "zh_Hans" in default_parameter_rule["help"])
                    ):
                        parameter_rule.help.zh_Hans = default_parameter_rule["help"].get(
                            "zh_Hans", default_parameter_rule["help"]["en_US"]
                        )
                except ValueError:
                    # 如果发生 ValueError 异常，则忽略并继续处理下一个参数规则
                    pass

            # 将填充后的参数规则添加到新列表中
            new_parameter_rules.append(parameter_rule)

        # 更新模型架构的参数规则
        schema.parameter_rules = new_parameter_rules

        # 返回填充后的模型架构
        return schema

    def get_customizable_model_schema(self, model: str, credentials: Mapping) -> Optional[AIModelEntity]:
        """
        获取可定制的模型架构

        该函数的主要用途是根据给定的模型名称和凭证，获取可定制的模型架构。

        :param model: 模型名称，字符串类型，用于标识要获取架构的模型。
        :param credentials: 模型凭证，Mapping 类型，包含访问模型所需的凭证信息。
        :return: 返回一个 AIModelEntity 类型的对象，表示模型的架构。如果无法获取架构，则返回 None。
        """
        return None

    def _get_default_parameter_rule_variable_map(self, name: DefaultParameterName) -> dict:
        """
        获取给定名称的默认参数规则

        该函数的主要用途是根据参数名称，从预定义的模板中获取默认的参数规则。

        :param name: 参数名称，DefaultParameterName 类型，用于标识要获取规则的参数。
        :return: 返回一个字典，表示默认的参数规则。如果参数名称无效，则抛出异常。
        """
        default_parameter_rule = PARAMETER_RULE_TEMPLATE.get(name)

        if not default_parameter_rule:
            raise Exception(f"Invalid model parameter rule name {name}")

        return default_parameter_rule

    def _get_num_tokens_by_gpt2(self, text: str) -> int:
        """
        Get number of tokens for given prompt messages by gpt2
        Some provider models do not provide an interface for obtaining the number of tokens.
        Here, the gpt2 tokenizer is used to calculate the number of tokens.
        This method can be executed offline, and the gpt2 tokenizer has been cached in the project.

        :param text: plain text of prompt. You need to convert the original message to plain text
        :return: number of tokens
        """
        return GPT2Tokenizer.get_num_tokens(text)

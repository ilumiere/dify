import os
from abc import ABC, abstractmethod
from typing import Optional

from core.helper.module_import_helper import get_subclasses_from_module, import_module_from_source
from core.model_runtime.entities.model_entities import AIModelEntity, ModelType
from core.model_runtime.entities.provider_entities import ProviderEntity
from core.model_runtime.model_providers.__base.ai_model import AIModel
from core.tools.utils.yaml_utils import load_yaml_file


class ModelProvider(ABC):
    """
    模型提供者基类，定义了模型提供者的基本行为和属性。

    该类是一个抽象基类，继承自 ABC，用于定义模型提供者的通用接口和行为。
    它包含两个主要属性：`provider_schema` 和 `model_instance_map`，分别用于存储提供者模式和模型实例映射。
    """

    provider_schema: Optional[ProviderEntity] = None
    """
    provider_schema 是一个可选的 ProviderEntity 实例，用于存储提供者的模式。
    该属性在首次获取提供者模式时会被缓存，以避免重复加载。
    """

    model_instance_map: dict[str, AIModel] = {}
    """
    model_instance_map 是一个字典，用于存储模型类型与模型实例的映射关系。
    键为提供者名称和模型类型的组合，值为对应的 AIModel 实例。
    """

    @abstractmethod
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials
        You can choose any validate_credentials method of model type or implement validate method by yourself,
        such as: get model list api

        这是一个抽象方法，需要在子类中实现。
        该方法用于验证提供者的凭证，如果验证失败，则抛出异常。

        :param credentials: 提供者的凭证，凭证格式定义在 `provider_credential_schema` 中。
        """
        raise NotImplementedError

    def get_provider_schema(self) -> ProviderEntity:
        """
        获取提供者的模式。

        该方法首先检查是否已经缓存了提供者模式，如果有则直接返回缓存的模式。
        如果没有缓存，则从 YAML 文件中加载模式，并将其转换为 ProviderEntity 实例。
        加载和转换过程中如果发生异常，则抛出异常。

        :return: 提供者的模式，类型为 ProviderEntity。
        """
        if self.provider_schema:
            return self.provider_schema

        # 获取当前路径的目录名
        provider_name = self.__class__.__module__.split(".")[-1]

        # 获取模型提供者类的路径
        base_path = os.path.abspath(__file__)
        current_path = os.path.join(os.path.dirname(os.path.dirname(base_path)), provider_name)

        # 从 YAML 文件中读取提供者模式
        yaml_path = os.path.join(current_path, f"{provider_name}.yaml")
        yaml_data = load_yaml_file(yaml_path)

        try:
            # 将 YAML 数据转换为实体
            provider_schema = ProviderEntity(**yaml_data)
        except Exception as e:
            raise Exception(f"Invalid provider schema for {provider_name}: {str(e)}")

        # 缓存模式
        self.provider_schema = provider_schema

        return provider_schema

    def models(self, model_type: ModelType) -> list[AIModelEntity]:
        """
        获取给定模型类型的所有模型。

        该方法首先获取提供者的模式，然后检查该模式是否支持指定的模型类型。
        如果不支持，则返回空列表。
        如果支持，则获取该模型类型的模型实例，并返回其预定义的模型列表。

        :param model_type: 模型类型，定义在 `ModelType` 中。
        :return: 模型列表，类型为 list[AIModelEntity]。
        """
        provider_schema = self.get_provider_schema()
        if model_type not in provider_schema.supported_model_types:
            return []

        # 获取模型类型的模型实例
        model_instance = self.get_model_instance(model_type)

        # 获取预定义的模型
        models = model_instance.predefined_models()

        # 返回模型
        return models

    def get_model_instance(self, model_type: ModelType) -> AIModel:
        """
        获取模型实例。

        该方法的主要用途是根据给定的模型类型动态加载并返回相应的模型实例。如果该模型类型的实例已经缓存，则直接返回缓存的实例，否则动态加载并缓存该实例。

        :param model_type: 模型类型，定义在 `ModelType` 中。该参数用于指定需要获取的模型类型。
        :return: 模型实例，类型为 AIModel。返回的实例是根据 `model_type` 动态加载的模型实例。
        """
        # 获取当前路径的目录名
        provider_name = self.__class__.__module__.split(".")[-1]

        # 检查是否已经缓存了该模型类型的模型实例
        if f"{provider_name}.{model_type.value}" in self.model_instance_map:
            return self.model_instance_map[f"{provider_name}.{model_type.value}"]

        # 获取模型类型类的路径
        base_path = os.path.abspath(__file__)
        model_type_name = model_type.value.replace("-", "_")
        model_type_path = os.path.join(os.path.dirname(os.path.dirname(base_path)), provider_name, model_type_name)
        model_type_py_path = os.path.join(model_type_path, f"{model_type_name}.py")

        # 检查模型类型路径和文件是否存在
        if not os.path.isdir(model_type_path) or not os.path.exists(model_type_py_path):
            raise Exception(f"Invalid model type {model_type} for provider {provider_name}")

        # 动态加载 {model_type_name}.py 文件并查找 AIModel 的子类
        parent_module = ".".join(self.__class__.__module__.split(".")[:-1])
        mod = import_module_from_source(
            module_name=f"{parent_module}.{model_type_name}.{model_type_name}", py_file_path=model_type_py_path
        )
        model_class = next(
            filter(
                lambda x: x.__module__ == mod.__name__ and not x.__abstractmethods__,
                get_subclasses_from_module(mod, AIModel),
            ),
            None,
        )
        if not model_class:
            raise Exception(f"Missing AIModel Class for model type {model_type} in {model_type_py_path}")

        # 创建模型实例并缓存
        model_instance_map = model_class()
        self.model_instance_map[f"{provider_name}.{model_type.value}"] = model_instance_map

        return model_instance_map

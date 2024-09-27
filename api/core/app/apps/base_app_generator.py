from collections.abc import Mapping
from typing import Any, Optional

from core.app.app_config.entities import AppConfig, VariableEntity, VariableEntityType


class BaseAppGenerator:
    """
    这是一个基类，用于生成应用程序的输入清理和验证逻辑。
    主要用途是根据应用程序配置过滤和验证用户输入，确保输入数据的完整性和正确性。
    """

    def _get_cleaned_inputs(self, user_inputs: Optional[Mapping[str, Any]], app_config: AppConfig) -> Mapping[str, Any]:
        """
        该方法用于清理和过滤用户输入，确保输入数据符合应用程序配置的要求。

        参数:
        - user_inputs: 用户输入的字典，可能为 None。
        - app_config: 应用程序配置对象，包含变量定义。

        返回值:
        - 一个字典，包含经过验证和清理的用户输入。
        """
        user_inputs = user_inputs or {}  # 如果 user_inputs 为 None，则初始化为空字典
        # 从表单配置中过滤输入变量，处理必填字段、默认值和选项值
        variables = app_config.variables  # 获取应用程序配置中的变量列表
        # 遍历变量列表，对每个变量进行输入验证
        filtered_inputs = {var.variable: self._validate_input(inputs=user_inputs, var=var) for var in variables}
        # 对验证后的输入进行清理
        filtered_inputs = {k: self._sanitize_value(v) for k, v in filtered_inputs.items()}
        return filtered_inputs  # 返回清理后的输入字典

    def _validate_input(self, *, inputs: Mapping[str, Any], var: VariableEntity):
        """
        该方法用于验证单个输入变量，确保其符合变量定义的要求。

        参数:
        - inputs: 用户输入的字典。
        - var: 变量实体对象，包含变量的定义。

        返回值:
        - 验证后的用户输入值。
        """
        user_input_value = inputs.get(var.variable)  # 获取用户输入的值
        if var.required and not user_input_value:
            # 如果变量是必填的且用户未提供输入，抛出异常
            raise ValueError(f"{var.variable} is required in input form")
        if not var.required and not user_input_value:
            # TODO: should we return None here if the default value is None?
            return var.default or ""
        if (
            var.type
            in {
                VariableEntityType.TEXT_INPUT,
                VariableEntityType.SELECT,
                VariableEntityType.PARAGRAPH,
            }
            and user_input_value
            and not isinstance(user_input_value, str)
        ):
            # 如果变量类型是文本输入、选择或段落，且用户输入不是字符串，抛出异常
            raise ValueError(f"(type '{var.type}') {var.variable} in input form must be a string")
        if var.type == VariableEntityType.NUMBER and isinstance(user_input_value, str):
            # 如果变量类型是数字且用户输入是字符串，尝试将其转换为数字
            try:
                if "." in user_input_value:
                    return float(user_input_value)  # 转换为浮点数
                else:
                    return int(user_input_value)  # 转换为整数
            except ValueError:
                # 如果转换失败，抛出异常
                raise ValueError(f"{var.variable} in input form must be a valid number")
        if var.type == VariableEntityType.SELECT:
            # 如果变量类型是选择，验证用户输入是否在选项列表中
            options = var.options or []
            if user_input_value not in options:
                raise ValueError(f"{var.variable} in input form must be one of the following: {options}")
        elif var.type in {VariableEntityType.TEXT_INPUT, VariableEntityType.PARAGRAPH}:
            # 如果变量类型是文本输入或段落，验证输入长度是否超过最大长度
            if var.max_length and user_input_value and len(user_input_value) > var.max_length:
                raise ValueError(f"{var.variable} in input form must be less than {var.max_length} characters")

        return user_input_value  # 返回验证后的用户输入值

    def _sanitize_value(self, value: Any) -> Any:
        """
        该方法用于清理输入值，去除可能的非法字符。

        参数:
        - value: 需要清理的输入值。

        返回值:
        - 清理后的输入值。
        """
        if isinstance(value, str):
            return value.replace("\x00", "")  # 去除字符串中的空字符
        return value  # 非字符串类型的值直接返回

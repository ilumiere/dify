from pydantic import BaseModel


class VariableSelector(BaseModel):
    """
    Variable Selector 类用于选择和处理变量及其相关值的选择器。

    该类的主要用途是定义一个变量选择器，其中包含一个变量名称和一组用于选择该变量值的选择器。

    属性:
    - variable: str
        变量的名称。该字符串表示要选择的变量的标识符。
    - value_selector: list[str]
        用于选择变量值的选择器列表。每个字符串表示一个选择器，用于从变量中提取特定的值。
    """

    variable: str
    """
    变量的名称。该字符串表示要选择的变量的标识符。
    """

    value_selector: list[str]
    """
    用于选择变量值的选择器列表。每个字符串表示一个选择器，用于从变量中提取特定的值。
    """


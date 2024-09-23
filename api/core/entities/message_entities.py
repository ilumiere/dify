import enum
from typing import Any

from pydantic import BaseModel


# PromptMessageFileType 枚举类用于定义消息文件的类型。
# 目前只包含一个类型：IMAGE，表示图像文件。
class PromptMessageFileType(enum.Enum):
    IMAGE = "image"  # 表示图像文件类型

    # value_of 静态方法用于根据值查找对应的枚举成员。
    # 参数:
    #   value (str): 要查找的枚举值。
    # 返回值:
    #   PromptMessageFileType: 匹配的枚举成员。
    # 异常:
    #   ValueError: 如果没有找到匹配的枚举成员，则抛出此异常。
    @staticmethod
    def value_of(value):
        for member in PromptMessageFileType:  # 遍历枚举成员
            if member.value == value:  # 检查当前成员的值是否与传入的值匹配
                return member  # 返回匹配的枚举成员
        raise ValueError(f"No matching enum found for value '{value}'")  # 如果没有匹配的成员，抛出异常


# PromptMessageFile 类用于表示消息文件的基本结构。
# 继承自 pydantic 的 BaseModel，用于数据验证和序列化。
class PromptMessageFile(BaseModel):
    type: PromptMessageFileType  # 文件类型，必须是 PromptMessageFileType 枚举中的一个值
    data: Any = None  # 文件数据，默认为 None


# ImagePromptMessageFile 类用于表示图像消息文件。
# 继承自 PromptMessageFile，增加了图像细节的定义。
class ImagePromptMessageFile(PromptMessageFile):
    # DETAIL 枚举类用于定义图像的细节级别。
    class DETAIL(enum.Enum):
        LOW = "low"  # 低细节级别
        HIGH = "high"  # 高细节级别
    # Python 3.6 引入类型注解时开始流行的一种方式，它允许直接在类定义中为属性赋值，
    type: PromptMessageFileType = PromptMessageFileType.IMAGE  # 文件类型默认为图像类型
    detail: DETAIL = DETAIL.LOW  # 图像细节级别默认为低细节

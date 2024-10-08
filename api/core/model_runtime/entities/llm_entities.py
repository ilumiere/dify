from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from core.model_runtime.entities.message_entities import AssistantPromptMessage, PromptMessage
from core.model_runtime.entities.model_entities import ModelUsage, PriceInfo


class LLMMode(Enum):
    """
    用于表示大型语言模型模式的枚举类。

    该类定义了两种模式：
    - COMPLETION: 完成模式，用于生成文本补全。
    - CHAT: 聊天模式，用于生成对话响应。
    """

    COMPLETION = "completion"
    CHAT = "chat"

    @classmethod
    def value_of(cls, value: str) -> "LLMMode":
        """
        根据给定的模式值获取对应的枚举实例。

        :param value: 模式值，字符串类型。
        :return: 对应的LLMMode枚举实例。
        :raises ValueError: 如果提供的模式值无效，则抛出此异常。
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"无效的模式值 {value}")

class LLMUsage(ModelUsage):
    """
    用于表示大型语言模型使用情况的模型类。

    该类包含以下属性：
    - prompt_tokens: 提示令牌数量，整数类型。
    - prompt_unit_price: 提示令牌的单价，Decimal类型。
    - prompt_price_unit: 提示令牌的价格单位，Decimal类型。
    - prompt_price: 提示令牌的总价格，Decimal类型。
    - completion_tokens: 完成令牌数量，整数类型。
    - completion_unit_price: 完成令牌的单价，Decimal类型。
    - completion_price_unit: 完成令牌的价格单位，Decimal类型。
    - completion_price: 完成令牌的总价格，Decimal类型。
    - total_tokens: 总令牌数量，整数类型。
    - total_price: 总价格，Decimal类型。
    - currency: 货币单位，字符串类型。
    - latency: 延迟时间，浮点数类型。
    """

    prompt_tokens: int
    prompt_unit_price: Decimal
    prompt_price_unit: Decimal
    prompt_price: Decimal
    completion_tokens: int
    completion_unit_price: Decimal
    completion_price_unit: Decimal
    completion_price: Decimal
    total_tokens: int
    total_price: Decimal
    currency: str
    latency: float

    @classmethod
    def empty_usage(cls):
        """
        创建一个空的LLMUsage实例。

        :return: 一个所有属性值均为0或默认值的LLMUsage实例。
        """
        return cls(
            prompt_tokens=0,
            prompt_unit_price=Decimal("0.0"),
            prompt_price_unit=Decimal("0.0"),
            prompt_price=Decimal("0.0"),
            completion_tokens=0,
            completion_unit_price=Decimal("0.0"),
            completion_price_unit=Decimal("0.0"),
            completion_price=Decimal("0.0"),
            total_tokens=0,
            total_price=Decimal("0.0"),
            currency="USD",
            latency=0.0,
        )

    def plus(self, other: "LLMUsage") -> "LLMUsage":
        """
        将两个LLMUsage实例相加。

        :param other: 另一个LLMUsage实例，用于相加。
        :return: 一个新的LLMUsage实例，其属性值为两个实例属性值的和。
        """
        if self.total_tokens == 0:
            return other
        else:
            return LLMUsage(
                prompt_tokens=self.prompt_tokens + other.prompt_tokens,
                # 使用 other 实例的 prompt_unit_price。这是因为 prompt_unit_price 通常是一个固定的值，不会因为相加而改变。
                prompt_unit_price=other.prompt_unit_price,
                prompt_price_unit=other.prompt_price_unit,
                prompt_price=self.prompt_price + other.prompt_price,
                completion_tokens=self.completion_tokens + other.completion_tokens,
                # 固定值
                completion_unit_price=other.completion_unit_price,
                completion_price_unit=other.completion_price_unit,
                completion_price=self.completion_price + other.completion_price,
                total_tokens=self.total_tokens + other.total_tokens,
                total_price=self.total_price + other.total_price,
                currency=other.currency,
                latency=self.latency + other.latency,
            )

    def __add__(self, other: "LLMUsage") -> "LLMUsage":
        """
        重载加法运算符，用于将两个LLMUsage实例相加。
        在 Python 中，__add__ 是一个特殊方法（也称为魔术方法），用于重载加法运算符 +。通过定义 __add__ 方法，你可以自定义两个对象相加的行为

        :param other: 另一个LLMUsage实例，用于相加。
        :return: 一个新的LLMUsage实例，其属性值为两个实例属性值的和。
        """
        return self.plus(other)


class LLMResult(BaseModel):
    """
    用于表示大型语言模型结果的模型类。

    该类包含以下属性：
    - model: 模型名称，字符串类型。
    - prompt_messages: 提示消息列表，列表类型，元素为PromptMessage实例。
    - message: 助手生成的消息，AssistantPromptMessage类型。
    - usage: 使用情况，LLMUsage类型。
    - system_fingerprint: 系统指纹，可选字符串类型。
    """

    model: str
    prompt_messages: list[PromptMessage]
    message: AssistantPromptMessage
    usage: LLMUsage
    system_fingerprint: Optional[str] = None


class LLMResultChunkDelta(BaseModel):
    """
    用于表示大型语言模型结果块的增量模型类。

    该类包含以下属性：
    - index: 块的索引，整数类型。
    - message: 助手生成的消息，AssistantPromptMessage类型。
    - usage: 使用情况，可选的LLMUsage类型。
    - finish_reason: 完成原因，可选字符串类型。
    """

    index: int
    message: AssistantPromptMessage
    usage: Optional[LLMUsage] = None
    finish_reason: Optional[str] = None


class LLMResultChunk(BaseModel):
    """
    用于表示大型语言模型结果块的模型类。

    该类包含以下属性：
    - model: 模型名称，字符串类型。
    - prompt_messages: 提示消息列表，列表类型，元素为PromptMessage实例。
    - system_fingerprint: 系统指纹，可选字符串类型。
    - delta: 结果块的增量，LLMResultChunkDelta类型。
    """

    model: str
    prompt_messages: list[PromptMessage]
    system_fingerprint: Optional[str] = None
    delta: LLMResultChunkDelta


class NumTokensResult(PriceInfo):
    """
    用于表示令牌数量结果的模型类。

    该类包含以下属性：
    - tokens: 令牌数量，整数类型。
    """

    tokens: int

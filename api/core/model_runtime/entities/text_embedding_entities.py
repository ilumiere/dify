from decimal import Decimal

from pydantic import BaseModel

from core.model_runtime.entities.model_entities import ModelUsage


class EmbeddingUsage(ModelUsage):
    """
    嵌入使用情况的模型类。

    该类继承自 `ModelUsage`，用于记录与嵌入相关的使用情况，包括令牌数量、价格、货币类型和延迟时间。

    属性:
    - `tokens`: 使用的令牌数量，类型为 `int`。
    - `total_tokens`: 总令牌数量，类型为 `int`。
    - `unit_price`: 每个令牌的单价，类型为 `Decimal`。
    - `price_unit`: 价格单位，类型为 `Decimal`。
    - `total_price`: 总价格，类型为 `Decimal`。
    - `currency`: 货币类型，类型为 `str`。
    - `latency`: 延迟时间，类型为 `float`。
    """

    tokens: int
    total_tokens: int
    unit_price: Decimal
    price_unit: Decimal
    total_price: Decimal
    currency: str
    latency: float


class TextEmbeddingResult(BaseModel):
    """
    文本嵌入结果的模型类。

    该类用于存储文本嵌入的结果，包括使用的模型名称、嵌入向量和相关的使用情况。

    属性:
    - `model`: 使用的模型名称，类型为 `str`。
    - `embeddings`: 嵌入向量列表，每个嵌入向量是一个浮点数列表，类型为 `list[list[float]]`。
    - `usage`: 嵌入使用情况，类型为 `EmbeddingUsage`。
    """

    model: str
    embeddings: list[list[float]]
    usage: EmbeddingUsage

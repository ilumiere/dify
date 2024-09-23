from pydantic import BaseModel

class RerankDocument(BaseModel):
    """
    用于表示重新排序文档的模型类。

    该类包含以下属性：
    - index: 文档的索引，表示文档在原始列表中的位置。
    - text: 文档的文本内容。
    - score: 文档的得分，表示文档在重新排序后的重要性或相关性。
    """

    index: int  # 文档的索引
    text: str  # 文档的文本内容
    score: float  # 文档的得分


class RerankResult(BaseModel):
    """
    用于表示重新排序结果的模型类。

    该类包含以下属性：
    - model: 用于重新排序的模型名称。
    - docs: 重新排序后的文档列表，每个文档由RerankDocument类表示。
    """

    model: str  # 用于重新排序的模型名称
    docs: list[RerankDocument]  # 重新排序后的文档列表


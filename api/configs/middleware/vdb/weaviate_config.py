from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class WeaviateConfig(BaseSettings):
    """
    该类用于配置与 Weaviate 数据库的连接设置。

    主要用途和功能：
    - 提供与 Weaviate 数据库连接所需的配置参数。
    - 使用 Pydantic 的 Field 来定义每个配置项的类型、描述和默认值。

    属性详细解释：
    - WEAVIATE_ENDPOINT: 可选字符串，表示 Weaviate 的端点 URL。默认值为 None，表示未设置。
    - WEAVIATE_API_KEY: 可选字符串，表示 Weaviate 的 API 密钥。默认值为 None，表示未设置。
    - WEAVIATE_GRPC_ENABLED: 布尔值，表示是否启用 gRPC 进行 Weaviate 连接。默认值为 True，表示启用。
    - WEAVIATE_BATCH_SIZE: 正整数，表示 Weaviate 的批处理大小。默认值为 100，表示每次处理 100 个数据项。
    """

    WEAVIATE_ENDPOINT: Optional[str] = Field(
        description="Weaviate 端点 URL",
        default=None,
    )

    WEAVIATE_API_KEY: Optional[str] = Field(
        description="Weaviate API 密钥",
        default=None,
    )

    WEAVIATE_GRPC_ENABLED: bool = Field(
        description="是否启用 gRPC 进行 Weaviate 连接",
        default=True,
    )

    WEAVIATE_BATCH_SIZE: PositiveInt = Field(
        description="Weaviate 批处理大小",
        default=100,
    )

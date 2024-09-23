from typing import Optional

from pydantic import Field, NonNegativeInt, PositiveInt
from pydantic_settings import BaseSettings


class QdrantConfig(BaseSettings):
    """
    QdrantConfig 类用于配置与 Qdrant 数据库的连接参数。

    主要用途：
    - 提供与 Qdrant 数据库连接所需的配置参数。
    - 这些参数包括 Qdrant 的 URL、API 密钥、客户端超时时间、是否启用 gRPC 支持以及 gRPC 端口号。

    每个属性的详细解释：
    - QDRANT_URL: 用于指定 Qdrant 数据库的 URL。默认值为 None，表示未指定 URL。
    - QDRANT_API_KEY: 用于指定连接 Qdrant 数据库所需的 API 密钥。默认值为 None，表示未指定 API 密钥。
    - QDRANT_CLIENT_TIMEOUT: 用于指定 Qdrant 客户端的超时时间（以秒为单位）。默认值为 20 秒，表示客户端在 20 秒后超时。
    - QDRANT_GRPC_ENABLED: 用于指定是否启用 gRPC 支持。默认值为 False，表示不启用 gRPC 支持。
    - QDRANT_GRPC_PORT: 用于指定 Qdrant 的 gRPC 端口号。默认值为 6334，表示 Qdrant 的默认 gRPC 端口。
    """

    QDRANT_URL: Optional[str] = Field(
        description="Qdrant 数据库的 URL。如果未提供，默认为 None。",
        default=None,
    )
    """
    Qdrant 数据库的 URL，类型为可选字符串。
    - 描述: 用于指定 Qdrant 数据库的 URL。
    - 默认值: None，表示未指定 URL。
    """

    QDRANT_API_KEY: Optional[str] = Field(
        description="Qdrant 数据库的 API 密钥。如果未提供，默认为 None。",
        default=None,
    )
    """
    Qdrant 数据库的 API 密钥，类型为可选字符串。
    - 描述: 用于指定连接 Qdrant 数据库所需的 API 密钥。
    - 默认值: None，表示未指定 API 密钥。
    """

    QDRANT_CLIENT_TIMEOUT: NonNegativeInt = Field(
        description="Qdrant 客户端的超时时间（以秒为单位）。必须为非负整数，默认值为 20 秒。",
        default=20,
    )
    """
    Qdrant 客户端的超时时间，类型为非负整数。
    - 描述: 用于指定 Qdrant 客户端的超时时间。
    - 默认值: 20，表示客户端在 20 秒后超时。
    """

    QDRANT_GRPC_ENABLED: bool = Field(
        description="是否启用 gRPC 支持。默认值为 False，表示不启用 gRPC 支持。",
        default=False,
    )
    """
    gRPC 支持的启用状态，类型为布尔值。
    - 描述: 用于指定是否启用 gRPC 支持。
    - 默认值: False，表示不启用 gRPC 支持。
    """

    QDRANT_GRPC_PORT: PositiveInt = Field(
        description="Qdrant 的 gRPC 端口号。必须为正整数，默认值为 6334。",
        default=6334,
    )
    """
    Qdrant 的 gRPC 端口号，类型为正整数。
    - 描述: 用于指定 Qdrant 的 gRPC 端口号。
    - 默认值: 6334，表示 Qdrant 的默认 gRPC 端口。
    """

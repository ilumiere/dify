from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class ChromaConfig(BaseSettings):
    """
    ChromaConfig 类用于定义与 Chroma 数据库相关的配置参数。
    该类继承自 BaseSettings，使用 Pydantic 的 Field 来定义每个配置项的类型、描述和默认值。
    这些配置项用于连接和配置 Chroma 数据库的各个方面，包括主机、端口、租户、数据库名称、认证提供者和认证凭据。
    """

    CHROMA_HOST: Optional[str] = Field(
        description="Chroma 数据库的主机地址。如果未提供，默认为 None。",
        default=None,
    )

    CHROMA_PORT: PositiveInt = Field(
        description="Chroma 数据库的端口号。必须为正整数，默认值为 8000。",
        default=8000,
    )

    CHROMA_TENANT: Optional[str] = Field(
        description="Chroma 数据库的租户名称。如果未提供，默认为 None。",
        default=None,
    )

    CHROMA_DATABASE: Optional[str] = Field(
        description="Chroma 数据库的名称。如果未提供，默认为 None。",
        default=None,
    )

    CHROMA_AUTH_PROVIDER: Optional[str] = Field(
        description="Chroma 数据库的认证提供者。如果未提供，默认为 None。",
        default=None,
    )

    CHROMA_AUTH_CREDENTIALS: Optional[str] = Field(
        description="Chroma 数据库的认证凭据。如果未提供，默认为 None。",
        default=None,
    )

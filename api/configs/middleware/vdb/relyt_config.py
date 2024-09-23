from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class RelytConfig(BaseSettings):
    """
    RelytConfig 类用于定义与 Relyt 服务相关的配置参数。
    这些配置参数包括 Relyt 服务的主机地址、端口号、用户名、密码以及数据库名称。
    该类继承自 `BaseSettings`，允许通过环境变量或配置文件加载这些配置。
    """

    RELYT_HOST: Optional[str] = Field(
        description="Relyt 服务的主机地址。如果未提供，默认为 None。",
        default=None,
    )

    RELYT_PORT: PositiveInt = Field(
        description="Relyt 服务的端口号。必须为正整数，默认值为 9200。",
        default=9200,
    )

    RELYT_USER: Optional[str] = Field(
        description="连接 Relyt 服务的用户名。如果未提供，默认为 None。",
        default=None,
    )

    RELYT_PASSWORD: Optional[str] = Field(
        description="连接 Relyt 服务的密码。如果未提供，默认为 None。",
        default=None,
    )

    RELYT_DATABASE: Optional[str] = Field(
        description="Relyt 服务使用的数据库名称。如果未提供，默认为 'default'。",
        default="default",
    )

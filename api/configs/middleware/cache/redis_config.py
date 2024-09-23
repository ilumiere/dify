from typing import Optional

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt
from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    """
    RedisConfig 类用于定义与 Redis 缓存相关的配置参数。
    这些配置参数包括 Redis 服务器的主机、端口、用户名、密码、数据库 ID 等。
    此外，还支持 Redis Sentinel 模式的配置，包括 Sentinel 节点、服务名称、用户名、密码和套接字超时时间。
    """

    REDIS_HOST: str = Field(
        description="Redis 服务器的主机地址",
        default="localhost",
    )
    """
    Redis 服务器的主机地址。默认值为 'localhost'，表示 Redis 服务器运行在本地。
    """

    REDIS_PORT: PositiveInt = Field(
        description="Redis 服务器的端口号",
        default=6379,
    )
    """
    Redis 服务器的端口号。默认值为 6379，这是 Redis 的标准端口号。
    """

    REDIS_USERNAME: Optional[str] = Field(
        description="Redis 服务器的用户名",
        default=None,
    )
    """
    Redis 服务器的用户名。如果 Redis 服务器不需要身份验证，则此项可以为 None。
    """

    REDIS_PASSWORD: Optional[str] = Field(
        description="Redis 服务器的密码",
        default=None,
    )
    """
    Redis 服务器的密码。如果 Redis 服务器不需要身份验证，则此项可以为 None。
    """

    REDIS_DB: NonNegativeInt = Field(
        description="Redis 数据库的 ID，默认为 0",
        default=0,
    )
    """
    Redis 数据库的 ID。默认值为 0，表示使用第一个数据库。
    """

    REDIS_USE_SSL: bool = Field(
        description="是否使用 SSL 进行 Redis 连接",
        default=False,
    )
    """
    是否使用 SSL 进行 Redis 连接。默认值为 False，表示不使用 SSL。
    """

    REDIS_USE_SENTINEL: Optional[bool] = Field(
        description="是否使用 Redis Sentinel 模式",
        default=False,
    )
    """
    是否使用 Redis Sentinel 模式。默认值为 False，表示不使用 Sentinel 模式。
    """

    REDIS_SENTINELS: Optional[str] = Field(
        description="Redis Sentinel 节点",
        default=None,
    )
    """
    Redis Sentinel 节点的地址。如果使用 Sentinel 模式，此项应包含 Sentinel 节点的地址。
    """

    REDIS_SENTINEL_SERVICE_NAME: Optional[str] = Field(
        description="Redis Sentinel 服务名称",
        default=None,
    )
    """
    Redis Sentinel 服务的名称。如果使用 Sentinel 模式，此项应包含 Sentinel 服务的名称。
    """

    REDIS_SENTINEL_USERNAME: Optional[str] = Field(
        description="Redis Sentinel 用户名",
        default=None,
    )
    """
    Redis Sentinel 的用户名。如果 Sentinel 不需要身份验证，则此项可以为 None。
    """

    REDIS_SENTINEL_PASSWORD: Optional[str] = Field(
        description="Redis Sentinel 密码",
        default=None,
    )
    """
    Redis Sentinel 的密码。如果 Sentinel 不需要身份验证，则此项可以为 None。
    """

    REDIS_SENTINEL_SOCKET_TIMEOUT: Optional[PositiveFloat] = Field(
        description="Redis Sentinel 套接字超时时间",
        default=0.1,
    )
    """
    Redis Sentinel 套接字超时时间。默认值为 0.1 秒，表示在连接 Sentinel 时等待响应的最长时间。
    """

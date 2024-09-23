from typing import Optional

from pydantic import Field, NonNegativeInt, PositiveInt
from pydantic_settings import BaseSettings


class TencentVectorDBConfig(BaseSettings):
    """
    TencentVectorDBConfig 类用于配置与腾讯向量数据库的连接参数。

    主要用途：
    - 提供与腾讯向量数据库连接所需的配置参数。
    - 这些参数包括数据库的 URL、API 密钥、超时时间、用户名、密码、分片数量、副本数量和数据库名称。

    每个属性的详细解释：
    - TENCENT_VECTOR_DB_URL: 用于指定腾讯向量数据库的 URL。默认值为 None，表示未指定 URL。
    - TENCENT_VECTOR_DB_API_KEY: 用于指定连接腾讯向量数据库所需的 API 密钥。默认值为 None，表示未指定 API 密钥。
    - TENCENT_VECTOR_DB_TIMEOUT: 用于指定腾讯向量数据库的超时时间（以秒为单位）。必须为正整数，默认值为 30 秒。
    - TENCENT_VECTOR_DB_USERNAME: 用于指定连接腾讯向量数据库的用户名。默认值为 None，表示未指定用户名。
    - TENCENT_VECTOR_DB_PASSWORD: 用于指定连接腾讯向量数据库的密码。默认值为 None，表示未指定密码。
    - TENCENT_VECTOR_DB_SHARD: 用于指定腾讯向量数据库的分片数量。必须为正整数，默认值为 1。
    - TENCENT_VECTOR_DB_REPLICAS: 用于指定腾讯向量数据库的副本数量。必须为非负整数，默认值为 2。
    - TENCENT_VECTOR_DB_DATABASE: 用于指定要连接的腾讯向量数据库名称。默认值为 None，表示未指定数据库名称。
    """

    TENCENT_VECTOR_DB_URL: Optional[str] = Field(
        description="腾讯向量数据库的 URL。如果未提供，默认为 None。",
        default=None,
    )
    """
    腾讯向量数据库的 URL，类型为可选字符串。
    - 描述: 用于指定腾讯向量数据库的 URL。
    - 默认值: None，表示未指定 URL。
    """

    TENCENT_VECTOR_DB_API_KEY: Optional[str] = Field(
        description="腾讯向量数据库的 API 密钥。如果未提供，默认为 None。",
        default=None,
    )
    """
    腾讯向量数据库的 API 密钥，类型为可选字符串。
    - 描述: 用于指定连接腾讯向量数据库所需的 API 密钥。
    - 默认值: None，表示未指定 API 密钥。
    """

    TENCENT_VECTOR_DB_TIMEOUT: PositiveInt = Field(
        description="腾讯向量数据库的超时时间（以秒为单位）。必须为正整数，默认值为 30 秒。",
        default=30,
    )
    """
    腾讯向量数据库的超时时间，类型为正整数。
    - 描述: 用于指定腾讯向量数据库的超时时间。
    - 默认值: 30，表示客户端在 30 秒后超时。
    """

    TENCENT_VECTOR_DB_USERNAME: Optional[str] = Field(
        description="腾讯向量数据库的用户名。如果未提供，默认为 None。",
        default=None,
    )
    """
    腾讯向量数据库的用户名，类型为可选字符串。
    - 描述: 用于指定连接腾讯向量数据库的用户名。
    - 默认值: None，表示未指定用户名。
    """

    TENCENT_VECTOR_DB_PASSWORD: Optional[str] = Field(
        description="腾讯向量数据库的密码。如果未提供，默认为 None。",
        default=None,
    )
    """
    腾讯向量数据库的密码，类型为可选字符串。
    - 描述: 用于指定连接腾讯向量数据库的密码。
    - 默认值: None，表示未指定密码。
    """

    TENCENT_VECTOR_DB_SHARD: PositiveInt = Field(
        description="腾讯向量数据库的分片数量。必须为正整数，默认值为 1。",
        default=1,
    )
    """
    腾讯向量数据库的分片数量，类型为正整数。
    - 描述: 用于指定腾讯向量数据库的分片数量。
    - 默认值: 1，表示默认分片数量为 1。
    """

    TENCENT_VECTOR_DB_REPLICAS: NonNegativeInt = Field(
        description="腾讯向量数据库的副本数量。必须为非负整数，默认值为 2。",
        default=2,
    )
    """
    腾讯向量数据库的副本数量，类型为非负整数。
    - 描述: 用于指定腾讯向量数据库的副本数量。
    - 默认值: 2，表示默认副本数量为 2。
    """

    TENCENT_VECTOR_DB_DATABASE: Optional[str] = Field(
        description="腾讯向量数据库的名称。如果未提供，默认为 None。",
        default=None,
    )
    """
    腾讯向量数据库的名称，类型为可选字符串。
    - 描述: 用于指定要连接的腾讯向量数据库名称。
    - 默认值: None，表示未指定数据库名称。
    """

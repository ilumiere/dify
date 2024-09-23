from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class OpenSearchConfig(BaseSettings):
    """
    该类用于配置与 OpenSearch 相关的设置。

    主要用途：
    - 提供一个配置类，用于存储和获取与 OpenSearch 连接相关的参数。
    - 这些参数包括 OpenSearch 的主机地址、端口号、用户名、密码以及是否使用 SSL 连接。

    属性说明：
    - OPENSEARCH_HOST: 可选字符串类型，表示 OpenSearch 的主机地址。默认值为 None，表示未指定主机地址。
    - OPENSEARCH_PORT: 正整数类型，表示 OpenSearch 的端口号。默认值为 9200，这是 OpenSearch 的默认端口。
    - OPENSEARCH_USER: 可选字符串类型，表示连接 OpenSearch 所需的用户名。默认值为 None，表示未指定用户名。
    - OPENSEARCH_PASSWORD: 可选字符串类型，表示连接 OpenSearch 所需的密码。默认值为 None，表示未指定密码。
    - OPENSEARCH_SECURE: 布尔类型，表示是否使用 SSL 连接 OpenSearch。默认值为 False，表示不使用 SSL 连接。
    """

    OPENSEARCH_HOST: Optional[str] = Field(
        description="OpenSearch 主机地址",
        default=None,
    )
    """
    OpenSearch 主机地址，类型为可选字符串。
    - 描述: 用于指定 OpenSearch 的主机地址。
    - 默认值: None，表示未指定主机地址。
    """

    OPENSEARCH_PORT: PositiveInt = Field(
        description="OpenSearch 端口号",
        default=9200,
    )
    """
    OpenSearch 端口号，类型为正整数。
    - 描述: 用于指定 OpenSearch 的端口号。
    - 默认值: 9200，表示 OpenSearch 的默认端口。
    """

    OPENSEARCH_USER: Optional[str] = Field(
        description="OpenSearch 用户名",
        default=None,
    )
    """
    OpenSearch 用户名，类型为可选字符串。
    - 描述: 用于指定连接 OpenSearch 的用户名。
    - 默认值: None，表示未指定用户名。
    """

    OPENSEARCH_PASSWORD: Optional[str] = Field(
        description="OpenSearch 密码",
        default=None,
    )
    """
    OpenSearch 密码，类型为可选字符串。
    - 描述: 用于指定连接 OpenSearch 的密码。
    - 默认值: None，表示未指定密码。
    """

    OPENSEARCH_SECURE: bool = Field(
        description="是否使用 SSL 连接 OpenSearch",
        default=False,
    )
    """
    是否使用 SSL 连接 OpenSearch，类型为布尔值。
    - 描述: 用于指定是否使用 SSL 连接 OpenSearch。
    - 默认值: False，表示不使用 SSL 连接。
    """

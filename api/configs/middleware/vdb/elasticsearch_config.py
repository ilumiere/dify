from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class ElasticsearchConfig(BaseSettings):
    """
    该类用于配置与 Elasticsearch 相关的设置。

    主要用途：
    - 提供一个配置类，用于存储和获取与 Elasticsearch 连接相关的参数。
    - 这些参数包括 Elasticsearch 的主机地址、端口号、用户名和密码。

    属性说明：
    - ELASTICSEARCH_HOST: 可选字符串类型，表示 Elasticsearch 的主机地址。默认值为 "127.0.0.1"，即本地主机。
    - ELASTICSEARCH_PORT: 正整数类型，表示 Elasticsearch 的端口号。默认值为 9200，这是 Elasticsearch 的默认端口。
    - ELASTICSEARCH_USERNAME: 可选字符串类型，表示连接 Elasticsearch 所需的用户名。默认值为 "elastic"。
    - ELASTICSEARCH_PASSWORD: 可选字符串类型，表示连接 Elasticsearch 所需的密码。默认值为 "elastic"。
    """

    ELASTICSEARCH_HOST: Optional[str] = Field(
        description="Elasticsearch 主机地址",
        default="127.0.0.1",
    )

    ELASTICSEARCH_PORT: PositiveInt = Field(
        description="Elasticsearch 端口号",
        default=9200,
    )

    ELASTICSEARCH_USERNAME: Optional[str] = Field(
        description="Elasticsearch 用户名",
        default="elastic",
    )

    ELASTICSEARCH_PASSWORD: Optional[str] = Field(
        description="Elasticsearch 密码",
        default="elastic",
    )

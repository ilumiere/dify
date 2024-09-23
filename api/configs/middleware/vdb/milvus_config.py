from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class MilvusConfig(BaseSettings):
    """
    该类用于配置与 Milvus 数据库的连接参数。

    主要用途：
    - 提供与 Milvus 数据库连接所需的配置参数。
    - 这些参数包括 URI、Token、用户名、密码和数据库名称。

    每个属性的详细解释：
    - MILVUS_URI: 用于指定 Milvus 服务的 URI。默认值为 "http://127.0.0.1:19530"。
    - MILVUS_TOKEN: 用于身份验证的 Token。默认值为 None，表示不需要 Token 进行身份验证。
    - MILVUS_USER: 用于身份验证的用户名。默认值为 None，表示不需要用户名进行身份验证。
    - MILVUS_PASSWORD: 用于身份验证的密码。默认值为 None，表示不需要密码进行身份验证。
    - MILVUS_DATABASE: 指定要连接的 Milvus 数据库名称。默认值为 "default"。
    """

    MILVUS_URI: Optional[str] = Field(
        description="Milvus 服务的 URI，用于连接到 Milvus 数据库。",
        default="http://127.0.0.1:19530",
    )

    MILVUS_TOKEN: Optional[str] = Field(
        description="用于身份验证的 Token。如果不需要 Token，则设置为 None。",
        default=None,
    )

    MILVUS_USER: Optional[str] = Field(
        description="用于身份验证的用户名。如果不需要用户名，则设置为 None。",
        default=None,
    )

    MILVUS_PASSWORD: Optional[str] = Field(
        description="用于身份验证的密码。如果不需要密码，则设置为 None。",
        default=None,
    )

    MILVUS_DATABASE: str = Field(
        description="要连接的 Milvus 数据库名称。默认值为 `default`。",
        default="default",
    )

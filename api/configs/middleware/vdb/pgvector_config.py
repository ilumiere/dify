from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class PGVectorConfig(BaseSettings):
    """
    PGVectorConfig 类用于配置与 PGVector 数据库的连接参数。

    主要用途：
    - 提供与 PGVector 数据库连接所需的配置参数。
    - 这些参数包括主机地址、端口号、用户名、密码和数据库名称。

    每个属性的详细解释：
    - PGVECTOR_HOST: 用于指定 PGVector 数据库的主机地址。默认值为 None，表示未指定主机地址。
    - PGVECTOR_PORT: 用于指定 PGVector 数据库的端口号。默认值为 5433，这是 PGVector 数据库的默认端口。
    - PGVECTOR_USER: 用于指定连接 PGVector 数据库的用户名。默认值为 None，表示未指定用户名。
    - PGVECTOR_PASSWORD: 用于指定连接 PGVector 数据库的密码。默认值为 None，表示未指定密码。
    - PGVECTOR_DATABASE: 用于指定要连接的 PGVector 数据库名称。默认值为 None，表示未指定数据库名称。
    """

    PGVECTOR_HOST: Optional[str] = Field(
        description="PGVector 数据库的主机地址。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVector 数据库的主机地址，类型为可选字符串。
    - 描述: 用于指定 PGVector 数据库的主机地址。
    - 默认值: None，表示未指定主机地址。
    """

    PGVECTOR_PORT: Optional[PositiveInt] = Field(
        description="PGVector 数据库的端口号。必须为正整数，默认值为 5433。",
        default=5433,
    )
    """
    PGVector 数据库的端口号，类型为可选正整数。
    - 描述: 用于指定 PGVector 数据库的端口号。
    - 默认值: 5433，表示 PGVector 数据库的默认端口。
    """

    PGVECTOR_USER: Optional[str] = Field(
        description="PGVector 数据库的用户名。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVector 数据库的用户名，类型为可选字符串。
    - 描述: 用于指定连接 PGVector 数据库的用户名。
    - 默认值: None，表示未指定用户名。
    """

    PGVECTOR_PASSWORD: Optional[str] = Field(
        description="PGVector 数据库的密码。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVector 数据库的密码，类型为可选字符串。
    - 描述: 用于指定连接 PGVector 数据库的密码。
    - 默认值: None，表示未指定密码。
    """

    PGVECTOR_DATABASE: Optional[str] = Field(
        description="PGVector 数据库的名称。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVector 数据库的名称，类型为可选字符串。
    - 描述: 用于指定要连接的 PGVector 数据库名称。
    - 默认值: None，表示未指定数据库名称。
    """

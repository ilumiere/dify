from typing import Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class PGVectoRSConfig(BaseSettings):
    """
    PGVectoRSConfig 类用于配置与 PGVectoRS 数据库的连接参数。

    主要用途：
    - 提供与 PGVectoRS 数据库连接所需的配置参数。
    - 这些参数包括主机地址、端口号、用户名、密码和数据库名称。

    每个属性的详细解释：
    - PGVECTO_RS_HOST: 用于指定 PGVectoRS 数据库的主机地址。默认值为 None，表示未指定主机地址。
    - PGVECTO_RS_PORT: 用于指定 PGVectoRS 数据库的端口号。默认值为 5431，这是 PGVectoRS 数据库的默认端口。
    - PGVECTO_RS_USER: 用于指定连接 PGVectoRS 数据库的用户名。默认值为 None，表示未指定用户名。
    - PGVECTO_RS_PASSWORD: 用于指定连接 PGVectoRS 数据库的密码。默认值为 None，表示未指定密码。
    - PGVECTO_RS_DATABASE: 用于指定要连接的 PGVectoRS 数据库名称。默认值为 None，表示未指定数据库名称。
    """

    PGVECTO_RS_HOST: Optional[str] = Field(
        description="PGVectoRS 数据库的主机地址。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVectoRS 数据库的主机地址，类型为可选字符串。
    - 描述: 用于指定 PGVectoRS 数据库的主机地址。
    - 默认值: None，表示未指定主机地址。
    """

    PGVECTO_RS_PORT: Optional[PositiveInt] = Field(
        description="PGVectoRS 数据库的端口号。必须为正整数，默认值为 5431。",
        default=5431,
    )
    """
    PGVectoRS 数据库的端口号，类型为可选正整数。
    - 描述: 用于指定 PGVectoRS 数据库的端口号。
    - 默认值: 5431，表示 PGVectoRS 数据库的默认端口。
    """

    PGVECTO_RS_USER: Optional[str] = Field(
        description="PGVectoRS 数据库的用户名。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVectoRS 数据库的用户名，类型为可选字符串。
    - 描述: 用于指定连接 PGVectoRS 数据库的用户名。
    - 默认值: None，表示未指定用户名。
    """

    PGVECTO_RS_PASSWORD: Optional[str] = Field(
        description="PGVectoRS 数据库的密码。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVectoRS 数据库的密码，类型为可选字符串。
    - 描述: 用于指定连接 PGVectoRS 数据库的密码。
    - 默认值: None，表示未指定密码。
    """

    PGVECTO_RS_DATABASE: Optional[str] = Field(
        description="PGVectoRS 数据库的名称。如果未提供，默认为 None。",
        default=None,
    )
    """
    PGVectoRS 数据库的名称，类型为可选字符串。
    - 描述: 用于指定要连接的 PGVectoRS 数据库名称。
    - 默认值: None，表示未指定数据库名称。
    """

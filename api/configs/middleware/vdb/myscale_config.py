from pydantic import BaseModel, Field, PositiveInt


class MyScaleConfig(BaseModel):
    """
    MyScaleConfig 类用于定义与 MyScale 数据库相关的配置参数。
    该类继承自 BaseModel，使用 Pydantic 的 Field 来定义每个配置项的类型、描述和默认值。
    这些配置项用于连接和配置 MyScale 数据库的各个方面，包括主机、端口、用户名、密码、数据库名称和全文搜索参数。
    """

    MYSCALE_HOST: str = Field(
        description="MyScale 数据库的主机地址。默认值为 'localhost'，表示数据库运行在本地主机上。",
        default="localhost",
    )
    """
    MyScale 数据库的主机地址，类型为字符串。
    - 描述: 用于指定 MyScale 数据库的主机地址。
    - 默认值: 'localhost'，表示数据库运行在本地主机上。
    """

    MYSCALE_PORT: PositiveInt = Field(
        description="MyScale 数据库的端口号。必须为正整数，默认值为 8123。",
        default=8123,
    )
    """
    MyScale 数据库的端口号，类型为正整数。
    - 描述: 用于指定 MyScale 数据库的端口号。
    - 默认值: 8123，表示数据库的默认端口号。
    """

    MYSCALE_USER: str = Field(
        description="MyScale 数据库的用户名。默认值为 'default'，表示使用默认用户名。",
        default="default",
    )
    """
    MyScale 数据库的用户名，类型为字符串。
    - 描述: 用于指定连接 MyScale 数据库的用户名。
    - 默认值: 'default'，表示使用默认用户名。
    """

    MYSCALE_PASSWORD: str = Field(
        description="MyScale 数据库的密码。默认值为空字符串，表示不需要密码进行身份验证。",
        default="",
    )
    """
    MyScale 数据库的密码，类型为字符串。
    - 描述: 用于指定连接 MyScale 数据库的密码。
    - 默认值: ''，表示不需要密码进行身份验证。
    """

    MYSCALE_DATABASE: str = Field(
        description="MyScale 数据库的名称。默认值为 'default'，表示使用默认数据库。",
        default="default",
    )
    """
    MyScale 数据库的名称，类型为字符串。
    - 描述: 用于指定要连接的 MyScale 数据库的名称。
    - 默认值: 'default'，表示使用默认数据库。
    """

    MYSCALE_FTS_PARAMS: str = Field(
        description="MyScale 数据库的全文搜索索引参数。默认值为空字符串，表示不使用任何参数。",
        default="",
    )
    """
    MyScale 数据库的全文搜索索引参数，类型为字符串。
    - 描述: 用于指定 MyScale 数据库的全文搜索索引参数。
    - 默认值: ''，表示不使用任何参数。
    """

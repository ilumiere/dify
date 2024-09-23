from typing import Optional

from pydantic import BaseModel, Field


class AnalyticdbConfig(BaseModel):
    """
    用于连接 AnalyticDB 的配置类。

    该类定义了与 AnalyticDB 连接相关的配置参数。这些参数包括访问密钥 ID、密钥、区域 ID、实例 ID、账户名、密码、命名空间及其密码。
    通过这些配置，可以与 AnalyticDB 进行交互，执行数据库操作。

    参考以下文档获取凭据的详细信息：
    https://www.alibabacloud.com/help/en/analyticdb-for-postgresql/getting-started/create-an-instance-instances-with-vector-engine-optimization-enabled
    """

    ANALYTICDB_KEY_ID: Optional[str] = Field(
        default=None, description="阿里云提供的用于身份验证的访问密钥 ID。"
    )
    """
    访问密钥 ID，类型为可选字符串。
    - 描述: 用于身份验证的访问密钥 ID。
    - 默认值: None，表示未指定访问密钥 ID。
    """

    ANALYTICDB_KEY_SECRET: Optional[str] = Field(
        default=None, description="与访问密钥 ID 对应的用于安全访问的秘密访问密钥。"
    )
    """
    秘密访问密钥，类型为可选字符串。
    - 描述: 用于安全访问的秘密访问密钥。
    - 默认值: None，表示未指定秘密访问密钥。
    """

    ANALYTICDB_REGION_ID: Optional[str] = Field(
        default=None, description="AnalyticDB 实例部署的区域（例如，'cn-hangzhou'）。"
    )
    """
    区域 ID，类型为可选字符串。
    - 描述: AnalyticDB 实例部署的区域。
    - 默认值: None，表示未指定区域。
    """

    ANALYTICDB_INSTANCE_ID: Optional[str] = Field(
        default=None,
        description="要连接的 AnalyticDB 实例的唯一标识符（例如，'gp-ab123456'）。",
    )
    """
    实例 ID，类型为可选字符串。
    - 描述: 要连接的 AnalyticDB 实例的唯一标识符。
    - 默认值: None，表示未指定实例 ID。
    """

    ANALYTICDB_ACCOUNT: Optional[str] = Field(
        default=None, description="用于登录 AnalyticDB 实例的账户名。"
    )
    """
    账户名，类型为可选字符串。
    - 描述: 用于登录 AnalyticDB 实例的账户名。
    - 默认值: None，表示未指定账户名。
    """

    ANALYTICDB_PASSWORD: Optional[str] = Field(
        default=None, description="与 AnalyticDB 账户关联的用于身份验证的密码。"
    )
    """
    密码，类型为可选字符串。
    - 描述: 与 AnalyticDB 账户关联的用于身份验证的密码。
    - 默认值: None，表示未指定密码。
    """

    ANALYTICDB_NAMESPACE: Optional[str] = Field(
        default=None, description="AnalyticDB 中的命名空间，用于模式隔离。"
    )
    """
    命名空间，类型为可选字符串。
    - 描述: AnalyticDB 中的命名空间，用于模式隔离。
    - 默认值: None，表示未指定命名空间。
    """

    ANALYTICDB_NAMESPACE_PASSWORD: Optional[str] = Field(
        default=None, description="用于访问 AnalyticDB 实例中指定命名空间的密码。"
    )
    """
    命名空间密码，类型为可选字符串。
    - 描述: 用于访问 AnalyticDB 实例中指定命名空间的密码。
    - 默认值: None，表示未指定命名空间密码。
    """

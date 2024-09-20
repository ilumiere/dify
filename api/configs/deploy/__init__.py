from pydantic import Field
from pydantic_settings import BaseSettings


class DeploymentConfig(BaseSettings):
    """
    部署配置类，用于定义和管理应用程序的部署相关配置。

    该类继承自 `BaseSettings`，使用 `pydantic` 库来确保配置项的类型安全和验证。
    每个配置项都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 定义应用程序的名称。
    - 控制调试模式的启用。
    - 设置测试模式。
    - 指定部署版本。
    - 定义部署环境。
    """

    APPLICATION_NAME: str = Field(
        description="应用程序的名称。",
        default="langgenius/dify",
    )
    """
    应用程序的名称。
    默认值为 "langgenius/dify"。
    """

    DEBUG: bool = Field(
        description="是否启用调试模式。",
        default=False,
    )
    """
    是否启用调试模式。
    默认值为 False，表示不启用调试模式。
    """

    TESTING: bool = Field(
        description="是否启用测试模式。",
        default=False,
    )
    """
    是否启用测试模式。
    默认值为 False，表示不启用测试模式。
    """

    EDITION: str = Field(
        description="部署版本。",
        default="SELF_HOSTED",
    )
    """
    部署版本。
    默认值为 "SELF_HOSTED"，表示自托管版本。
    """

    DEPLOY_ENV: str = Field(
        description="部署环境，默认为生产环境。",
        default="PRODUCTION",
    )
    """
    部署环境。
    默认值为 "PRODUCTION"，表示生产环境。
    """

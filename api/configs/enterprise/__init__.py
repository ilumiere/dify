from pydantic import Field
from pydantic_settings import BaseSettings


class EnterpriseFeatureConfig(BaseSettings):
    """
    企业功能配置类，用于定义和管理企业级功能的相关配置。

    该类继承自 `BaseSettings`，使用 `pydantic` 库来确保配置项的类型安全和验证。
    每个配置项都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 控制企业级功能的启用。
    - 控制是否允许替换企业标志。

    **在使用之前，请通过电子邮件联系 business@dify.ai 以了解许可事宜。**
    """

    # TODO 企业开关
    ENTERPRISE_ENABLED: bool = Field(
        description="是否启用企业级功能。"
        "在使用之前，请通过电子邮件联系 business@dify.ai 以了解许可事宜。",
        default=False,
    )
    """
    是否启用企业级功能。
    默认值为 False，表示不启用企业级功能。
    """

    CAN_REPLACE_LOGO: bool = Field(
        description="是否允许替换企业标志。",
        default=False,
    )
    """
    是否允许替换企业标志。
    默认值为 False，表示不允许替换企业标志。
    """

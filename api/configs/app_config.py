from pydantic_settings import SettingsConfigDict

from configs.deploy import DeploymentConfig
from configs.enterprise import EnterpriseFeatureConfig
from configs.extra import ExtraServiceConfig
from configs.feature import FeatureConfig
from configs.middleware import MiddlewareConfig
from configs.packaging import PackagingInfo


class DifyConfig(
    # 打包信息
    PackagingInfo,
    # 部署配置
    DeploymentConfig,
    # 功能配置
    FeatureConfig,
    # 中间件配置
    MiddlewareConfig,
    # 额外服务配置
    ExtraServiceConfig,
    # 企业功能配置
    # **在使用之前，请通过电子邮件联系 business@dify.ai 以了解许可事宜。**
    EnterpriseFeatureConfig,
):
    """
    DifyConfig 类用于定义和管理应用程序的配置。

    该类继承了多个配置类，包括打包信息、部署配置、功能配置、中间件配置、额外服务配置和企业功能配置。
    通过这种方式，DifyConfig 类能够集中管理应用程序的所有配置项，确保配置的一致性和可维护性。

    主要用途：
    - 管理应用程序的打包信息。
    - 控制应用程序的部署配置。
    - 配置应用程序的功能。
    - 管理应用程序的中间件。
    - 配置额外的服务。
    - 管理企业功能配置。
    """

    model_config = SettingsConfigDict(
        # 从 dotenv 格式的配置文件中读取配置
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        # 忽略额外的属性
        extra="ignore",
    )
    """
    model_config 属性用于配置 Pydantic 的设置。

    - env_file: 指定从 .env 文件中读取配置。
    - env_file_encoding: 指定 .env 文件的编码格式为 UTF-8。
    - frozen: 设置为 True，表示配置对象是不可变的。
    - extra: 设置为 "ignore"，表示忽略未知的额外属性。
    """

    # 在添加任何配置之前，
    # 请考虑将其安排在现有或添加的适当配置组中，
    # 以提高可读性和可维护性。
    # 感谢您的专注和考虑。

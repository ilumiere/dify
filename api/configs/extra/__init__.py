from configs.extra.notion_config import NotionConfig
from configs.extra.sentry_config import SentryConfig


class ExtraServiceConfig(
    # 按照字母顺序排列配置
    NotionConfig,
    SentryConfig,
):
    """
    ExtraServiceConfig 类用于组合多个外部服务的配置。
    
    主要用途：
    - 该类继承了 NotionConfig 和 SentryConfig，用于管理与 Notion 和 Sentry 相关的配置。
    - 通过继承这些配置类，ExtraServiceConfig 可以统一管理多个外部服务的配置信息。
    
    属性解释：
    - NotionConfig: 用于配置与 Notion API 相关的设置，例如 API 密钥、数据库 ID 等。
    - SentryConfig: 用于配置与 Sentry 错误监控服务相关的设置，例如 DSN、环境变量等。
    
    该类目前没有定义任何方法或属性，仅用于组合和继承其他配置类。
    """
    pass


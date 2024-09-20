from typing import Optional

from pydantic import Field, NonNegativeFloat
from pydantic_settings import BaseSettings


class SentryConfig(BaseSettings):
    """
    Sentry 配置类，用于定义和管理与 Sentry 集成的相关配置。

    该类继承自 `BaseSettings`，使用 `pydantic` 库来确保配置项的类型安全和验证。
    每个配置项都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 存储 Sentry DSN（数据源名称）。
    - 设置 Sentry 跟踪采样率。
    - 设置 Sentry 配置文件采样率。
    """

    SENTRY_DSN: Optional[str] = Field(
        description="Sentry DSN（数据源名称），用于标识 Sentry 项目。",
        default=None,
    )
    """
    Sentry DSN（数据源名称）。
    默认值为 None，表示未设置 Sentry DSN。
    """

    SENTRY_TRACES_SAMPLE_RATE: NonNegativeFloat = Field(
        description="Sentry 跟踪采样率，用于控制跟踪事件的采样频率。",
        default=1.0,
    )
    """
    Sentry 跟踪采样率。
    默认值为 1.0，表示采样所有跟踪事件。
    """

    SENTRY_PROFILES_SAMPLE_RATE: NonNegativeFloat = Field(
        description="Sentry 配置文件采样率，用于控制配置文件事件的采样频率。",
        default=1.0,
    )
    """
    Sentry 配置文件采样率。
    默认值为 1.0，表示采样所有配置文件事件。
    """

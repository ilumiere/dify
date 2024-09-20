from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class NotionConfig(BaseSettings):
    """
    Notion 集成配置类，用于定义和管理与 Notion 集成的相关配置。

    该类继承自 `BaseSettings`，使用 `pydantic` 库来确保配置项的类型安全和验证。
    每个配置项都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 存储 Notion 客户端 ID。
    - 存储 Notion 客户端密钥。
    - 存储 Notion 集成类型。
    - 存储 Notion 内部密钥。
    - 存储 Notion 集成令牌。
    """

    NOTION_CLIENT_ID: Optional[str] = Field(
        description="Notion 客户端 ID，用于标识 Notion 客户端应用程序。",
        default=None,
    )
    """
    Notion 客户端 ID。
    默认值为 None，表示未设置 Notion 客户端 ID。
    """

    NOTION_CLIENT_SECRET: Optional[str] = Field(
        description="Notion 客户端密钥，用于验证 Notion 客户端应用程序的身份。",
        default=None,
    )
    """
    Notion 客户端密钥。
    默认值为 None，表示未设置 Notion 客户端密钥。
    """

    NOTION_INTEGRATION_TYPE: Optional[str] = Field(
        description="Notion 集成类型，默认值为 None，可用值为 'internal'。",
        default=None,
    )
    """
    Notion 集成类型。
    默认值为 None，表示未设置 Notion 集成类型。
    可用值为 'internal'，表示内部集成。
    """

    NOTION_INTERNAL_SECRET: Optional[str] = Field(
        description="Notion 内部密钥，用于内部集成时的身份验证。",
        default=None,
    )
    """
    Notion 内部密钥。
    默认值为 None，表示未设置 Notion 内部密钥。
    """

    NOTION_INTEGRATION_TOKEN: Optional[str] = Field(
        description="Notion 集成令牌，用于访问 Notion API 的授权令牌。",
        default=None,
    )
    """
    Notion 集成令牌。
    默认值为 None，表示未设置 Notion 集成令牌。
    """

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AzureBlobStorageConfig(BaseSettings):
    """
    Azure Blob 存储配置类

    该类用于定义与 Azure Blob 存储相关的配置参数。这些参数包括账户名称、账户密钥、容器名称和账户 URL。
    这些配置参数将用于连接和操作 Azure Blob 存储服务。
    """

    AZURE_BLOB_ACCOUNT_NAME: Optional[str] = Field(
        description="Azure Blob 账户名称",
        default=None,
    )
    """
    Azure Blob 账户名称

    该属性用于存储 Azure Blob 存储账户的名称。账户名称是连接到 Azure Blob 存储服务的必要参数之一。
    默认值为 None，表示该参数是可选的。
    """

    AZURE_BLOB_ACCOUNT_KEY: Optional[str] = Field(
        description="Azure Blob 账户密钥",
        default=None,
    )
    """
    Azure Blob 账户密钥

    该属性用于存储 Azure Blob 存储账户的密钥。账户密钥是用于身份验证和访问 Azure Blob 存储服务的关键参数。
    默认值为 None，表示该参数是可选的。
    """

    AZURE_BLOB_CONTAINER_NAME: Optional[str] = Field(
        description="Azure Blob 容器名称",
        default=None,
    )
    """
    Azure Blob 容器名称

    该属性用于存储 Azure Blob 存储容器名称。容器名称是用于组织和管理存储在 Azure Blob 存储中的数据的关键参数。
    默认值为 None，表示该参数是可选的。
    """

    AZURE_BLOB_ACCOUNT_URL: Optional[str] = Field(
        description="Azure Blob 账户 URL",
        default=None,
    )
    """
    Azure Blob 账户 URL

    该属性用于存储 Azure Blob 存储账户的 URL。账户 URL 是用于访问 Azure Blob 存储服务的完整路径。
    默认值为 None，表示该参数是可选的。
    """

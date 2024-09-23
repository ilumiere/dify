from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

class GoogleCloudStorageConfig(BaseSettings):
    """
    GoogleCloudStorageConfig 类用于定义与 Google Cloud 存储相关的配置参数。
    这些配置参数包括存储桶名称和服务账户 JSON 的 Base64 编码。
    每个配置参数都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 定义 Google Cloud 存储桶的名称。
    - 配置访问 Google Cloud 存储所需的服务账户 JSON 的 Base64 编码。
    """

    GOOGLE_STORAGE_BUCKET_NAME: Optional[str] = Field(
        description="Google Cloud 存储桶的名称。",
        default=None,
    )
    """
    Google Cloud 存储桶的名称。如果未提供，则默认为 None。
    """

    GOOGLE_STORAGE_SERVICE_ACCOUNT_JSON_BASE64: Optional[str] = Field(
        description="Google Cloud 存储服务账户 JSON 的 Base64 编码。",
        default=None,
    )
    """
    Google Cloud 存储服务账户 JSON 的 Base64 编码。用于身份验证。如果未提供，则默认为 None。
    """

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class OCIStorageConfig(BaseSettings):
    """
    OCIStorageConfig 类用于定义与 Oracle Cloud Infrastructure (OCI) 存储相关的配置参数。
    这些配置参数包括存储服务的端点、区域、存储桶名称、访问密钥和秘密密钥。
    每个配置参数都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 定义 OCI 存储服务的端点 URL。
    - 配置 OCI 存储服务的区域。
    - 指定 OCI 存储桶的名称。
    - 配置访问 OCI 存储所需的访问密钥和秘密密钥。
    """

    OCI_ENDPOINT: Optional[str] = Field(
        description="OCI 存储服务的端点 URL。用户可以指定自定义的 OCI 端点，用于连接到 OCI 存储服务。",
        default=None,
    )
    """
    OCI 存储服务的端点 URL。如果未提供，则默认为 None。
    """

    OCI_REGION: Optional[str] = Field(
        description="OCI 存储服务的区域。指定存储桶所在的 OCI 区域，例如 'us-ashburn-1'。",
        default=None,
    )
    """
    OCI 存储服务的区域。如果未提供，则默认为 None。
    """

    OCI_BUCKET_NAME: Optional[str] = Field(
        description="OCI 存储桶的名称。指定用于存储对象的存储桶名称。",
        default=None,
    )
    """
    OCI 存储桶的名称。如果未提供，则默认为 None。
    """

    OCI_ACCESS_KEY: Optional[str] = Field(
        description="OCI 存储服务的访问密钥。用于身份验证的访问密钥 ID。",
        default=None,
    )
    """
    OCI 存储服务的访问密钥。如果未提供，则默认为 None。
    """

    OCI_SECRET_KEY: Optional[str] = Field(
        description="OCI 存储服务的秘密密钥。用于身份验证的秘密访问密钥。",
        default=None,
    )
    """
    OCI 存储服务的秘密密钥。如果未提供，则默认为 None。
    """

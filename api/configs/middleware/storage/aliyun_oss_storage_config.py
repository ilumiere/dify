from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AliyunOSSStorageConfig(BaseSettings):
    """
    AliyunOSSStorageConfig 类用于定义与阿里云 OSS 存储相关的配置参数。
    这些配置参数包括 OSS 存储桶名称、访问密钥、秘密密钥、端点 URL、区域、认证版本和存储路径。
    每个配置参数都通过 `Field` 进行详细描述，并提供默认值。

    主要用途：
    - 定义阿里云 OSS 存储桶的名称。
    - 配置访问阿里云 OSS 所需的访问密钥和秘密密钥。
    - 指定阿里云 OSS 的端点 URL 和区域。
    - 设置阿里云 OSS 的认证版本和存储路径。
    """

    ALIYUN_OSS_BUCKET_NAME: Optional[str] = Field(
        description="阿里云 OSS 存储桶的名称。",
        default=None,
    )
    """
    阿里云 OSS 存储桶的名称。如果未提供，则默认为 None。
    """

    ALIYUN_OSS_ACCESS_KEY: Optional[str] = Field(
        description="阿里云 OSS 的访问密钥。",
        default=None,
    )
    """
    阿里云 OSS 的访问密钥。用于身份验证。如果未提供，则默认为 None。
    """

    ALIYUN_OSS_SECRET_KEY: Optional[str] = Field(
        description="阿里云 OSS 的秘密密钥。",
        default=None,
    )
    """
    阿里云 OSS 的秘密密钥。用于身份验证。如果未提供，则默认为 None。
    """

    ALIYUN_OSS_ENDPOINT: Optional[str] = Field(
        description="阿里云 OSS 的端点 URL。",
        default=None,
    )
    """
    阿里云 OSS 的端点 URL。用于连接到 OSS 服务。如果未提供，则默认为 None。
    """

    ALIYUN_OSS_REGION: Optional[str] = Field(
        description="阿里云 OSS 的区域。",
        default=None,
    )
    """
    阿里云 OSS 的区域。用于指定 OSS 服务的地理位置。如果未提供，则默认为 None。
    """

    ALIYUN_OSS_AUTH_VERSION: Optional[str] = Field(
        description="阿里云 OSS 的认证版本。",
        default=None,
    )
    """
    阿里云 OSS 的认证版本。用于指定使用的认证协议。如果未提供，则默认为 None。
    """

    ALIYUN_OSS_PATH: Optional[str] = Field(
        description="阿里云 OSS 的存储路径。",
        default=None,
    )
    """
    阿里云 OSS 的存储路径。用于指定存储对象的路径。如果未提供，则默认为 None。
    """

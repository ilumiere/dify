from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class S3StorageConfig(BaseSettings):
    """
    S3StorageConfig 类用于配置与 Amazon S3 存储相关的设置。
    该类继承自 BaseSettings，使用 Pydantic 的 Field 来定义每个配置项的类型、描述和默认值。
    每个配置项都是可选的，允许用户根据需要提供或忽略某些配置。
    """

    S3_ENDPOINT: Optional[str] = Field(
        description="S3 存储服务的端点 URL。用户可以指定自定义的 S3 端点，例如使用 MinIO 或其他兼容 S3 的服务。",
        default=None,
    )

    S3_REGION: Optional[str] = Field(
        description="S3 存储服务的区域。指定存储桶所在的 AWS 区域，例如 'us-west-2'。",
        default=None,
    )

    S3_BUCKET_NAME: Optional[str] = Field(
        description="S3 存储桶的名称。指定用于存储对象的存储桶名称。",
        default=None,
    )

    S3_ACCESS_KEY: Optional[str] = Field(
        description="S3 存储服务的访问密钥。用于身份验证的访问密钥 ID。",
        default=None,
    )

    S3_SECRET_KEY: Optional[str] = Field(
        description="S3 存储服务的秘密密钥。用于身份验证的秘密访问密钥。",
        default=None,
    )

    S3_ADDRESS_STYLE: str = Field(
        description="S3 存储服务的地址样式。指定使用 'path-style' 或 'virtual-hosted-style' 地址。默认值为 'auto'，表示自动选择。",
        default="auto",
    )

    S3_USE_AWS_MANAGED_IAM: bool = Field(
        description="是否使用 AWS 管理的 IAM 角色进行 S3 访问。如果设置为 True，将使用 AWS 管理的 IAM 角色进行身份验证。",
        default=False,
    )

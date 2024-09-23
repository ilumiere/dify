from typing import Optional

from pydantic import BaseModel, Field


class HuaweiCloudOBSStorageConfig(BaseModel):
    """
    华为云 OBS 存储配置类

    该类用于定义与华为云对象存储服务（OBS）相关的配置参数。这些参数包括存储桶名称、访问密钥、秘密密钥和服务器URL。
    通过这些配置，可以连接到华为云的OBS服务并进行文件的上传、下载等操作。
    """

    HUAWEI_OBS_BUCKET_NAME: Optional[str] = Field(
        description="华为云 OBS 存储桶名称。存储桶是用于存储对象的容器。",
        default=None,
    )
    """
    华为云 OBS 存储桶名称。存储桶是用于存储对象的容器。
    """

    HUAWEI_OBS_ACCESS_KEY: Optional[str] = Field(
        description="华为云 OBS 访问密钥。访问密钥用于身份验证，允许访问存储桶中的资源。",
        default=None,
    )
    """
    华为云 OBS 访问密钥。访问密钥用于身份验证，允许访问存储桶中的资源。
    """

    HUAWEI_OBS_SECRET_KEY: Optional[str] = Field(
        description="华为云 OBS 秘密密钥。秘密密钥与访问密钥一起用于身份验证。",
        default=None,
    )
    """
    华为云 OBS 秘密密钥。秘密密钥与访问密钥一起用于身份验证。
    """

    HUAWEI_OBS_SERVER: Optional[str] = Field(
        description="华为云 OBS 服务器URL。该URL用于指定OBS服务的访问地址。",
        default=None,
    )
    """
    华为云 OBS 服务器URL。该URL用于指定OBS服务的访问地址。
    """

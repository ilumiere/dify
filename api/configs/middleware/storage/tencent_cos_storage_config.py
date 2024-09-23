from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class TencentCloudCOSStorageConfig(BaseSettings):
    """
    腾讯云COS存储配置类

    该类用于定义与腾讯云COS（Cloud Object Storage）相关的配置参数。这些参数包括存储桶名称、区域、密钥ID、密钥和协议方案。
    通过这些配置，可以与腾讯云COS进行交互，执行文件上传、下载等操作。
    """

    TENCENT_COS_BUCKET_NAME: Optional[str] = Field(
        description="腾讯云COS存储桶名称",
        default=None,
    )
    """
    腾讯云COS存储桶名称

    该属性用于指定腾讯云COS存储桶的名称。存储桶是存储对象的容器，每个对象都存储在一个特定的存储桶中。
    默认值为None，表示未指定存储桶名称。
    """

    TENCENT_COS_REGION: Optional[str] = Field(
        description="腾讯云COS区域",
        default=None,
    )
    """
    腾讯云COS区域

    该属性用于指定腾讯云COS服务的区域。不同的区域可能有不同的服务可用性和性能特征。
    默认值为None，表示未指定区域。
    """

    TENCENT_COS_SECRET_ID: Optional[str] = Field(
        description="腾讯云COS密钥ID",
        default=None,
    )
    """
    腾讯云COS密钥ID

    该属性用于指定腾讯云COS的密钥ID。密钥ID是访问腾讯云COS服务的身份凭证之一。
    默认值为None，表示未指定密钥ID。
    """

    TENCENT_COS_SECRET_KEY: Optional[str] = Field(
        description="腾讯云COS密钥",
        default=None,
    )
    """
    腾讯云COS密钥

    该属性用于指定腾讯云COS的密钥。密钥是访问腾讯云COS服务的身份凭证之一。
    默认值为None，表示未指定密钥。
    """

    TENCENT_COS_SCHEME: Optional[str] = Field(
        description="腾讯云COS协议方案",
        default=None,
    )
    """
    腾讯云COS协议方案

    该属性用于指定腾讯云COS的协议方案，例如HTTP或HTTPS。协议方案决定了与COS服务通信时使用的协议。
    默认值为None，表示未指定协议方案。
    """

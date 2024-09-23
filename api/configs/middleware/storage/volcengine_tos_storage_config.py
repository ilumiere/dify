from typing import Optional

from pydantic import BaseModel, Field


class VolcengineTOSStorageConfig(BaseModel):
    """
    该类用于配置Volcengine TOS存储服务的相关参数。

    主要用途：
    - 提供一个结构化的方式来存储和管理Volcengine TOS存储服务的配置信息。
    - 通过Pydantic的BaseModel来确保配置项的类型安全和默认值管理。

    属性说明：
    - VOLCENGINE_TOS_BUCKET_NAME: 存储桶名称，用于标识存储数据的容器。
    - VOLCENGINE_TOS_ACCESS_KEY: 访问密钥，用于身份验证和访问控制。
    - VOLCENGINE_TOS_SECRET_KEY: 密钥，用于加密和解密数据。
    - VOLCENGINE_TOS_ENDPOINT: 端点URL，用于指定Volcengine TOS服务的访问地址。
    - VOLCENGINE_TOS_REGION: 区域，用于指定Volcengine TOS服务的地理位置。
    """

    VOLCENGINE_TOS_BUCKET_NAME: Optional[str] = Field(
        description="Volcengine TOS Bucket Name",
        default=None,
    )
    """
    存储桶名称，类型为可选字符串。
    - 描述: 用于标识存储数据的容器。
    - 默认值: None，表示未指定存储桶名称。
    """

    VOLCENGINE_TOS_ACCESS_KEY: Optional[str] = Field(
        description="Volcengine TOS Access Key",
        default=None,
    )
    """
    访问密钥，类型为可选字符串。
    - 描述: 用于身份验证和访问控制。
    - 默认值: None，表示未指定访问密钥。
    """

    VOLCENGINE_TOS_SECRET_KEY: Optional[str] = Field(
        description="Volcengine TOS Secret Key",
        default=None,
    )
    """
    密钥，类型为可选字符串。
    - 描述: 用于加密和解密数据。
    - 默认值: None，表示未指定密钥。
    """

    VOLCENGINE_TOS_ENDPOINT: Optional[str] = Field(
        description="Volcengine TOS Endpoint URL",
        default=None,
    )
    """
    端点URL，类型为可选字符串。
    - 描述: 用于指定Volcengine TOS服务的访问地址。
    - 默认值: None，表示未指定端点URL。
    """

    VOLCENGINE_TOS_REGION: Optional[str] = Field(
        description="Volcengine TOS Region",
        default=None,
    )
    """
    区域，类型为可选字符串。
    - 描述: 用于指定Volcengine TOS服务的地理位置。
    - 默认值: None，表示未指定区域。
    """

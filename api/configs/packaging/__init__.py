from pydantic import Field
from pydantic_settings import BaseSettings


class PackagingInfo(BaseSettings):
    """
    PackagingInfo 类用于存储和配置打包构建信息。

    主要用途和功能：
    - 提供当前 Dify 应用的版本号和构建时使用的 Git 提交的 SHA-1 校验和。
    - 使用 Pydantic 的 Field 来定义每个配置项的类型、描述和默认值。

    属性详细解释：
    - CURRENT_VERSION: 字符串类型，表示当前 Dify 应用的版本号。默认值为 "0.8.2"。
    - COMMIT_SHA: 字符串类型，表示用于构建应用的 Git 提交的 SHA-1 校验和。默认值为空字符串。
    """

    CURRENT_VERSION: str = Field(
        description="当前 Dify 应用的版本号",
        default="0.8.2",
    )
    """
    CURRENT_VERSION 属性用于指定当前 Dify 应用的版本号。
    - 类型为字符串。
    - 描述: 用于指定当前 Dify 应用的版本号。
    - 默认值: "0.8.2"，表示当前版本为 0.8.2。
    """

    COMMIT_SHA: str = Field(
        description="用于构建应用的 Git 提交的 SHA-1 校验和",
        default="",
    )
    """
    COMMIT_SHA 属性用于指定用于构建应用的 Git 提交的 SHA-1 校验和。
    - 类型为字符串。
    - 描述: 用于指定用于构建应用的 Git 提交的 SHA-1 校验和。
    - 默认值: 空字符串，表示未指定校验和。
    """

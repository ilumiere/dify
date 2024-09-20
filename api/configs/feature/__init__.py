from typing import Annotated, Optional

from pydantic import AliasChoices, Field, HttpUrl, NegativeInt, NonNegativeInt, PositiveInt, computed_field
from pydantic_settings import BaseSettings

from configs.feature.hosted_service import HostedServiceConfig


class SecurityConfig(BaseSettings):
    """
    安全配置类，用于管理应用程序的安全密钥和重置密码令牌的过期时间。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    SECRET_KEY: Optional[str] = Field(
        description="应用程序的密钥，用于安全地签名会话 cookie。"
        "确保在部署时更改此密钥为强密钥。"
        "可以使用 `openssl rand -base64 42` 生成强密钥。"
        "或者通过 `SECRET_KEY` 环境变量设置。",
        default=None,
    )
    """
    SECRET_KEY 属性：
    - 类型：Optional[str]
    - 描述：应用程序的密钥，用于安全地签名会话 cookie。
    - 默认值：None
    - 说明：确保在部署时更改此密钥为强密钥，可以使用 `openssl rand -base64 42` 生成强密钥，或者通过 `SECRET_KEY` 环境变量设置。
    """

    RESET_PASSWORD_TOKEN_EXPIRY_HOURS: PositiveInt = Field(
        description="重置密码令牌的过期时间，单位为小时。",
        default=24,
    )
    """
    RESET_PASSWORD_TOKEN_EXPIRY_HOURS 属性：
    - 类型：PositiveInt
    - 描述：重置密码令牌的过期时间，单位为小时。
    - 默认值：24
    - 说明：重置密码令牌的过期时间，单位为小时，默认值为 24 小时。
    """


class AppExecutionConfig(BaseSettings):
    """
    App Execution 配置类，用于管理应用程序执行的相关配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    APP_MAX_EXECUTION_TIME: PositiveInt = Field(
        description="应用程序执行的超时时间，单位为秒。",
        default=1200,
    )
    """
    APP_MAX_EXECUTION_TIME 属性：
    - 类型：PositiveInt
    - 描述：应用程序执行的超时时间，单位为秒。
    - 默认值：1200
    - 说明：应用程序执行的超时时间，单位为秒，默认值为 1200 秒（20 分钟）。
    """

    APP_MAX_ACTIVE_REQUESTS: NonNegativeInt = Field(
        description="每个应用程序的最大活跃请求数，0 表示无限制。",
        default=0,
    )
    """
    APP_MAX_ACTIVE_REQUESTS 属性：
    - 类型：NonNegativeInt
    - 描述：每个应用程序的最大活跃请求数，0 表示无限制。
    - 默认值：0
    - 说明：每个应用程序的最大活跃请求数，0 表示无限制，默认值为 0。
    """


class CodeExecutionSandboxConfig(BaseSettings):
    """
    Code Execution Sandbox 配置类，用于管理代码执行沙箱的相关配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    CODE_EXECUTION_ENDPOINT: HttpUrl = Field(
        description="代码执行服务的端点 URL。",
        default="http://sandbox:8194",
    )
    """
    CODE_EXECUTION_ENDPOINT 属性：
    - 类型：HttpUrl
    - 描述：代码执行服务的端点 URL。
    - 默认值："http://sandbox:8194"
    - 说明：代码执行服务的端点 URL，用于发送代码执行请求。
    """

    CODE_EXECUTION_API_KEY: str = Field(
        description="代码执行服务的 API 密钥。",
        default="dify-sandbox",
    )
    """
    CODE_EXECUTION_API_KEY 属性：
    - 类型：str
    - 描述：代码执行服务的 API 密钥。
    - 默认值："dify-sandbox"
    - 说明：用于身份验证的 API 密钥，确保代码执行请求的安全性。
    """

    CODE_EXECUTION_CONNECT_TIMEOUT: Optional[float] = Field(
        description="代码执行请求的连接超时时间，单位为秒。",
        default=10.0,
    )
    """
    CODE_EXECUTION_CONNECT_TIMEOUT 属性：
    - 类型：Optional[float]
    - 描述：代码执行请求的连接超时时间，单位为秒。
    - 默认值：10.0
    - 说明：连接超时时间，用于控制连接到代码执行服务的最大等待时间。
    """

    CODE_EXECUTION_READ_TIMEOUT: Optional[float] = Field(
        description="代码执行请求的读取超时时间，单位为秒。",
        default=60.0,
    )
    """
    CODE_EXECUTION_READ_TIMEOUT 属性：
    - 类型：Optional[float]
    - 描述：代码执行请求的读取超时时间，单位为秒。
    - 默认值：60.0
    - 说明：读取超时时间，用于控制从代码执行服务读取响应的最大等待时间。
    """

    CODE_EXECUTION_WRITE_TIMEOUT: Optional[float] = Field(
        description="代码执行请求的写入超时时间，单位为秒。",
        default=10.0,
    )
    """
    CODE_EXECUTION_WRITE_TIMEOUT 属性：
    - 类型：Optional[float]
    - 描述：代码执行请求的写入超时时间，单位为秒。
    - 默认值：10.0
    - 说明：写入超时时间，用于控制向代码执行服务发送请求的最大等待时间。
    """

    # TODO code max number
    CODE_MAX_NUMBER: PositiveInt = Field(
        description="max depth for code execution",
        default=9223372036854775807,
    )
    """
    CODE_MAX_NUMBER 属性：
    - 类型：PositiveInt
    - 描述：代码执行的最大数值限制。
    - 默认值：9223372036854775807
    - 说明：用于限制代码执行中数值的最大值，防止数值溢出。
    """

    CODE_MIN_NUMBER: NegativeInt = Field(
        description="代码执行的最小数值限制。",
        default=-9223372036854775807,
    )
    """
    CODE_MIN_NUMBER 属性：
    - 类型：NegativeInt
    - 描述：代码执行的最小数值限制。
    - 默认值：-9223372036854775807
    - 说明：用于限制代码执行中数值的最小值，防止数值溢出。
    """

    CODE_MAX_DEPTH: PositiveInt = Field(
        description="max depth for code execution",
        default=5,
    )
    """
    CODE_MAX_DEPTH 属性：
    - 类型：PositiveInt
    - 描述：代码执行的最大深度限制。
    - 默认值：5
    - 说明：用于限制代码执行的递归深度，防止无限递归。
    """

    CODE_MAX_PRECISION: PositiveInt = Field(
        description="代码执行中浮点数的最大精度位数。",
        default=20,
    )
    """
    CODE_MAX_PRECISION 属性：
    - 类型：PositiveInt
    - 描述：代码执行中浮点数的最大精度位数。
    - 默认值：20
    - 说明：用于限制代码执行中浮点数的精度，防止精度溢出。
    """

    CODE_MAX_STRING_LENGTH: PositiveInt = Field(
        description="代码执行中字符串的最大长度限制。",
        default=80000,
    )
    """
    CODE_MAX_STRING_LENGTH 属性：
    - 类型：PositiveInt
    - 描述：代码执行中字符串的最大长度限制。
    - 默认值：80000
    - 说明：用于限制代码执行中字符串的长度，防止内存溢出。
    """

    CODE_MAX_STRING_ARRAY_LENGTH: PositiveInt = Field(
        description="代码执行中字符串数组的最大长度限制。",
        default=30,
    )
    """
    CODE_MAX_STRING_ARRAY_LENGTH 属性：
    - 类型：PositiveInt
    - 描述：代码执行中字符串数组的最大长度限制。
    - 默认值：30
    - 说明：用于限制代码执行中字符串数组的长度，防止内存溢出。
    """

    CODE_MAX_OBJECT_ARRAY_LENGTH: PositiveInt = Field(
        description="代码执行中对象数组的最大长度限制。",
        default=30,
    )
    """
    CODE_MAX_OBJECT_ARRAY_LENGTH 属性：
    - 类型：PositiveInt
    - 描述：代码执行中对象数组的最大长度限制。
    - 默认值：30
    - 说明：用于限制代码执行中对象数组的长度，防止内存溢出。
    """

    CODE_MAX_NUMBER_ARRAY_LENGTH: PositiveInt = Field(
        description="代码执行中数值数组的最大长度限制。",
        default=1000,
    )
    """
    CODE_MAX_NUMBER_ARRAY_LENGTH 属性：
    - 类型：PositiveInt
    - 描述：代码执行中数值数组的最大长度限制。
    - 默认值：1000
    - 说明：用于限制代码执行中数值数组的长度，防止内存溢出。
    """


class EndpointConfig(BaseSettings):
    """
    模块 URL 配置类。

    该类用于配置不同模块的 URL 前缀，以便在应用程序中使用这些 URL 进行各种操作，如登录授权回调、Notion 集成回调、前端地址拼接以及 CORS 配置等。
    """

    CONSOLE_API_URL: str = Field(
        description="控制台 API 的后端 URL 前缀。"
        "用于拼接登录授权回调或 Notion 集成回调的 URL。",
        default="",
    )
    """
    CONSOLE_API_URL 属性：
    - 类型：str
    - 描述：控制台 API 的后端 URL 前缀。
    - 默认值：空字符串
    - 说明：用于拼接登录授权回调或 Notion 集成回调的 URL。
    """

    CONSOLE_WEB_URL: str = Field(
        description="控制台 Web 的前端 URL 前缀。"
        "用于拼接一些前端地址，并用于 CORS 配置。",
        default="",
    )
    """
    CONSOLE_WEB_URL 属性：
    - 类型：str
    - 描述：控制台 Web 的前端 URL 前缀。
    - 默认值：空字符串
    - 说明：用于拼接一些前端地址，并用于 CORS 配置。
    """

    SERVICE_API_URL: str = Field(
        description="服务 API 的 URL 前缀。"
        "用于向前端显示服务 API 的基础 URL。",
        default="",
    )
    """
    SERVICE_API_URL 属性：
    - 类型：str
    - 描述：服务 API 的 URL 前缀。
    - 默认值：空字符串
    - 说明：用于向前端显示服务 API 的基础 URL。
    """

    APP_WEB_URL: str = Field(
        description="WebApp 的 URL 前缀。"
        "用于向前端显示 WebApp API 的基础 URL。",
        default="",
    )
    """
    APP_WEB_URL 属性：
    - 类型：str
    - 描述：WebApp 的 URL 前缀。
    - 默认值：空字符串
    - 说明：用于向前端显示 WebApp API 的基础 URL。
    """


class FileAccessConfig(BaseSettings):
    """
    文件访问配置类，用于定义与文件访问相关的配置项。

    主要用途：
    - 配置文件预览或下载的 URL 前缀。
    - 配置文件访问的超时时间。

    属性：
    - FILES_URL: 文件预览或下载的 URL 前缀。
    - FILES_ACCESS_TIMEOUT: 文件访问的超时时间，单位为秒。
    """

    FILES_URL: str = Field(
        description="文件预览或下载的 URL 前缀。"
        "用于向前端显示文件预览或下载的 URL，或作为多模型输入；"
        "URL 是签名且具有过期时间的。",
        validation_alias=AliasChoices("FILES_URL", "CONSOLE_API_URL"),
        alias_priority=1,
        default="",
    )
    """
    FILES_URL 属性：
    - 类型：str
    - 描述：文件预览或下载的 URL 前缀。
    - 默认值：空字符串
    - 说明：用于向前端显示文件预览或下载的 URL，或作为多模型输入；URL 是签名且具有过期时间的。
    - validation_alias: 验证别名，允许使用 "FILES_URL" 或 "CONSOLE_API_URL" 作为别名。
    - alias_priority: 别名优先级，设置为 1。
    """

    FILES_ACCESS_TIMEOUT: int = Field(
        description="文件访问的超时时间，单位为秒。",
        default=300,
    )
    """
    FILES_ACCESS_TIMEOUT 属性：
    - 类型：int
    - 描述：文件访问的超时时间，单位为秒。
    - 默认值：300 秒
    - 说明：定义文件访问的超时时间，超过此时间未完成访问则视为超时。
    """


class FileUploadConfig(BaseSettings):
    """
    文件上传配置类，用于定义与文件上传相关的配置项。

    主要用途：
    - 配置上传文件的大小限制。
    - 配置上传文件的批次限制。
    - 配置上传图片文件的大小限制。
    - 配置批量上传的限制。

    属性：
    - UPLOAD_FILE_SIZE_LIMIT: 上传文件的大小限制，单位为兆字节（MB）。
    - UPLOAD_FILE_BATCH_LIMIT: 上传文件的批次限制。
    - UPLOAD_IMAGE_FILE_SIZE_LIMIT: 上传图片文件的大小限制，单位为兆字节（MB）。
    - BATCH_UPLOAD_LIMIT: 批量上传的限制。
    """

    UPLOAD_FILE_SIZE_LIMIT: NonNegativeInt = Field(
        description="上传文件的大小限制，单位为兆字节（MB）。",
        default=15,
    )
    """
    UPLOAD_FILE_SIZE_LIMIT 属性：
    - 类型：NonNegativeInt
    - 描述：上传文件的大小限制，单位为兆字节（MB）。
    - 默认值：15 MB
    - 说明：用于限制单个文件上传的最大大小，防止文件过大导致服务器资源耗尽。
    """

    UPLOAD_FILE_BATCH_LIMIT: NonNegativeInt = Field(
        description="上传文件的批次限制。",
        default=5,
    )
    """
    UPLOAD_FILE_BATCH_LIMIT 属性：
    - 类型：NonNegativeInt
    - 描述：上传文件的批次限制。
    - 默认值：5
    - 说明：用于限制一次上传的文件数量，防止批量上传过多文件导致服务器负载过高。
    """

    UPLOAD_IMAGE_FILE_SIZE_LIMIT: NonNegativeInt = Field(
        description="上传图片文件的大小限制，单位为兆字节（MB）。",
        default=10,
    )
    """
    UPLOAD_IMAGE_FILE_SIZE_LIMIT 属性：
    - 类型：NonNegativeInt
    - 描述：上传图片文件的大小限制，单位为兆字节（MB）。
    - 默认值：10 MB
    - 说明：用于限制单个图片文件上传的最大大小，防止图片文件过大导致服务器资源耗尽。
    """

    BATCH_UPLOAD_LIMIT: NonNegativeInt = Field(
        description="",  # todo: to be clarified
        default=20,
    )
    """
    BATCH_UPLOAD_LIMIT 属性：
    - 类型：NonNegativeInt
    - 描述：批量上传的限制。
    - 默认值：20
    - 说明：用于限制批量上传的总次数或总文件数，防止频繁或大量上传导致服务器负载过高。
    """


# AliasChoices 用于定义字段的多个别名。例如，inner_CONSOLE_CORS_ALLOW_ORIGINS
# 字段可以使用 CONSOLE_CORS_ALLOW_ORIGINS 或 CONSOLE_WEB_URL 作为别名。
# Annotated 用于为字段添加额外的验证规则。
# 例如，HTTP_REQUEST_MAX_CONNECT_TIMEOUT 字段被定义为 PositiveInt，并且必须大于或等于 10。
# computed_field 是 Pydantic 中的一个装饰器，用于定义计算属性。
# 计算属性是根据其他字段的值动态计算得出的属性，而不是直接从数据源加载的。
class HttpConfig(BaseSettings):
    """
    HTTP 配置类，用于管理与 HTTP 请求和响应相关的配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    API_COMPRESSION_ENABLED: bool = Field(
        description="是否启用 HTTP 响应的 gzip 压缩。",
        default=False,
    )
    """
    API_COMPRESSION_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用 HTTP 响应的 gzip 压缩。
    - 默认值：False
    - 说明：启用后，HTTP 响应将使用 gzip 压缩，减少传输数据量，提高性能。
    """

    inner_CONSOLE_CORS_ALLOW_ORIGINS: str = Field(
        description="控制台 CORS 允许的源列表，以逗号分隔。",
        validation_alias=AliasChoices("CONSOLE_CORS_ALLOW_ORIGINS", "CONSOLE_WEB_URL"),
        default="",
    )
    """
    inner_CONSOLE_CORS_ALLOW_ORIGINS 属性：
    - 类型：str
    - 描述：控制台 CORS 允许的源列表，以逗号分隔。
    - 默认值：空字符串
    - 说明：用于配置控制台的 CORS 策略，允许指定的源访问控制台资源。
    """

    @computed_field
    @property
    def CONSOLE_CORS_ALLOW_ORIGINS(self) -> list[str]:
        """
        计算属性，将 `inner_CONSOLE_CORS_ALLOW_ORIGINS` 字符串转换为列表。

        返回值：
        - 类型：list[str]
        - 说明：返回一个包含允许源的列表。
        """
        return self.inner_CONSOLE_CORS_ALLOW_ORIGINS.split(",")

    inner_WEB_API_CORS_ALLOW_ORIGINS: str = Field(
        description="Web API CORS 允许的源列表，以逗号分隔。",
        validation_alias=AliasChoices("WEB_API_CORS_ALLOW_ORIGINS"),
        default="*",
    )
    """
    inner_WEB_API_CORS_ALLOW_ORIGINS 属性：
    - 类型：str
    - 描述：Web API CORS 允许的源列表，以逗号分隔。
    - 默认值："*"
    - 说明：用于配置 Web API 的 CORS 策略，允许指定的源访问 Web API 资源。
    """

    @computed_field
    @property
    def WEB_API_CORS_ALLOW_ORIGINS(self) -> list[str]:
        """
        计算属性，将 `inner_WEB_API_CORS_ALLOW_ORIGINS` 字符串转换为列表。

        返回值：
        - 类型：list[str]
        - 说明：返回一个包含允许源的列表。
        """
        return self.inner_WEB_API_CORS_ALLOW_ORIGINS.split(",")

    HTTP_REQUEST_MAX_CONNECT_TIMEOUT: Annotated[
        PositiveInt, Field(ge=10, description="HTTP 请求的连接超时时间，单位为秒。")
    ] = 10
    """
    HTTP_REQUEST_MAX_CONNECT_TIMEOUT 属性：
    - 类型：PositiveInt
    - 描述：HTTP 请求的连接超时时间，单位为秒。
    - 默认值：10
    - 说明：设置 HTTP 请求的最大连接超时时间，防止连接时间过长导致资源浪费。
    """

    HTTP_REQUEST_MAX_READ_TIMEOUT: Annotated[
        PositiveInt, Field(ge=60, description="HTTP 请求的读取超时时间，单位为秒。")
    ] = 60
    """
    HTTP_REQUEST_MAX_READ_TIMEOUT 属性：
    - 类型：PositiveInt
    - 描述：HTTP 请求的读取超时时间，单位为秒。
    - 默认值：60
    - 说明：设置 HTTP 请求的最大读取超时时间，防止读取时间过长导致资源浪费。
    """

    HTTP_REQUEST_MAX_WRITE_TIMEOUT: Annotated[
        PositiveInt, Field(ge=10, description="HTTP 请求的写入超时时间，单位为秒。")
    ] = 20
    """
    HTTP_REQUEST_MAX_WRITE_TIMEOUT 属性：
    - 类型：PositiveInt
    - 描述：HTTP 请求的写入超时时间，单位为秒。
    - 默认值：20
    - 说明：设置 HTTP 请求的最大写入超时时间，防止写入时间过长导致资源浪费。
    """

    HTTP_REQUEST_NODE_MAX_BINARY_SIZE: PositiveInt = Field(
        description="HTTP 请求节点允许的最大二进制文件大小，单位为字节。",
        default=10 * 1024 * 1024,
    )
    """
    HTTP_REQUEST_NODE_MAX_BINARY_SIZE 属性：
    - 类型：PositiveInt
    - 描述：HTTP 请求节点允许的最大二进制文件大小，单位为字节。
    - 默认值：10 * 1024 * 1024（10 MB）
    - 说明：设置 HTTP 请求节点允许上传的最大二进制文件大小，防止文件过大导致服务器资源耗尽。
    """

    HTTP_REQUEST_NODE_MAX_TEXT_SIZE: PositiveInt = Field(
        description="HTTP 请求节点允许的最大文本文件大小，单位为字节。",
        default=1 * 1024 * 1024,
    )
    """
    HTTP_REQUEST_NODE_MAX_TEXT_SIZE 属性：
    - 类型：PositiveInt
    - 描述：HTTP 请求节点允许的最大文本文件大小，单位为字节。
    - 默认值：1 * 1024 * 1024（1 MB）
    - 说明：设置 HTTP 请求节点允许上传的最大文本文件大小，防止文件过大导致服务器资源耗尽。
    """

    SSRF_PROXY_HTTP_URL: Optional[str] = Field(
        description="SSRF 代理的 HTTP URL。",
        default=None,
    )
    """
    SSRF_PROXY_HTTP_URL 属性：
    - 类型：Optional[str]
    - 描述：SSRF 代理的 HTTP URL。
    - 默认值：None
    - 说明：用于配置 SSRF 代理的 HTTP URL，防止 SSRF 攻击。
    """

    SSRF_PROXY_HTTPS_URL: Optional[str] = Field(
        description="SSRF 代理的 HTTPS URL。",
        default=None,
    )
    """
    SSRF_PROXY_HTTPS_URL 属性：
    - 类型：Optional[str]
    - 描述：SSRF 代理的 HTTPS URL。
    - 默认值：None
    - 说明：用于配置 SSRF 代理的 HTTPS URL，防止 SSRF 攻击。
    """


class InnerAPIConfig(BaseSettings):
    """
    Inner API 配置类，用于管理内部 API 的相关配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    INNER_API: bool = Field(
        description="是否启用内部 API。",
        default=False,
    )
    """
    INNER_API 属性：
    - 类型：bool
    - 描述：是否启用内部 API。
    - 默认值：False
    - 说明：用于控制是否启用内部 API 功能。
    """

    INNER_API_KEY: Optional[str] = Field(
        description="内部 API 密钥，用于内部 API 的身份验证。",
        default=None,
    )
    """
    INNER_API_KEY 属性：
    - 类型：Optional[str]
    - 描述：内部 API 密钥，用于内部 API 的身份验证。
    - 默认值：None
    - 说明：用于配置内部 API 的身份验证密钥，确保内部 API 的安全性。
    """


class LoggingConfig(BaseSettings):
    """
    日志配置类，用于管理应用程序的日志输出设置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    LOG_LEVEL: str = Field(
        description="日志输出级别，默认为 INFO。建议在生产环境中设置为 ERROR。",
        default="INFO",
    )
    """
    LOG_LEVEL 属性：
    - 类型：str
    - 描述：日志输出级别，控制日志的详细程度。
    - 默认值："INFO"
    - 说明：建议在生产环境中设置为 "ERROR"，以减少日志输出量。
    """

    LOG_FILE: Optional[str] = Field(
        description="日志输出文件路径。",
        default=None,
    )
    """
    LOG_FILE 属性：
    - 类型：Optional[str]
    - 描述：日志输出文件的路径，指定日志文件的存储位置。
    - 默认值：None
    - 说明：如果未指定，日志将输出到标准输出（stdout）。
    """

    LOG_FORMAT: str = Field(
        description="日志格式。",
        default="%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(filename)s:%(lineno)d] - %(message)s",
    )
    """
    LOG_FORMAT 属性：
    - 类型：str
    - 描述：日志格式，定义日志输出的格式。
    - 默认值："%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(filename)s:%(lineno)d] - %(message)s"
    - 说明：包含时间、日志级别、线程名、文件名、行号和日志消息等信息。
    """

    LOG_DATEFORMAT: Optional[str] = Field(
        description="日志日期格式。",
        default=None,
    )
    """
    LOG_DATEFORMAT 属性：
    - 类型：Optional[str]
    - 描述：日志日期格式，定义日志中日期时间的显示格式。
    - 默认值：None
    - 说明：如果未指定，将使用默认的日期格式。
    """

    LOG_TZ: Optional[str] = Field(
        description="指定日志时区，例如：America/New_York。",
        default=None,
    )
    """
    LOG_TZ 属性：
    - 类型：Optional[str]
    - 描述：日志时区，指定日志输出的时区。
    - 默认值：None
    - 说明：如果未指定，将使用系统默认时区。
    """


class ModelLoadBalanceConfig(BaseSettings):
    """
    ModelLoadBalanceConfig 类用于管理模型负载均衡的配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    主要用途是控制是否启用模型负载均衡功能。
    """

    MODEL_LB_ENABLED: bool = Field(
        description="是否启用模型负载均衡功能。",
        default=False,
    )
    """
    MODEL_LB_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用模型负载均衡功能。
    - 默认值：False
    - 说明：启用后，系统将根据负载情况动态分配模型请求，以提高系统性能和稳定性。
    """


class BillingConfig(BaseSettings):
    """
    平台计费配置类，用于管理平台计费功能的启用状态。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    主要用途是控制是否启用平台的计费功能。
    """

    BILLING_ENABLED: bool = Field(
        description="是否启用计费功能。",
        default=False,
    )
    """
    BILLING_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用计费功能。
    - 默认值：False
    - 说明：启用后，平台将根据用户的使用情况进行计费。
    """


class UpdateConfig(BaseSettings):
    """
    UpdateConfig 类用于管理应用程序的更新检查配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    主要用途是定义检查更新的 URL，以便应用程序能够定期检查是否有新版本可用。
    """

    CHECK_UPDATE_URL: str = Field(
        description="用于检查更新的 URL。",
        default="https://updates.dify.ai",
    )
    """
    CHECK_UPDATE_URL 属性：
    - 类型：str
    - 描述：用于检查更新的 URL。
    - 默认值："https://updates.dify.ai"
    - 说明：应用程序将使用此 URL 定期检查是否有新版本可用。
    """


class WorkflowConfig(BaseSettings):
    """
    WorkflowConfig 类用于管理工作流功能的相关配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    主要用途是定义工作流执行的最大步骤数、最大执行时间、调用深度以及变量大小的限制。
    """

    WORKFLOW_MAX_EXECUTION_STEPS: PositiveInt = Field(
        description="单个工作流执行中的最大执行步骤数。",
        default=500,
    )
    """
    WORKFLOW_MAX_EXECUTION_STEPS 属性：
    - 类型：PositiveInt
    - 描述：单个工作流执行中的最大执行步骤数。
    - 默认值：500
    - 说明：用于限制单个工作流执行中的步骤数，防止无限循环或过多的步骤导致资源耗尽。
    """

    WORKFLOW_MAX_EXECUTION_TIME: PositiveInt = Field(
        description="单个工作流执行中的最大执行时间，单位为秒。",
        default=1200,
    )
    """
    WORKFLOW_MAX_EXECUTION_TIME 属性：
    - 类型：PositiveInt
    - 描述：单个工作流执行中的最大执行时间，单位为秒。
    - 默认值：1200
    - 说明：用于限制单个工作流执行的时间，防止执行时间过长导致资源浪费。
    """

    # TODO workflow调用深度应该怎么处理
    WORKFLOW_CALL_MAX_DEPTH: PositiveInt = Field(
        description="单个工作流执行中的最大调用深度。",
        default=5,
    )
    """
    WORKFLOW_CALL_MAX_DEPTH 属性：
    - 类型：PositiveInt
    - 描述：单个工作流执行中的最大调用深度。
    - 默认值：5
    - 说明：用于限制工作流中的调用深度，防止无限递归或过深的调用导致资源耗尽。
    """

    MAX_VARIABLE_SIZE: PositiveInt = Field(
        description="变量的最大大小，单位为字节，默认值为 5KB。",
        default=5 * 1024,
    )
    """
    MAX_VARIABLE_SIZE 属性：
    - 类型：PositiveInt
    - 描述：变量的最大大小，单位为字节，默认值为 5KB。
    - 默认值：5 * 1024
    - 说明：用于限制工作流中变量的大小，防止变量过大导致内存溢出。
    """


class OAuthConfig(BaseSettings):
    """
    OAuth 配置类，用于管理 OAuth 认证的相关配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。
    """

    OAUTH_REDIRECT_PATH: str = Field(
        description="OAuth 认证后的重定向路径。",
        default="/console/api/oauth/authorize",
    )
    """
    OAUTH_REDIRECT_PATH 属性：
    - 类型：str
    - 描述：OAuth 认证后的重定向路径。
    - 默认值："/console/api/oauth/authorize"
    - 说明：用于指定 OAuth 认证成功后的重定向路径，通常是用户授权后的回调地址。
    """

    GITHUB_CLIENT_ID: Optional[str] = Field(
        description="GitHub OAuth 客户端 ID。",
        default=None,
    )
    """
    GITHUB_CLIENT_ID 属性：
    - 类型：Optional[str]
    - 描述：GitHub OAuth 客户端 ID。
    - 默认值：None
    - 说明：用于配置 GitHub OAuth 认证的客户端 ID，确保 OAuth 认证的正确性。
    """

    GITHUB_CLIENT_SECRET: Optional[str] = Field(
        description="GitHub OAuth 客户端密钥。",
        default=None,
    )
    """
    GITHUB_CLIENT_SECRET 属性：
    - 类型：Optional[str]
    - 描述：GitHub OAuth 客户端密钥。
    - 默认值：None
    - 说明：用于配置 GitHub OAuth 认证的客户端密钥，确保 OAuth 认证的安全性。
    """

    GOOGLE_CLIENT_ID: Optional[str] = Field(
        description="Google OAuth 客户端 ID。",
        default=None,
    )
    """
    GOOGLE_CLIENT_ID 属性：
    - 类型：Optional[str]
    - 描述：Google OAuth 客户端 ID。
    - 默认值：None
    - 说明：用于配置 Google OAuth 认证的客户端 ID，确保 OAuth 认证的正确性。
    """

    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        description="Google OAuth 客户端密钥。",
        default=None,
    )
    """
    GOOGLE_CLIENT_SECRET 属性：
    - 类型：Optional[str]
    - 描述：Google OAuth 客户端密钥。
    - 默认值：None
    - 说明：用于配置 Google OAuth 认证的客户端密钥，确保 OAuth 认证的安全性。
    """


class ModerationConfig(BaseSettings):
    """
    应用中的审核配置类。

    该类继承自 `BaseSettings`，用于定义与审核相关的配置项。
    主要用途是配置审核系统中的缓冲区大小，以确保审核过程的效率和稳定性。
    """

    MODERATION_BUFFER_SIZE: PositiveInt = Field(
        description="审核系统的缓冲区大小。",
        default=300,
    )
    """
    MODERATION_BUFFER_SIZE 属性：
    - 类型：PositiveInt
    - 描述：审核系统的缓冲区大小。
    - 默认值：300
    - 说明：该属性定义了审核系统中用于存储待审核内容的缓冲区大小。缓冲区的大小直接影响审核系统的性能和响应速度。较大的缓冲区可以处理更多的待审核内容，但也会占用更多的内存资源。默认值为 300，适用于大多数情况。
    """


class ToolConfig(BaseSettings):
    """
    ToolConfig 类用于定义与工具相关的配置项。

    该类继承自 `BaseSettings`，主要用途是配置工具图标缓存的过期时间，以确保工具图标的缓存管理。
    """

    TOOL_ICON_CACHE_MAX_AGE: PositiveInt = Field(
        description="工具图标缓存的最大过期时间，单位为秒。",
        default=3600,
    )
    """
    TOOL_ICON_CACHE_MAX_AGE 属性：
    - 类型：PositiveInt
    - 描述：工具图标缓存的最大过期时间，单位为秒。
    - 默认值：3600
    - 说明：该属性定义了工具图标在缓存中的最大存活时间。超过这个时间后，缓存中的图标将被视为过期并重新加载。默认值为 3600 秒（1 小时），适用于大多数情况。较大的缓存时间可以减少图标的加载次数，但也会增加缓存占用的内存资源。
    """


class MailConfig(BaseSettings):
    """
    MailConfig 类用于定义与邮件相关的配置项。

    该类继承自 `BaseSettings`，主要用途是配置邮件发送的相关参数，包括邮件提供商类型、默认发送地址、Resend API 密钥和 URL、SMTP 服务器配置等。
    这些配置项用于确保邮件发送的可靠性和安全性。
    """

    MAIL_TYPE: Optional[str] = Field(
        description="邮件提供商类型名称，默认为 None，可选值为 `smtp` 和 `resend`。",
        default=None,
    )
    """
    MAIL_TYPE 属性：
    - 类型：Optional[str]
    - 描述：邮件提供商类型名称。
    - 默认值：None
    - 说明：该属性定义了邮件发送所使用的提供商类型。可选值为 `smtp` 和 `resend`。默认为 None，表示未指定提供商类型。
    """

    MAIL_DEFAULT_SEND_FROM: Optional[str] = Field(
        description="默认的发送邮件地址。",
        default=None,
    )
    """
    MAIL_DEFAULT_SEND_FROM 属性：
    - 类型：Optional[str]
    - 描述：默认的发送邮件地址。
    - 默认值：None
    - 说明：该属性定义了默认的发送邮件地址。默认为 None，表示未指定默认发送地址。
    """

    RESEND_API_KEY: Optional[str] = Field(
        description="Resend API 密钥。",
        default=None,
    )
    """
    RESEND_API_KEY 属性：
    - 类型：Optional[str]
    - 描述：Resend API 密钥。
    - 默认值：None
    - 说明：该属性定义了 Resend API 的密钥。默认为 None，表示未指定 API 密钥。
    """

    RESEND_API_URL: Optional[str] = Field(
        description="Resend API URL。",
        default=None,
    )
    """
    RESEND_API_URL 属性：
    - 类型：Optional[str]
    - 描述：Resend API URL。
    - 默认值：None
    - 说明：该属性定义了 Resend API 的 URL。默认为 None，表示未指定 API URL。
    """

    SMTP_SERVER: Optional[str] = Field(
        description="SMTP 服务器主机地址。",
        default=None,
    )
    """
    SMTP_SERVER 属性：
    - 类型：Optional[str]
    - 描述：SMTP 服务器主机地址。
    - 默认值：None
    - 说明：该属性定义了 SMTP 服务器的主机地址。默认为 None，表示未指定 SMTP 服务器地址。
    """

    SMTP_PORT: Optional[int] = Field(
        description="SMTP 服务器端口号。",
        default=465,
    )
    """
    SMTP_PORT 属性：
    - 类型：Optional[int]
    - 描述：SMTP 服务器端口号。
    - 默认值：465
    - 说明：该属性定义了 SMTP 服务器的端口号。默认为 465，表示使用 SSL/TLS 加密的 SMTP 端口。
    """

    SMTP_USERNAME: Optional[str] = Field(
        description="SMTP 服务器用户名。",
        default=None,
    )
    """
    SMTP_USERNAME 属性：
    - 类型：Optional[str]
    - 描述：SMTP 服务器用户名。
    - 默认值：None
    - 说明：该属性定义了 SMTP 服务器的用户名。默认为 None，表示未指定用户名。
    """

    SMTP_PASSWORD: Optional[str] = Field(
        description="SMTP 服务器密码。",
        default=None,
    )
    """
    SMTP_PASSWORD 属性：
    - 类型：Optional[str]
    - 描述：SMTP 服务器密码。
    - 默认值：None
    - 说明：该属性定义了 SMTP 服务器的密码。默认为 None，表示未指定密码。
    """

    SMTP_USE_TLS: bool = Field(
        description="是否使用 TLS 连接到 SMTP 服务器。",
        default=False,
    )
    """
    SMTP_USE_TLS 属性：
    - 类型：bool
    - 描述：是否使用 TLS 连接到 SMTP 服务器。
    - 默认值：False
    - 说明：该属性定义了是否使用 TLS 连接到 SMTP 服务器。默认为 False，表示不使用 TLS 连接。
    """

    # Opportunistic TLS: 这是一种安全措施，允许在不安全的连接上自动升级到 TLS（Transport Layer Security）加密连接。
    # 如果服务器支持 TLS，客户端会尝试使用 TLS 加密通信。如果服务器不支持 TLS，通信将继续以明文形式进行。
    SMTP_OPPORTUNISTIC_TLS: bool = Field(
        description="是否使用 opportunistic TLS 连接到 SMTP 服务器。",
        default=False,
    )
    """
    SMTP_OPPORTUNISTIC_TLS 属性：
    - 类型：bool
    - 描述：是否使用 opportunistic TLS 连接到 SMTP 服务器。
    - 默认值：False
    - 说明：该属性定义了是否使用 opportunistic TLS 连接到 SMTP 服务器。默认为 False，表示不使用 opportunistic TLS 连接。
    """


class RagEtlConfig(BaseSettings):
    """
    RAG ETL 配置类。
    ETL: 指的是数据处理过程中的三个步骤：提取（Extract）、转换（Transform）和加载（Load）。
    在 RAG 上下文中，ETL 通常用于处理和准备数据，以便用于生成任务。
    该类用于定义 RAG ETL 相关的配置参数。每个属性对应一个配置项，并提供了详细的描述和默认值。
    
    """

    ETL_TYPE: str = Field(
        description="RAG ETL 类型名称，默认为 `dify`，可选值为 `dify` 和 `Unstructured`。",
        default="dify",
    )
    """
    ETL_TYPE 属性：
    - 类型：str
    - 描述：RAG ETL 类型名称。
    - 默认值："dify"
    - 说明：该属性定义了 RAG ETL 的类型名称。默认为 "dify"，可选值为 "dify" 和 "Unstructured"。
    """

    KEYWORD_DATA_SOURCE_TYPE: str = Field(
        description="关键词数据的源类型，默认为 `database`，可选值为 `database`。",
        default="database",
    )
    """
    KEYWORD_DATA_SOURCE_TYPE 属性：
    - 类型：str
    - 描述：关键词数据的源类型。
    - 默认值："database"
    - 说明：该属性定义了关键词数据的源类型。默认为 "database"，可选值为 "database"。
    """

    UNSTRUCTURED_API_URL: Optional[str] = Field(
        description="Unstructured API 的 URL。",
        default=None,
    )
    """
    UNSTRUCTURED_API_URL 属性：
    - 类型：Optional[str]
    - 描述：Unstructured API 的 URL。
    - 默认值：None
    - 说明：该属性定义了 Unstructured API 的 URL。默认为 None，表示未指定 URL。
    """

    UNSTRUCTURED_API_KEY: Optional[str] = Field(
        description="Unstructured API 的密钥。",
        default=None,
    )
    """
    UNSTRUCTURED_API_KEY 属性：
    - 类型：Optional[str]
    - 描述：Unstructured API 的密钥。
    - 默认值：None
    - 说明：该属性定义了 Unstructured API 的密钥。默认为 None，表示未指定密钥。
    """


class DataSetConfig(BaseSettings):
    """
    数据集配置类

    该类用于定义与数据集相关的配置参数。它继承自 `BaseSettings`，并包含两个属性：`CLEAN_DAY_SETTING` 和 `DATASET_OPERATOR_ENABLED`。

    属性：
    - `CLEAN_DAY_SETTING`: 定义了数据集清理的时间间隔（以天为单位）。
    - `DATASET_OPERATOR_ENABLED`: 定义是否启用数据集操作。
    """

    CLEAN_DAY_SETTING: PositiveInt = Field(
        description="数据集清理的时间间隔（以天为单位）",
        default=30,
    )
    """
    CLEAN_DAY_SETTING 属性：
    - 类型：PositiveInt
    - 描述：数据集清理的时间间隔（以天为单位）。
    - 默认值：30
    - 说明：该属性定义了数据集清理的时间间隔。默认值为 30 天，表示每 30 天进行一次数据集清理。
    """

    DATASET_OPERATOR_ENABLED: bool = Field(
        description="是否启用数据集操作",
        default=False,
    )
    """
    DATASET_OPERATOR_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用数据集操作。
    - 默认值：False
    - 说明：该属性定义了是否启用数据集操作。默认值为 False，表示不启用数据集操作。
    """


class WorkspaceConfig(BaseSettings):
    """
    WorkspaceConfig 类用于管理工作区的相关配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。主要用途是定义工作区邀请链接的过期时间。
    """

    INVITE_EXPIRY_HOURS: PositiveInt = Field(
        description="工作区邀请链接的过期时间，单位为小时。",
        default=72,
    )
    """
    INVITE_EXPIRY_HOURS 属性：
    - 类型：PositiveInt
    - 描述：工作区邀请链接的过期时间，单位为小时。
    - 默认值：72
    - 说明：该属性定义了工作区邀请链接的有效期。默认值为 72 小时，表示邀请链接在创建后 72 小时内有效。
    """


class IndexingConfig(BaseSettings):
    """
    IndexingConfig 类用于管理索引配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。主要用途是定义索引过程中分段的最大标记长度。
    """

    INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH: PositiveInt = Field(
        description="索引过程中分段的最大标记长度",
        default=1000,
    )
    """
    INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH 属性：
    - 类型：PositiveInt
    - 描述：索引过程中分段的最大标记长度。
    - 默认值：1000
    - 说明：该属性定义了在索引过程中，文本被分段时的最大标记长度。默认值为 1000，表示每个分段的最大标记长度为 1000。
    """


class ImageFormatConfig(BaseSettings):
    """
    ImageFormatConfig 类用于管理多模态发送图像格式的配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。主要用途是定义多模态发送图像的格式。
    """

    MULTIMODAL_SEND_IMAGE_FORMAT: str = Field(
        description="多模态发送图像的格式，支持 base64 和 url，默认值为 base64。",
        default="base64",
    )
    """
    MULTIMODAL_SEND_IMAGE_FORMAT 属性：
    - 类型：str
    - 描述：多模态发送图像的格式。
    - 默认值："base64"
    - 说明：该属性定义了多模态发送图像的格式，支持 base64 和 url 两种格式。默认值为 base64，表示图像将以 base64 编码的形式发送。
    """

# CeleryBeat 是一个定时任务调度器，用于周期性地执行任务。它是 Celery 项目的一部分，Celery 是一个分布式任务队列，用于处理异步任务和定时任务。
# Celery: 一个分布式任务队列，用于处理异步任务和定时任务。
# CeleryBeat: Celery 的定时任务调度器，用于周期性地执行任务。
class CeleryBeatConfig(BaseSettings):
    """
    CeleryBeatConfig 类用于管理 Celery Beat 调度器的配置。

    该类继承自 `BaseSettings`，用于从环境变量或配置文件中加载配置。主要用途是定义 Celery Beat 调度器的时间间隔。
    """

    CELERY_BEAT_SCHEDULER_TIME: int = Field(
        description="Celery Beat 调度器的时间间隔，默认值为 1 天。",
        default=1,
    )
    """
    CELERY_BEAT_SCHEDULER_TIME 属性：
    - 类型：int
    - 描述：Celery Beat 调度器的时间间隔，单位为天。
    - 默认值：1
    - 说明：该属性定义了 Celery Beat 调度器的时间间隔。默认值为 1 天，表示调度器每隔 1 天执行一次任务。
    """


class PositionConfig(BaseSettings):
    POSITION_PROVIDER_PINS: str = Field(
        description="The heads of model providers",
        default="",
    )

    POSITION_PROVIDER_INCLUDES: str = Field(
        description="The included model providers",
        default="",
    )

    POSITION_PROVIDER_EXCLUDES: str = Field(
        description="The excluded model providers",
        default="",
    )

    POSITION_TOOL_PINS: str = Field(
        description="The heads of tools",
        default="",
    )

    POSITION_TOOL_INCLUDES: str = Field(
        description="The included tools",
        default="",
    )

    POSITION_TOOL_EXCLUDES: str = Field(
        description="The excluded tools",
        default="",
    )

    @computed_field
    def POSITION_PROVIDER_PINS_LIST(self) -> list[str]:
        return [item.strip() for item in self.POSITION_PROVIDER_PINS.split(",") if item.strip() != ""]

    @computed_field
    def POSITION_PROVIDER_INCLUDES_SET(self) -> set[str]:
        return {item.strip() for item in self.POSITION_PROVIDER_INCLUDES.split(",") if item.strip() != ""}

    @computed_field
    def POSITION_PROVIDER_EXCLUDES_SET(self) -> set[str]:
        return {item.strip() for item in self.POSITION_PROVIDER_EXCLUDES.split(",") if item.strip() != ""}

    @computed_field
    def POSITION_TOOL_PINS_LIST(self) -> list[str]:
        return [item.strip() for item in self.POSITION_TOOL_PINS.split(",") if item.strip() != ""]

    @computed_field
    def POSITION_TOOL_INCLUDES_SET(self) -> set[str]:
        return {item.strip() for item in self.POSITION_TOOL_INCLUDES.split(",") if item.strip() != ""}

    @computed_field
    def POSITION_TOOL_EXCLUDES_SET(self) -> set[str]:
        return {item.strip() for item in self.POSITION_TOOL_EXCLUDES.split(",") if item.strip() != ""}


class FeatureConfig(
    # place the configs in alphabet order
    AppExecutionConfig,
    BillingConfig,
    CodeExecutionSandboxConfig,
    DataSetConfig,
    EndpointConfig,
    FileAccessConfig,
    FileUploadConfig,
    HttpConfig,
    ImageFormatConfig,
    InnerAPIConfig,
    IndexingConfig,
    LoggingConfig,
    MailConfig,
    ModelLoadBalanceConfig,
    ModerationConfig,
    OAuthConfig,
    RagEtlConfig,
    SecurityConfig,
    ToolConfig,
    UpdateConfig,
    WorkflowConfig,
    WorkspaceConfig,
    PositionConfig,
    # hosted services config
    HostedServiceConfig,
    CeleryBeatConfig,
):
    pass

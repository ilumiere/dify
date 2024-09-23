from typing import Optional

from pydantic import Field, NonNegativeInt
from pydantic_settings import BaseSettings


class HostedOpenAiConfig(BaseSettings):
    """
    托管 OpenAI 服务配置类。

    该类用于配置与托管 OpenAI 服务相关的设置，包括 API 密钥、API 基础 URL、组织信息、试用和付费功能的启用状态，以及相关模型的列表和配额限制。
    """

    HOSTED_OPENAI_API_KEY: Optional[str] = Field(
        description="托管 OpenAI 服务的 API 密钥。用于身份验证和访问 OpenAI 服务。",
        default=None,
    )

    HOSTED_OPENAI_API_BASE: Optional[str] = Field(
        description="托管 OpenAI 服务的 API 基础 URL。用于指定 OpenAI 服务的访问地址。",
        default=None,
    )

    HOSTED_OPENAI_API_ORGANIZATION: Optional[str] = Field(
        description="托管 OpenAI 服务的组织标识符。用于指定使用 OpenAI 服务的组织。",
        default=None,
    )

    HOSTED_OPENAI_TRIAL_ENABLED: bool = Field(
        description="是否启用试用功能。如果为 True，则启用试用功能；否则禁用。",
        default=False,
    )

    HOSTED_OPENAI_TRIAL_MODELS: str = Field(
        description="试用功能启用的模型列表。多个模型之间用逗号分隔。",
        default="gpt-3.5-turbo,"
        "gpt-3.5-turbo-1106,"
        "gpt-3.5-turbo-instruct,"
        "gpt-3.5-turbo-16k,"
        "gpt-3.5-turbo-16k-0613,"
        "gpt-3.5-turbo-0613,"
        "gpt-3.5-turbo-0125,"
        "text-davinci-003",
    )

    HOSTED_OPENAI_QUOTA_LIMIT: NonNegativeInt = Field(
        description="试用和付费功能的配额限制。表示用户可以使用的最大请求次数。",
        default=200,
    )

    HOSTED_OPENAI_PAID_ENABLED: bool = Field(
        description="是否启用付费功能。如果为 True，则启用付费功能；否则禁用。",
        default=False,
    )

    HOSTED_OPENAI_PAID_MODELS: str = Field(
        description="付费功能启用的模型列表。多个模型之间用逗号分隔。",
        default="gpt-4,"
        "gpt-4-turbo-preview,"
        "gpt-4-turbo-2024-04-09,"
        "gpt-4-1106-preview,"
        "gpt-4-0125-preview,"
        "gpt-3.5-turbo,"
        "gpt-3.5-turbo-16k,"
        "gpt-3.5-turbo-16k-0613,"
        "gpt-3.5-turbo-1106,"
        "gpt-3.5-turbo-0613,"
        "gpt-3.5-turbo-0125,"
        "gpt-3.5-turbo-instruct,"
        "text-davinci-003",
    )


class HostedAzureOpenAiConfig(BaseSettings):
    """
    托管 Azure OpenAI 服务配置类。

    该类用于配置与托管 Azure OpenAI 服务相关的设置，包括服务的启用状态、API 密钥、API 基础 URL 和配额限制。
    """

    HOSTED_AZURE_OPENAI_ENABLED: bool = Field(
        description="是否启用托管 Azure OpenAI 服务。如果为 True，则启用服务；否则禁用。",
        default=False,
    )

    HOSTED_AZURE_OPENAI_API_KEY: Optional[str] = Field(
        description="托管 Azure OpenAI 服务的 API 密钥。用于身份验证和访问 Azure OpenAI 服务。",
        default=None,
    )

    HOSTED_AZURE_OPENAI_API_BASE: Optional[str] = Field(
        description="托管 Azure OpenAI 服务的 API 基础 URL。用于指定 Azure OpenAI 服务的访问地址。",
        default=None,
    )

    HOSTED_AZURE_OPENAI_QUOTA_LIMIT: NonNegativeInt = Field(
        description="托管 Azure OpenAI 服务的配额限制。表示用户可以使用的最大请求次数。",
        default=200,
    )


class HostedAnthropicConfig(BaseSettings):
    """
    托管 Anthropic 服务配置类。

    该类用于配置与托管 Anthropic 服务相关的设置，包括服务的 API 基础 URL、API 密钥、试用状态、配额限制和付费状态。
    """

    HOSTED_ANTHROPIC_API_BASE: Optional[str] = Field(
        description="托管 Anthropic 服务的 API 基础 URL。用于指定 Anthropic 服务的访问地址。",
        default=None,
    )

    HOSTED_ANTHROPIC_API_KEY: Optional[str] = Field(
        description="托管 Anthropic 服务的 API 密钥。用于身份验证和访问 Anthropic 服务。",
        default=None,
    )

    HOSTED_ANTHROPIC_TRIAL_ENABLED: bool = Field(
        description="是否启用 Anthropic 服务的试用功能。如果为 True，则启用试用功能；否则禁用。",
        default=False,
    )

    HOSTED_ANTHROPIC_QUOTA_LIMIT: NonNegativeInt = Field(
        description="托管 Anthropic 服务的配额限制。表示用户可以使用的最大请求次数。",
        default=600000,
    )

    HOSTED_ANTHROPIC_PAID_ENABLED: bool = Field(
        description="是否启用 Anthropic 服务的付费功能。如果为 True，则启用付费功能；否则禁用。",
        default=False,
    )


class HostedMinmaxConfig(BaseSettings):
    """
    托管 Minmax 服务配置类。

    该类用于配置与托管 Minmax 服务相关的设置，包括服务的启用状态。
    """

    HOSTED_MINIMAX_ENABLED: bool = Field(
        description="是否启用 Minmax 服务。如果为 True，则启用 Minmax 服务；否则禁用。",
        default=False,
    )
    """
    HOSTED_MINIMAX_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用 Minmax 服务。
    - 默认值：False
    - 说明：该属性定义了 Minmax 服务的启用状态。默认值为 False，表示禁用 Minmax 服务。
    """


class HostedSparkConfig(BaseSettings):
    """
    托管 Spark 服务配置类。

    该类用于配置与托管 Spark 服务相关的设置，包括服务的启用状态。
    """

    HOSTED_SPARK_ENABLED: bool = Field(
        description="是否启用 Spark 服务。如果为 True，则启用 Spark 服务；否则禁用。",
        default=False,
    )
    """
    HOSTED_SPARK_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用 Spark 服务。
    - 默认值：False
    - 说明：该属性定义了 Spark 服务的启用状态。默认值为 False，表示禁用 Spark 服务。
    """


class HostedZhipuAIConfig(BaseSettings):
    """
    托管 ZhipuAI 服务配置类。

    该类用于配置与托管 ZhipuAI 服务相关的设置，包括服务的启用状态。
    """

    HOSTED_ZHIPUAI_ENABLED: bool = Field(
        description="是否启用 ZhipuAI 服务。如果为 True，则启用 ZhipuAI 服务；否则禁用。",
        default=False,
    )
    """
    HOSTED_ZHIPUAI_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用 ZhipuAI 服务。
    - 默认值：False
    - 说明：该属性定义了 ZhipuAI 服务的启用状态。默认值为 False，表示禁用 ZhipuAI 服务。
    """


class HostedModerationConfig(BaseSettings):
    """
    托管内容审核服务配置类。

    该类用于配置与托管内容审核服务相关的设置，包括服务的启用状态和使用的审核服务提供商。
    """

    HOSTED_MODERATION_ENABLED: bool = Field(
        description="是否启用内容审核服务。如果为 True，则启用内容审核服务；否则禁用。",
        default=False,
    )
    """
    HOSTED_MODERATION_ENABLED 属性：
    - 类型：bool
    - 描述：是否启用内容审核服务。
    - 默认值：False
    - 说明：该属性定义了内容审核服务的启用状态。默认值为 False，表示禁用内容审核服务。
    """

    HOSTED_MODERATION_PROVIDERS: str = Field(
        description="内容审核服务的提供商列表。多个提供商之间用逗号分隔。",
        default="",
    )
    """
    HOSTED_MODERATION_PROVIDERS 属性：
    - 类型：str
    - 描述：内容审核服务的提供商列表。
    - 默认值：空字符串
    - 说明：该属性定义了内容审核服务的提供商。默认值为空字符串，表示未指定任何提供商。
    """


class HostedFetchAppTemplateConfig(BaseSettings):
    """
    托管获取应用模板配置类。

    该类用于配置与获取应用模板相关的设置，包括获取模式和远程域名。
    """

    HOSTED_FETCH_APP_TEMPLATES_MODE: str = Field(
        description="获取应用模板的模式，默认值为 'remote'，可选值包括 'remote', 'db', 'builtin'。",
        default="remote",
    )
    """
    HOSTED_FETCH_APP_TEMPLATES_MODE 属性：
    - 类型：str
    - 描述：获取应用模板的模式。
    - 默认值："remote"
    - 说明：该属性定义了获取应用模板的方式。默认值为 "remote"，表示从远程服务器获取模板。可选值包括：
      - "remote": 从远程服务器获取模板。
      - "db": 从数据库获取模板。
      - "builtin": 使用内置模板。
    """

    HOSTED_FETCH_APP_TEMPLATES_REMOTE_DOMAIN: str = Field(
        description="获取远程应用模板的域名。",
        default="https://tmpl.dify.ai",
    )
    """
    HOSTED_FETCH_APP_TEMPLATES_REMOTE_DOMAIN 属性：
    - 类型：str
    - 描述：获取远程应用模板的域名。
    - 默认值："https://tmpl.dify.ai"
    - 说明：该属性定义了获取远程应用模板时使用的域名。默认值为 "https://tmpl.dify.ai"，表示从该域名获取模板。
    """


class HostedServiceConfig(
    # place the configs in alphabet order
    HostedAnthropicConfig,
    HostedAzureOpenAiConfig,
    HostedFetchAppTemplateConfig,
    HostedMinmaxConfig,
    HostedOpenAiConfig,
    HostedSparkConfig,
    HostedZhipuAIConfig,
    # moderation
    HostedModerationConfig,
):
    pass

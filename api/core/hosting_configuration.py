from typing import Optional

from flask import Config, Flask
from pydantic import BaseModel

from core.entities.provider_entities import QuotaUnit, RestrictModel
from core.model_runtime.entities.model_entities import ModelType
from models.provider import ProviderQuotaType


class HostingQuota(BaseModel):
    """
    托管配额类，用于定义托管提供者的配额信息。

    属性:
        quota_type (ProviderQuotaType): 配额类型，表示托管提供者的配额类型。
        restrict_models (list[RestrictModel]): 受限制的模型列表，默认为空列表。
    """
    quota_type: ProviderQuotaType
    restrict_models: list[RestrictModel] = []


class TrialHostingQuota(HostingQuota):
    """
    试用托管配额类，继承自 HostingQuota，用于定义试用托管提供者的配额信息。

    属性:
        quota_type (ProviderQuotaType): 配额类型，默认为 ProviderQuotaType.TRIAL。
        quota_limit (int): 配额限制，默认为 0。-1 表示无限制。
    """
    quota_type: ProviderQuotaType = ProviderQuotaType.TRIAL
    quota_limit: int = 0
    """Quota limit for the hosting provider models. -1 means unlimited."""


class PaidHostingQuota(HostingQuota):
    """
    付费托管配额类，继承自 HostingQuota，用于定义付费托管提供者的配额信息。

    属性:
        quota_type (ProviderQuotaType): 配额类型，默认为 ProviderQuotaType.PAID。
    """
    quota_type: ProviderQuotaType = ProviderQuotaType.PAID


class FreeHostingQuota(HostingQuota):
    """
    免费托管配额类，继承自 HostingQuota，用于定义免费托管提供者的配额信息。

    属性:
        quota_type (ProviderQuotaType): 配额类型，默认为 ProviderQuotaType.FREE。
    """
    quota_type: ProviderQuotaType = ProviderQuotaType.FREE


class HostingProvider(BaseModel):
    """
    托管提供者类，用于定义托管提供者的配置信息。

    属性:
        enabled (bool): 是否启用该托管提供者，默认为 False。
        credentials (Optional[dict]): 托管提供者的凭证信息，默认为 None。
        quota_unit (Optional[QuotaUnit]): 配额单位，默认为 None。
        quotas (list[HostingQuota]): 托管提供者的配额列表，默认为空列表。
    """
    enabled: bool = False
    credentials: Optional[dict] = None
    quota_unit: Optional[QuotaUnit] = None
    quotas: list[HostingQuota] = []


class HostedModerationConfig(BaseModel):
    """
    托管内容审核配置类，用于定义托管内容审核的配置信息。

    属性:
        enabled (bool): 是否启用内容审核，默认为 False。
        providers (list[str]): 内容审核的提供者列表，默认为空列表。
    """
    enabled: bool = False
    providers: list[str] = []


class HostingConfiguration:
    """
    该类用于管理托管配置，包括不同托管提供者的配置和内容审核配置。

    属性:
        provider_map (dict[str, HostingProvider]): 存储不同托管提供者的配置信息。
        moderation_config (HostedModerationConfig): 存储内容审核配置信息。
    """

    provider_map: dict[str, HostingProvider] = {}
    moderation_config: HostedModerationConfig = None

    def init_app(self, app: Flask) -> None:
        """
        初始化 Flask 应用的托管配置。

        参数:
            app (Flask): Flask 应用实例。

        逻辑:
            1. 获取应用配置。
            2. 如果应用版本不是 "CLOUD"，则直接返回。
            3. 初始化各个托管提供者的配置，并存储在 provider_map 中。
            4. 初始化内容审核配置，并存储在 moderation_config 中。
        """
        config = app.config

        if config.get("EDITION") != "CLOUD":
            return

        self.provider_map["azure_openai"] = self.init_azure_openai(config)
        self.provider_map["openai"] = self.init_openai(config)
        self.provider_map["anthropic"] = self.init_anthropic(config)
        self.provider_map["minimax"] = self.init_minimax(config)
        self.provider_map["spark"] = self.init_spark(config)
        self.provider_map["zhipuai"] = self.init_zhipuai(config)

        self.moderation_config = self.init_moderation_config(config)
    @staticmethod
    def init_azure_openai(app_config: Config) -> HostingProvider:
        """
        初始化 Azure OpenAI 托管提供者的配置。

        该函数用于根据 Flask 应用的配置初始化 Azure OpenAI 托管提供者的配置。

        参数:
            app_config (Config): Flask 应用配置对象，包含所有必要的配置信息。

        逻辑:
            1. 设置配额单位为 "TIMES"，表示配额以使用次数为单位。
            2. 检查是否启用了 Azure OpenAI 托管。
            3. 如果启用了 Azure OpenAI 托管，则配置凭证和配额。
            4. 返回配置好的 HostingProvider 对象。

        返回值:
            HostingProvider: 配置好的 Azure OpenAI 托管提供者对象，包含是否启用、凭证、配额单位和配额信息。
        """
        # 设置配额单位为 "TIMES"
        quota_unit = QuotaUnit.TIMES

        # 检查是否启用了 Azure OpenAI 托管
        if app_config.get("HOSTED_AZURE_OPENAI_ENABLED"):
            # 配置凭证信息，包括 API 密钥、API 基础地址和基础模型名称
            credentials = {
                "openai_api_key": app_config.get("HOSTED_AZURE_OPENAI_API_KEY"),
                "openai_api_base": app_config.get("HOSTED_AZURE_OPENAI_API_BASE"),
                "base_model_name": "gpt-35-turbo",
            }

            # 初始化配额列表
            quotas = []

            # 获取托管配额限制，默认值为 1000
            hosted_quota_limit = int(app_config.get("HOSTED_AZURE_OPENAI_QUOTA_LIMIT", "1000"))

            # 配置试用配额，包括配额限制和受限模型列表
            trial_quota = TrialHostingQuota(
                quota_limit=hosted_quota_limit,
                restrict_models=[
                    RestrictModel(model="gpt-4", base_model_name="gpt-4", model_type=ModelType.LLM),
                    RestrictModel(model="gpt-4o", base_model_name="gpt-4o", model_type=ModelType.LLM),
                    RestrictModel(model="gpt-4o-mini", base_model_name="gpt-4o-mini", model_type=ModelType.LLM),
                    RestrictModel(model="gpt-4-32k", base_model_name="gpt-4-32k", model_type=ModelType.LLM),
                    RestrictModel(
                        model="gpt-4-1106-preview", base_model_name="gpt-4-1106-preview", model_type=ModelType.LLM
                    ),
                    RestrictModel(
                        model="gpt-4-vision-preview", base_model_name="gpt-4-vision-preview", model_type=ModelType.LLM
                    ),
                    RestrictModel(model="gpt-35-turbo", base_model_name="gpt-35-turbo", model_type=ModelType.LLM),
                    RestrictModel(
                        model="gpt-35-turbo-1106", base_model_name="gpt-35-turbo-1106", model_type=ModelType.LLM
                    ),
                    RestrictModel(
                        model="gpt-35-turbo-instruct", base_model_name="gpt-35-turbo-instruct", model_type=ModelType.LLM
                    ),
                    RestrictModel(
                        model="gpt-35-turbo-16k", base_model_name="gpt-35-turbo-16k", model_type=ModelType.LLM
                    ),
                    RestrictModel(
                        model="text-davinci-003", base_model_name="text-davinci-003", model_type=ModelType.LLM
                    ),
                    RestrictModel(
                        model="text-embedding-ada-002",
                        base_model_name="text-embedding-ada-002",
                        model_type=ModelType.TEXT_EMBEDDING,
                    ),
                    RestrictModel(
                        model="text-embedding-3-small",
                        base_model_name="text-embedding-3-small",
                        model_type=ModelType.TEXT_EMBEDDING,
                    ),
                    RestrictModel(
                        model="text-embedding-3-large",
                        base_model_name="text-embedding-3-large",
                        model_type=ModelType.TEXT_EMBEDDING,
                    ),
                ],
            )
            # 将试用配额添加到配额列表中
            quotas.append(trial_quota)

            # 返回启用的 HostingProvider 对象，包含凭证、配额单位和配额信息
            return HostingProvider(enabled=True, credentials=credentials, quota_unit=quota_unit, quotas=quotas)

        # 如果未启用 Azure OpenAI 托管，返回未启用的 HostingProvider 对象，仅包含配额单位
        return HostingProvider(
            enabled=False,
            quota_unit=quota_unit,
        )

    def init_openai(self, app_config: Config) -> HostingProvider:
        """
        初始化 OpenAI 托管提供者的配置。

        该函数的主要用途是根据 Flask 应用配置对象初始化 OpenAI 托管提供者的配置，包括配额单位、试用和付费配额，并返回配置好的 HostingProvider 对象。

        参数:
            app_config (Config): Flask 应用配置对象，包含 OpenAI 托管提供者的相关配置信息。

        逻辑:
            1. 设置配额单位为 "CREDITS"。
            2. 根据配置初始化试用和付费配额。
            3. 如果存在配额，则初始化凭证信息。
            4. 返回配置好的 HostingProvider 对象。

        返回值:
            HostingProvider: 配置好的 OpenAI 托管提供者对象，包含是否启用、凭证信息、配额单位和配额信息。
        """
        # 设置配额单位为 "CREDITS"
        quota_unit = QuotaUnit.CREDITS
        quotas = []

        # 如果启用了试用配额，则初始化试用配额
        if app_config.get("HOSTED_OPENAI_TRIAL_ENABLED"):
            # 获取试用配额限制，默认值为 200
            hosted_quota_limit = int(app_config.get("HOSTED_OPENAI_QUOTA_LIMIT", "200"))
            # 解析试用配额限制的模型
            trial_models = self.parse_restrict_models_from_env(app_config, "HOSTED_OPENAI_TRIAL_MODELS")
            # 创建试用配额对象
            trial_quota = TrialHostingQuota(quota_limit=hosted_quota_limit, restrict_models=trial_models)
            # 将试用配额添加到配额列表中
            quotas.append(trial_quota)

        # 如果启用了付费配额，则初始化付费配额
        if app_config.get("HOSTED_OPENAI_PAID_ENABLED"):
            # 解析付费配额限制的模型
            paid_models = self.parse_restrict_models_from_env(app_config, "HOSTED_OPENAI_PAID_MODELS")
            # 创建付费配额对象
            paid_quota = PaidHostingQuota(restrict_models=paid_models)
            # 将付费配额添加到配额列表中
            quotas.append(paid_quota)

        # 如果存在配额，则初始化凭证信息
        if len(quotas) > 0:
            credentials = {
                "openai_api_key": app_config.get("HOSTED_OPENAI_API_KEY"),
            }

            # 如果配置了 OpenAI API 基础 URL，则添加到凭证信息中
            if app_config.get("HOSTED_OPENAI_API_BASE"):
                credentials["openai_api_base"] = app_config.get("HOSTED_OPENAI_API_BASE")

            # 如果配置了 OpenAI API 组织信息，则添加到凭证信息中
            if app_config.get("HOSTED_OPENAI_API_ORGANIZATION"):
                credentials["openai_organization"] = app_config.get("HOSTED_OPENAI_API_ORGANIZATION")

            # 返回启用的 HostingProvider 对象，包含凭证、配额单位和配额信息
            return HostingProvider(enabled=True, credentials=credentials, quota_unit=quota_unit, quotas=quotas)

        # 如果未启用 OpenAI 托管，返回未启用的 HostingProvider 对象，仅包含配额单位
        return HostingProvider(
            enabled=False,
            quota_unit=quota_unit,
        )

    @staticmethod
    def init_anthropic(app_config: Config) -> HostingProvider:
        """
        初始化 Anthropic 托管提供者的配置。

        参数:
            app_config (Config): Flask 应用配置对象，包含所有配置信息。

        逻辑:
            1. 设置配额单位为 "TOKENS"。
            2. 根据配置初始化试用和付费配额。
            3. 如果存在配额，初始化凭证信息并返回启用的 HostingProvider 对象。
            4. 如果未启用任何配额，返回未启用的 HostingProvider 对象。

        返回值:
            HostingProvider: 配置好的 Anthropic 托管提供者对象，包含是否启用、凭证信息、配额单位和配额信息。
        """
        # 设置配额单位为 "TOKENS"
        quota_unit = QuotaUnit.TOKENS
        quotas = []

        # 如果启用了试用配额，则初始化试用配额
        if app_config.get("HOSTED_ANTHROPIC_TRIAL_ENABLED"):
            # 获取试用配额限制，默认值为 0
            hosted_quota_limit = int(app_config.get("HOSTED_ANTHROPIC_QUOTA_LIMIT", "0"))
            # 创建试用配额对象
            trial_quota = TrialHostingQuota(quota_limit=hosted_quota_limit)
            # 将试用配额添加到配额列表中
            quotas.append(trial_quota)

        # 如果启用了付费配额，则初始化付费配额
        if app_config.get("HOSTED_ANTHROPIC_PAID_ENABLED"):
            # 创建付费配额对象
            paid_quota = PaidHostingQuota()
            # 将付费配额添加到配额列表中
            quotas.append(paid_quota)

        # 如果存在配额，则初始化凭证信息
        if len(quotas) > 0:
            credentials = {
                "anthropic_api_key": app_config.get("HOSTED_ANTHROPIC_API_KEY"),
            }

            # 如果配置了 Anthropic API 基础 URL，则添加到凭证信息中
            if app_config.get("HOSTED_ANTHROPIC_API_BASE"):
                credentials["anthropic_api_url"] = app_config.get("HOSTED_ANTHROPIC_API_BASE")

            # 返回启用的 HostingProvider 对象，包含凭证、配额单位和配额信息
            return HostingProvider(enabled=True, credentials=credentials, quota_unit=quota_unit, quotas=quotas)

        # 如果未启用 Anthropic 托管，返回未启用的 HostingProvider 对象，仅包含配额单位
        return HostingProvider(
            enabled=False,
            quota_unit=quota_unit,
        )

    @staticmethod
    def init_minimax(app_config: Config) -> HostingProvider:
        """
        初始化 Minimax 托管提供者的配置。

        参数:
            app_config (Config): Flask 应用配置对象。

        逻辑:
            1. 设置配额单位为 "TOKENS"。
            2. 检查是否启用了 Minimax 托管。
            3. 如果启用，创建一个包含免费配额的列表。
            4. 返回配置好的 HostingProvider 对象，启用状态为 True，配额单位为 "TOKENS"，配额列表包含免费配额。
            5. 如果未启用，返回配置好的 HostingProvider 对象，启用状态为 False，配额单位为 "TOKENS"。

        返回值:
            HostingProvider: 配置好的 Minimax 托管提供者对象。
        """
        quota_unit = QuotaUnit.TOKENS  # 设置配额单位为 "TOKENS"
        if app_config.get("HOSTED_MINIMAX_ENABLED"):  # 检查是否启用了 Minimax 托管
            quotas = [FreeHostingQuota()]  # 创建一个包含免费配额的列表

            return HostingProvider(
                enabled=True,  # 启用状态为 True
                credentials=None,  # 使用提供者的凭证
                quota_unit=quota_unit,  # 配额单位为 "TOKENS"
                quotas=quotas,  # 配额列表包含免费配额
            )

        return HostingProvider(
            enabled=False,  # 启用状态为 False
            quota_unit=quota_unit,  # 配额单位为 "TOKENS"
        )
    @staticmethod
    def init_spark(app_config: Config) -> HostingProvider:
        """
        初始化 Spark 托管提供者的配置。

        参数:
            app_config (Config): Flask 应用配置对象。

        逻辑:
            1. 设置配额单位为 "TOKENS"。
            2. 检查是否启用了 Spark 托管。
            3. 如果启用，创建一个包含免费配额的列表。
            4. 返回配置好的 HostingProvider 对象，启用状态为 True，配额单位为 "TOKENS"，配额列表包含免费配额。
            5. 如果未启用，返回配置好的 HostingProvider 对象，启用状态为 False，配额单位为 "TOKENS"。

        返回值:
            HostingProvider: 配置好的 Spark 托管提供者对象。
        """
        quota_unit = QuotaUnit.TOKENS  # 设置配额单位为 "TOKENS"
        if app_config.get("HOSTED_SPARK_ENABLED"):  # 检查是否启用了 Spark 托管
            quotas = [FreeHostingQuota()]  # 创建一个包含免费配额的列表

            return HostingProvider(
                enabled=True,  # 启用状态为 True
                credentials=None,  # 使用提供者的凭证
                quota_unit=quota_unit,  # 配额单位为 "TOKENS"
                quotas=quotas,  # 配额列表包含免费配额
            )

        return HostingProvider(
            enabled=False,  # 启用状态为 False
            quota_unit=quota_unit,  # 配额单位为 "TOKENS"
        )
    @staticmethod
    def init_zhipuai(app_config: Config) -> HostingProvider:
        """
        初始化 ZhipuAI 托管提供者的配置。

        参数:
            app_config (Config): Flask 应用配置对象。

        逻辑:
            1. 设置配额单位为 "TOKENS"。
            2. 检查是否启用了 ZhipuAI 托管。
            3. 如果启用，创建一个包含免费配额的列表。
            4. 返回配置好的 HostingProvider 对象，启用状态为 True，配额单位为 "TOKENS"，配额列表包含免费配额。
            5. 如果未启用，返回配置好的 HostingProvider 对象，启用状态为 False，配额单位为 "TOKENS"。

        返回值:
            HostingProvider: 配置好的 ZhipuAI 托管提供者对象。
        """
        quota_unit = QuotaUnit.TOKENS  # 设置配额单位为 "TOKENS"
        if app_config.get("HOSTED_ZHIPUAI_ENABLED"):  # 检查是否启用了 ZhipuAI 托管
            quotas = [FreeHostingQuota()]  # 创建一个包含免费配额的列表

            return HostingProvider(
                enabled=True,  # 启用状态为 True
                credentials=None,  # 使用提供者的凭证
                quota_unit=quota_unit,  # 配额单位为 "TOKENS"
                quotas=quotas,  # 配额列表包含免费配额
            )

        return HostingProvider(
            enabled=False,  # 启用状态为 False
            quota_unit=quota_unit,  # 配额单位为 "TOKENS"
        )

    @staticmethod
    def init_moderation_config(app_config: Config) -> HostedModerationConfig:
        """
        初始化托管内容审核配置。

        参数:
            app_config (Config): Flask 应用配置对象。

        功能:
            1. 检查是否启用了托管内容审核功能。
            2. 如果启用了托管内容审核功能并且提供了审核提供者列表，则返回一个启用的 HostedModerationConfig 对象，包含提供的审核提供者列表。
            3. 如果未启用托管内容审核功能或未提供审核提供者列表，则返回一个未启用的 HostedModerationConfig 对象。

        返回值:
            HostedModerationConfig: 配置好的托管内容审核配置对象。
        """
        # 检查是否启用了托管内容审核功能，并且是否提供了审核提供者列表
        if app_config.get("HOSTED_MODERATION_ENABLED") and app_config.get("HOSTED_MODERATION_PROVIDERS"):
            # 返回一个启用的 HostedModerationConfig 对象，包含提供的审核提供者列表
            return HostedModerationConfig(
                enabled=True,  # 启用状态为 True
                providers=app_config.get("HOSTED_MODERATION_PROVIDERS").split(",")  # 将提供的审核提供者列表按逗号分割
            )

        # 返回一个未启用的 HostedModerationConfig 对象
        return HostedModerationConfig(enabled=False)

    @staticmethod
    def parse_restrict_models_from_env(app_config: Config, env_var: str) -> list[RestrictModel]:
        """
        从环境变量中解析受限模型列表。

        参数:
            app_config (Config): Flask 应用配置对象，用于获取环境变量。
            env_var (str): 环境变量的名称，包含受限模型的字符串列表。

        功能:
            1. 从 app_config 中获取指定环境变量的值。
            2. 如果环境变量存在，将其值按逗号分割成模型名称列表。
            3. 过滤掉空字符串，并创建 RestrictModel 对象列表。
            4. 返回包含 RestrictModel 对象的列表。

        返回值:
            list[RestrictModel]: 包含 RestrictModel 对象的列表，每个对象表示一个受限模型。
        """
        models_str = app_config.get(env_var)  # 从 app_config 中获取指定环境变量的值
        models_list = models_str.split(",") if models_str else []  # 如果环境变量存在，将其值按逗号分割成模型名称列表，否则返回空列表
        return [
            RestrictModel(model=model_name.strip(), model_type=ModelType.LLM)  # 创建 RestrictModel 对象，模型类型为 LLM
            for model_name in models_list  # 遍历模型名称列表
            if model_name.strip()  # 过滤掉空字符串
        ]

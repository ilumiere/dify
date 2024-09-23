from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from core.model_runtime.entities.common_entities import I18nObject


class ModelType(Enum):
    """
    模型类型的枚举类。

    该类定义了不同类型的模型，并为每个模型类型提供了枚举值。
    每个枚举值代表一种特定的模型类型，例如语言模型（LLM）、文本嵌入模型（TEXT_EMBEDDING）等。
    """

    LLM = "llm"
    TEXT_EMBEDDING = "text-embedding"
    RERANK = "rerank"
    SPEECH2TEXT = "speech2text"
    MODERATION = "moderation"
    TTS = "tts"
    TEXT2IMG = "text2img"

    @classmethod
    def value_of(cls, origin_model_type: str) -> "ModelType":
        """
        根据原始模型类型获取对应的模型类型枚举值。

        该方法接收一个字符串参数 `origin_model_type`，并返回对应的 `ModelType` 枚举值。
        如果传入的 `origin_model_type` 无效，则抛出 `ValueError` 异常。

        :param origin_model_type: 原始模型类型的字符串表示
        :return: 对应的 `ModelType` 枚举值
        :raises ValueError: 如果 `origin_model_type` 无效
        """
        if origin_model_type in {"text-generation", cls.LLM.value}:
            return cls.LLM
        elif origin_model_type in {"embeddings", cls.TEXT_EMBEDDING.value}:
            return cls.TEXT_EMBEDDING
        elif origin_model_type in {"reranking", cls.RERANK.value}:
            return cls.RERANK
        elif origin_model_type in {"speech2text", cls.SPEECH2TEXT.value}:
            return cls.SPEECH2TEXT
        elif origin_model_type in {"tts", cls.TTS.value}:
            return cls.TTS
        elif origin_model_type in {"text2img", cls.TEXT2IMG.value}:
            return cls.TEXT2IMG
        elif origin_model_type == cls.MODERATION.value:
            return cls.MODERATION
        else:
            raise ValueError(f"invalid origin model type {origin_model_type}")

    def to_origin_model_type(self) -> str:
        """
        根据模型类型枚举值获取对应的原始模型类型字符串。

        该方法返回与当前 `ModelType` 枚举值对应的原始模型类型字符串。
        如果当前枚举值无效，则抛出 `ValueError` 异常。

        :return: 对应的原始模型类型字符串
        :raises ValueError: 如果当前枚举值无效
        """
        if self == self.LLM:
            return "text-generation"
        elif self == self.TEXT_EMBEDDING:
            return "embeddings"
        elif self == self.RERANK:
            return "reranking"
        elif self == self.SPEECH2TEXT:
            return "speech2text"
        elif self == self.TTS:
            return "tts"
        elif self == self.MODERATION:
            return "moderation"
        elif self == self.TEXT2IMG:
            return "text2img"
        else:
            raise ValueError(f"invalid model type {self}")


class FetchFrom(Enum):
    """
    Enum class for fetch from.
    """

    PREDEFINED_MODEL = "predefined-model"
    CUSTOMIZABLE_MODEL = "customizable-model"


class ModelFeature(Enum):
    """
    模型功能的枚举类。

    该类定义了不同的大型语言模型（LLM）功能，每个功能对应一个特定的字符串值。

    属性:
    - TOOL_CALL: 表示工具调用功能。
    - MULTI_TOOL_CALL: 表示多工具调用功能。
    - AGENT_THOUGHT: 表示代理思维功能。
    - VISION: 表示视觉功能。
    - STREAM_TOOL_CALL: 表示流式工具调用功能。

    主要用途：用于表示和管理大型语言模型的功能，便于在代码中进行功能判断和处理。
    """

    TOOL_CALL = "tool-call"  # 工具调用功能
    MULTI_TOOL_CALL = "multi-tool-call"  # 多工具调用功能
    AGENT_THOUGHT = "agent-thought"  # 代理思维功能
    VISION = "vision"  # 视觉功能
    STREAM_TOOL_CALL = "stream-tool-call"  # 流式工具调用功能


class DefaultParameterName(str, Enum):
    """
    参数模板变量的枚举类。

    该类定义了不同参数的名称，每个参数名称对应一个特定的字符串值。

    属性:
    - TEMPERATURE: 表示温度参数，用于控制生成文本的随机性。
    - TOP_P: 表示Top P参数，用于控制生成文本的多样性。
    - TOP_K: 表示Top K参数，用于控制生成文本的选择范围。
    - PRESENCE_PENALTY: 表示存在惩罚参数，用于减少重复出现的词汇。
    - FREQUENCY_PENALTY: 表示频率惩罚参数，用于减少高频词汇的出现。
    - MAX_TOKENS: 表示最大令牌数参数，用于限制生成文本的长度。
    - RESPONSE_FORMAT: 表示响应格式参数，用于指定生成文本的格式。
    - JSON_SCHEMA: 表示JSON模式参数，用于定义JSON数据的结构。

    主要用途：用于表示和管理参数模板中的变量名称，便于在代码中进行参数名称的匹配和处理。
    """

    TEMPERATURE = "temperature"  # 温度参数
    TOP_P = "top_p"  # Top P参数
    TOP_K = "top_k"  # Top K参数
    PRESENCE_PENALTY = "presence_penalty"  # 存在惩罚参数
    FREQUENCY_PENALTY = "frequency_penalty"  # 频率惩罚参数
    MAX_TOKENS = "max_tokens"  # 最大令牌数参数
    RESPONSE_FORMAT = "response_format"  # 响应格式参数
    JSON_SCHEMA = "json_schema"  # JSON模式参数

    @classmethod
    def value_of(cls, value: Any) -> "DefaultParameterName":
        """
        根据值获取参数名称。

        该方法用于根据传入的值查找对应的参数名称。

        参数:
        - value: 要查找的参数值。

        返回值:
        - DefaultParameterName: 匹配的参数名称。

        异常:
        - ValueError: 如果没有找到匹配的参数名称，则抛出此异常。
        """
        for name in cls:  # 遍历枚举成员
            if name.value == value:  # 检查当前成员的值是否与传入的值匹配
                return name  # 返回匹配的参数名称
        raise ValueError(f"invalid parameter name {value}")  # 如果没有匹配的成员，抛出异常


class ParameterType(Enum):
    """
    参数类型的枚举类。

    该类定义了不同参数类型的名称，每个参数类型对应一个特定的字符串值。

    属性:
    - FLOAT: 表示浮点数类型，用于表示小数。
    - INT: 表示整数类型，用于表示整数值。
    - STRING: 表示字符串类型，用于表示文本数据。
    - BOOLEAN: 表示布尔类型，用于表示真或假。
    - TEXT: 表示文本类型，用于表示长文本数据。

    主要用途：用于表示和管理参数模板中的变量类型，便于在代码中进行参数类型的匹配和处理。
    """

    FLOAT = "float"  # 浮点数类型
    INT = "int"  # 整数类型
    STRING = "string"  # 字符串类型
    BOOLEAN = "boolean"  # 布尔类型
    TEXT = "text"  # 文本类型


class ModelPropertyKey(Enum):
    """
    模型属性键的枚举类。

    该类定义了模型属性的键，每个键对应一个特定的字符串值。这些键用于标识模型属性的不同方面，如模式、上下文大小、文件上传限制等。

    属性:
    - MODE: 表示模型的模式，类型为字符串。
    - CONTEXT_SIZE: 表示模型的上下文大小，类型为字符串。
    - MAX_CHUNKS: 表示模型的最大块数，类型为字符串。
    - FILE_UPLOAD_LIMIT: 表示模型的文件上传限制，类型为字符串。
    - SUPPORTED_FILE_EXTENSIONS: 表示模型支持的文件扩展名，类型为字符串。
    - MAX_CHARACTERS_PER_CHUNK: 表示每个块的最大字符数，类型为字符串。
    - DEFAULT_VOICE: 表示模型的默认语音，类型为字符串。
    - VOICES: 表示模型的语音列表，类型为字符串。
    - WORD_LIMIT: 表示模型的字数限制，类型为字符串。
    - AUDIO_TYPE: 表示模型的音频类型，类型为字符串。
    - MAX_WORKERS: 表示模型的最大工作线程数，类型为字符串。

    主要用途：用于表示和管理模型属性的键，便于在代码中进行属性键的匹配和处理。
    """

    MODE = "mode"  # 模型的模式
    CONTEXT_SIZE = "context_size"  # 模型的上下文大小
    MAX_CHUNKS = "max_chunks"  # 模型的最大块数
    FILE_UPLOAD_LIMIT = "file_upload_limit"  # 模型的文件上传限制
    SUPPORTED_FILE_EXTENSIONS = "supported_file_extensions"  # 模型支持的文件扩展名
    MAX_CHARACTERS_PER_CHUNK = "max_characters_per_chunk"  # 每个块的最大字符数
    DEFAULT_VOICE = "default_voice"  # 模型的默认语音
    VOICES = "voices"  # 模型的语音列表
    WORD_LIMIT = "word_limit"  # 模型的字数限制
    AUDIO_TYPE = "audio_type"  # 模型的音频类型
    MAX_WORKERS = "max_workers"  # 模型的最大工作线程数


class ProviderModel(BaseModel):
    """
    提供者模型的模型类。

    该类用于表示和管理提供者模型的相关信息。它继承自 `BaseModel`，并包含多个属性，每个属性都有特定的用途和类型。

    属性:
    - model: 表示模型的名称，类型为字符串。
    - label: 表示模型的标签，类型为 `I18nObject`，用于国际化显示。
    - model_type: 表示模型的类型，类型为 `ModelType`，用于区分不同类型的模型。
    - features: 表示模型的特性列表，类型为 `Optional[list[ModelFeature]]`，可选属性，默认为 `None`。
    - fetch_from: 表示模型数据的获取来源，类型为 `FetchFrom`。
    - model_properties: 表示模型的属性字典，类型为 `dict[ModelPropertyKey, Any]`，键为 `ModelPropertyKey` 枚举类型，值为任意类型。
    - deprecated: 表示模型是否已弃用，类型为布尔值，默认为 `False`。
    - model_config: 表示模型的配置，类型为 `ConfigDict`，包含受保护的命名空间。

    主要用途：用于表示和管理提供者模型的相关信息，便于在代码中进行模型信息的匹配和处理。
    """

    model: str  # 模型的名称
    label: I18nObject  # 模型的标签，用于国际化显示
    model_type: ModelType  # 模型的类型，用于区分不同类型的模型
    features: Optional[list[ModelFeature]] = None  # 模型的特性列表，可选属性，默认为 None
    fetch_from: FetchFrom  # 模型数据的获取来源
    model_properties: dict[ModelPropertyKey, Any]  # 模型的属性字典，键为 ModelPropertyKey 枚举类型，值为任意类型
    deprecated: bool = False  # 表示模型是否已弃用，默认为 False
    model_config = ConfigDict(protected_namespaces=())  # 模型的配置，包含受保护的命名空间


class ParameterRule(BaseModel):
    """
    参数规则的模型类。

    该类用于定义和管理参数规则的相关信息。它继承自 `BaseModel`，并包含多个属性，每个属性都有特定的用途和类型。

    属性:
    - name: 参数的名称，类型为字符串。
    - use_template: 参数使用的模板，类型为可选字符串，默认为 `None`。
    - label: 参数的标签，类型为 `I18nObject`，用于国际化显示。
    - type: 参数的类型，类型为 `ParameterType`，用于区分不同类型的参数。
    - help: 参数的帮助信息，类型为可选的 `I18nObject`，默认为 `None`。
    - required: 参数是否为必填项，类型为布尔值，默认为 `False`。
    - default: 参数的默认值，类型为可选的任意类型，默认为 `None`。
    - min: 参数的最小值，类型为可选的浮点数，默认为 `None`。
    - max: 参数的最大值，类型为可选的浮点数，默认为 `None`。
    - precision: 参数的精度，类型为可选的整数，默认为 `None`。
    - options: 参数的可选值列表，类型为字符串列表，默认为空列表。

    主要用途：用于定义和管理参数规则的相关信息，便于在代码中进行参数规则的匹配和处理。
    """

    name: str  # 参数的名称
    use_template: Optional[str] = None  # 参数使用的模板，默认为 None
    label: I18nObject  # 参数的标签，用于国际化显示
    type: ParameterType  # 参数的类型，用于区分不同类型的参数
    help: Optional[I18nObject] = None  # 参数的帮助信息，默认为 None
    required: bool = False  # 参数是否为必填项，默认为 False
    default: Optional[Any] = None  # 参数的默认值，默认为 None
    min: Optional[float] = None  # 参数的最小值，默认为 None
    max: Optional[float] = None  # 参数的最大值，默认为 None
    precision: Optional[int] = None  # 参数的精度，默认为 None
    options: list[str] = []  # 参数的可选值列表，默认为空列表


class PriceConfig(BaseModel):
    """
    价格配置的模型类。

    该类用于定义和管理价格信息的相关属性。它继承自 `BaseModel`，并包含多个属性，每个属性都有特定的用途和类型。

    属性:
    - input: 输入价格，类型为 `Decimal`，表示输入的价格。
    - output: 输出价格，类型为可选的 `Decimal`，默认为 `None`，表示输出的价格。
    - unit: 单位价格，类型为 `Decimal`，表示每个单位的价格。
    - currency: 货币类型，类型为字符串，表示使用的货币类型。

    主要用途：用于定义和管理价格信息的相关属性，便于在代码中进行价格信息的匹配和处理。
    """

    input: Decimal  # 输入价格，类型为 `Decimal`，表示输入的价格
    output: Optional[Decimal] = None  # 输出价格，类型为可选的 `Decimal`，默认为 `None`，表示输出的价格
    unit: Decimal  # 单位价格，类型为 `Decimal`，表示每个单位的价格
    currency: str  # 货币类型，类型为字符串，表示使用的货币类型



class AIModelEntity(ProviderModel):
    """
    AI模型实体类。

    该类用于表示一个AI模型的实体，包含模型的参数规则和价格配置。它继承自 `ProviderModel`，并包含两个主要属性。

    属性:
    - parameter_rules: 参数规则列表，类型为 `list[ParameterRule]`，默认为空列表。该属性用于存储模型的参数规则，每个规则定义了参数的名称、类型、默认值等信息。
    - pricing: 价格配置，类型为可选的 `PriceConfig`，默认为 `None`。该属性用于存储模型的价格信息，包括输入价格、输出价格、单位价格和货币类型。

    主要用途：用于定义和管理AI模型的参数规则和价格配置，便于在代码中进行模型参数和价格的匹配和处理。
    """

    parameter_rules: list[ParameterRule] = []  # 参数规则列表，默认为空列表
    pricing: Optional[PriceConfig] = None  # 价格配置，默认为 None


class ModelUsage(BaseModel):
    pass


class PriceType(Enum):
    """
    价格类型的枚举类。

    该类用于定义和管理价格类型的枚举值。每个枚举值代表一种价格类型，便于在代码中进行价格类型的匹配和处理。

    枚举值:
    - INPUT: 输入价格类型，值为 "input"，表示输入的价格类型。
    - OUTPUT: 输出价格类型，值为 "output"，表示输出的价格类型。

    主要用途：用于定义和管理价格类型的枚举值，便于在代码中进行价格类型的匹配和处理。
    """

    INPUT = "input"  # 输入价格类型，值为 "input"，表示输入的价格类型
    OUTPUT = "output"  # 输出价格类型，值为 "output"，表示输出的价格类型


class PriceInfo(BaseModel):
    """
    价格信息模型类。

    该类用于表示和管理价格信息的相关属性。它继承自 `BaseModel`，并包含四个主要属性。

    属性:
    - unit_price: 单位价格，类型为 `Decimal`，表示每个单位的价格。
    - unit: 单位数量，类型为 `Decimal`，表示购买的单位数量。
    - total_amount: 总金额，类型为 `Decimal`，表示总的价格金额。
    - currency: 货币类型，类型为字符串，表示使用的货币类型。

    主要用途：用于定义和管理价格信息的相关属性，便于在代码中进行价格信息的匹配和处理。
    """

    unit_price: Decimal  # 单位价格，类型为 `Decimal`，表示每个单位的价格
    unit: Decimal  # 单位数量，类型为 `Decimal`，表示购买的单位数量
    total_amount: Decimal  # 总金额，类型为 `Decimal`，表示总的价格金额
    currency: str  # 货币类型，类型为字符串，表示使用的货币类型

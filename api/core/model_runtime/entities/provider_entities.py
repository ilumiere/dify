from collections.abc import Sequence
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from core.model_runtime.entities.common_entities import I18nObject
from core.model_runtime.entities.model_entities import ModelType, ProviderModel


class ConfigurateMethod(Enum):
    """
    提供者模型配置方法的枚举类。

    该类定义了两种配置方法：预定义模型和可定制模型。

    属性:
    - PREDEFINED_MODEL: 表示使用预定义的模型。
    - CUSTOMIZABLE_MODEL: 表示使用可定制的模型。
    """

    PREDEFINED_MODEL = "predefined-model"
    CUSTOMIZABLE_MODEL = "customizable-model"


class FormType(Enum):
    """
    表单类型的枚举类。

    该类定义了多种表单类型，用于不同的用户输入场景。

    属性:
    - TEXT_INPUT: 表示文本输入框。
    - SECRET_INPUT: 表示密码输入框。
    - SELECT: 表示下拉选择框。
    - RADIO: 表示单选按钮。
    - SWITCH: 表示开关按钮。
    """

    TEXT_INPUT = "text-input"
    SECRET_INPUT = "secret-input"
    SELECT = "select"
    RADIO = "radio"
    SWITCH = "switch"


class FormShowOnObject(BaseModel):
    """
    表单显示条件的模型类。

    该类用于定义表单在特定条件下的显示行为。

    属性:
    - variable: 变量名称，类型为字符串。
    - value: 变量值，类型为字符串。
    """

    variable: str
    value: str


class FormOption(BaseModel):
    """
    表单选项的模型类。

    该类用于定义表单中的选项，包括标签、值和显示条件。

    属性:
    - label: 选项的标签，类型为 I18nObject，用于国际化显示。
    - value: 选项的值，类型为字符串。
    - show_on: 显示条件列表，类型为 list[FormShowOnObject]，默认为空列表。

    方法:
    - __init__: 初始化方法，如果标签为空，则使用值作为标签。
    """

    label: I18nObject
    value: str
    show_on: list[FormShowOnObject] = []

    def __init__(self, **data):
        super().__init__(**data)
        if not self.label:
            self.label = I18nObject(en_US=self.value)


class CredentialFormSchema(BaseModel):
    """
    凭证表单模式的模型类。

    该类用于定义凭证表单的结构，包括变量、标签、类型、是否必填、默认值、选项、占位符、最大长度和显示条件。

    属性:
    - variable: 变量名称，类型为字符串。
    - label: 标签，类型为 I18nObject，用于国际化显示。
    - type: 表单类型，类型为 FormType 枚举。
    - required: 是否必填，类型为布尔值，默认为 True。
    - default: 默认值，类型为 Optional[str]，默认为 None。
    - options: 选项列表，类型为 Optional[list[FormOption]]，默认为 None。
    - placeholder: 占位符，类型为 Optional[I18nObject]，默认为 None。
    - max_length: 最大长度，类型为 int，默认为 0。
    - show_on: 显示条件列表，类型为 list[FormShowOnObject]，默认为空列表。
    """

    variable: str
    label: I18nObject
    type: FormType
    required: bool = True
    default: Optional[str] = None
    options: Optional[list[FormOption]] = None
    placeholder: Optional[I18nObject] = None
    max_length: int = 0
    show_on: list[FormShowOnObject] = []


class ProviderCredentialSchema(BaseModel):
    """
    提供者凭证模式的模型类。

    该类用于定义提供者的凭证表单模式列表。

    属性:
    - credential_form_schemas: 凭证表单模式列表，类型为 list[CredentialFormSchema]。
    """

    credential_form_schemas: list[CredentialFormSchema]


class FieldModelSchema(BaseModel):
    """
    字段模型模式的模型类。

    该类用于定义字段的标签和占位符。

    属性:
    - label: 标签，类型为 I18nObject，用于国际化显示。
    - placeholder: 占位符，类型为 Optional[I18nObject]，默认为 None。
    """

    label: I18nObject
    placeholder: Optional[I18nObject] = None


class ModelCredentialSchema(BaseModel):
    """
    模型凭证模式的模型类。

    该类用于定义模型的凭证表单模式，包括模型字段和凭证表单模式列表。

    属性:
    - model: 模型字段，类型为 FieldModelSchema。
    - credential_form_schemas: 凭证表单模式列表，类型为 list[CredentialFormSchema]。
    """

    model: FieldModelSchema
    credential_form_schemas: list[CredentialFormSchema]


class SimpleProviderEntity(BaseModel):
    """
    简单提供者实体的模型类。

    该类用于表示一个简单的提供者实体，包含提供者的基本信息。

    属性:
    - provider: 提供者的名称，类型为字符串。
    - label: 提供者的标签，类型为 I18nObject，用于国际化显示。
    - icon_small: 提供者的小图标，类型为 Optional[I18nObject]，默认为 None。
    - icon_large: 提供者的大图标，类型为 Optional[I18nObject]，默认为 None。
    - supported_model_types: 提供者支持的模型类型列表，类型为 Sequence[ModelType]。
    - models: 提供者的模型列表，类型为 list[ProviderModel]，默认为空列表。
    """

    provider: str
    label: I18nObject
    icon_small: Optional[I18nObject] = None
    icon_large: Optional[I18nObject] = None
    supported_model_types: Sequence[ModelType]
    models: list[ProviderModel] = []


class ProviderHelpEntity(BaseModel):
    """
    提供者帮助实体的模型类。

    该类用于表示提供者的帮助信息，包括标题和URL。

    属性:
    - title: 帮助信息的标题，类型为 I18nObject，用于国际化显示。
    - url: 帮助信息的URL，类型为 I18nObject，用于国际化显示。
    """

    title: I18nObject
    url: I18nObject


class ProviderEntity(BaseModel):
    """
    提供者实体的模型类。

    该类用于表示一个完整的提供者实体，包含提供者的详细信息。

    属性:
    - provider: 提供者的名称，类型为字符串。
    - label: 提供者的标签，类型为 I18nObject，用于国际化显示。
    - description: 提供者的描述，类型为 Optional[I18nObject]，默认为 None。
    - icon_small: 提供者的小图标，类型为 Optional[I18nObject]，默认为 None。
    - icon_large: 提供者的大图标，类型为 Optional[I18nObject]，默认为 None。
    - background: 提供者的背景图片，类型为 Optional[str]，默认为 None。
    - help: 提供者的帮助信息，类型为 Optional[ProviderHelpEntity]，默认为 None。
    - supported_model_types: 提供者支持的模型类型列表，类型为 Sequence[ModelType]。
    - configurate_methods: 提供者的配置方法列表，类型为 list[ConfigurateMethod]。
    - models: 提供者的模型列表，类型为 list[ProviderModel]，默认为空列表。
    - provider_credential_schema: 提供者的凭证模式，类型为 Optional[ProviderCredentialSchema]，默认为 None。
    - model_credential_schema: 模型的凭证模式，类型为 Optional[ModelCredentialSchema]，默认为 None。

    方法:
    - to_simple_provider: 将当前提供者实体转换为简单提供者实体。

    返回值:
    - 返回一个 SimpleProviderEntity 对象。
    """

    provider: str
    label: I18nObject
    description: Optional[I18nObject] = None
    icon_small: Optional[I18nObject] = None
    icon_large: Optional[I18nObject] = None
    background: Optional[str] = None
    help: Optional[ProviderHelpEntity] = None
    supported_model_types: Sequence[ModelType]
    configurate_methods: list[ConfigurateMethod]
    models: list[ProviderModel] = []
    provider_credential_schema: Optional[ProviderCredentialSchema] = None
    model_credential_schema: Optional[ModelCredentialSchema] = None

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())

    def to_simple_provider(self) -> SimpleProviderEntity:
        """
        将当前提供者实体转换为简单提供者实体。

        该方法用于提取当前提供者实体的基本信息，并返回一个 SimpleProviderEntity 对象。

        返回值:
        - 返回一个 SimpleProviderEntity 对象。
        """
        return SimpleProviderEntity(
            provider=self.provider,
            label=self.label,
            icon_small=self.icon_small,
            icon_large=self.icon_large,
            supported_model_types=self.supported_model_types,
            models=self.models,
        )


class ProviderConfig(BaseModel):
    """
    提供者配置的模型类。

    该类用于表示提供者的配置信息，包括提供者的名称和凭证。

    属性:
    - provider: 提供者的名称，类型为字符串。
    - credentials: 提供者的凭证，类型为字典。
    """

    provider: str
    credentials: dict

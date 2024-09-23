from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from core.model_runtime.entities.common_entities import I18nObject
from core.model_runtime.entities.model_entities import ModelType, ProviderModel
from core.model_runtime.entities.provider_entities import ProviderEntity


class ModelStatus(Enum):
    """
    模型状态的枚举类。

    该类定义了模型可能的状态，每个状态对应一个特定的字符串值。

    属性:
    - ACTIVE: 表示模型处于活动状态，可以正常使用。
    - NO_CONFIGURE: 表示模型未配置，无法使用。
    - QUOTA_EXCEEDED: 表示模型的配额已超出，无法使用。
    - NO_PERMISSION: 表示用户没有权限使用该模型。
    - DISABLED: 表示模型已被禁用，无法使用。

    主要用途：用于表示和管理模型的状态，便于在代码中进行状态判断和处理。
    """

    ACTIVE = "active"  # 模型处于活动状态，可以正常使用
    NO_CONFIGURE = "no-configure"  # 模型未配置，无法使用
    QUOTA_EXCEEDED = "quota-exceeded"  # 模型的配额已超出，无法使用
    NO_PERMISSION = "no-permission"  # 用户没有权限使用该模型
    DISABLED = "disabled"  # 模型已被禁用，无法使用


class SimpleModelProviderEntity(BaseModel):
    """
    简单模型提供者实体类。

    该类用于表示一个简单的模型提供者实体，包含提供者的基本信息。

    属性:
    - provider: 提供者的名称，类型为字符串。
    - label: 提供者的标签，类型为 I18nObject，用于国际化显示。
    - icon_small: 提供者的小图标，类型为 Optional[I18nObject]，默认为 None。
    - icon_large: 提供者的大图标，类型为 Optional[I18nObject]，默认为 None。
    - supported_model_types: 提供者支持的模型类型列表，类型为 list[ModelType]。

    主要用途：存储和管理简单模型提供者的信息，包括名称、标签、图标和支持的模型类型。
    """

    provider: str  # 提供者的名称
    label: I18nObject  # 提供者的标签，用于国际化显示
    icon_small: Optional[I18nObject] = None  # 提供者的小图标，默认为 None
    icon_large: Optional[I18nObject] = None  # 提供者的大图标，默认为 None
    supported_model_types: list[ModelType]  # 提供者支持的模型类型列表

    def __init__(self, provider_entity: ProviderEntity) -> None:
        """
        初始化简单模型提供者实体。

        该方法用于从 ProviderEntity 对象初始化 SimpleModelProviderEntity 对象。

        参数:
        - provider_entity: 一个 ProviderEntity 对象，包含提供者的详细信息。

        返回值:
        - 无返回值，该方法通过 super().__init__() 方法初始化当前对象的属性。
        """
        # 调用父类 BaseModel 的初始化方法，传递从 provider_entity 中提取的属性值
        super().__init__(
            provider=provider_entity.provider,  # 提供者的名称
            label=provider_entity.label,  # 提供者的标签
            icon_small=provider_entity.icon_small,  # 提供者的小图标
            icon_large=provider_entity.icon_large,  # 提供者的大图标
            supported_model_types=provider_entity.supported_model_types,  # 提供者支持的模型类型列表
        )


class ProviderModelWithStatusEntity(ProviderModel):
    """
    带有状态的模型提供者实体类。

    该类用于表示一个带有状态的模型提供者实体，包含模型的状态和负载均衡的启用状态。

    属性:
    - status: 模型的状态，类型为 ModelStatus 枚举。
    - load_balancing_enabled: 负载均衡是否启用，类型为布尔值，默认为 False。

    主要用途：存储和管理带有状态的模型提供者的信息，包括模型的状态和负载均衡的启用状态。
    """

    status: ModelStatus  # 模型的状态，类型为 ModelStatus 枚举
    load_balancing_enabled: bool = False  # 负载均衡是否启用，类型为布尔值，默认为 False

class ModelWithProviderEntity(ProviderModelWithStatusEntity):
    """
    Model with provider entity.
    """

    provider: SimpleModelProviderEntity


class DefaultModelProviderEntity(BaseModel):
    """
    默认模型提供者实体类。

    该类用于表示一个默认的模型提供者实体，包含提供者的基本信息。

    属性:
    - provider: 提供者的名称，类型为字符串。
    - label: 提供者的标签，类型为 I18nObject，用于国际化显示。
    - icon_small: 提供者的小图标，类型为 Optional[I18nObject]，默认为 None。
    - icon_large: 提供者的大图标，类型为 Optional[I18nObject]，默认为 None。
    - supported_model_types: 提供者支持的模型类型列表，类型为 list[ModelType]。

    主要用途：存储和管理默认模型提供者的信息，包括名称、标签、图标和支持的模型类型。
    """

    provider: str  # 提供者的名称
    label: I18nObject  # 提供者的标签，用于国际化显示
    icon_small: Optional[I18nObject] = None  # 提供者的小图标，默认为 None
    icon_large: Optional[I18nObject] = None  # 提供者的大图标，默认为 None
    supported_model_types: list[ModelType]  # 提供者支持的模型类型列表


class DefaultModelEntity(BaseModel):
    """
    默认模型实体类。

    该类用于表示一个默认的模型实体，包含模型的基本信息。

    属性:
    - model: 模型的名称，类型为字符串。
    - model_type: 模型的类型，类型为 ModelType 枚举。
    - provider: 模型的提供者信息，类型为 DefaultModelProviderEntity 类。

    Pydantic 配置:
    - model_config: 配置 Pydantic 的模型行为，这里设置了 protected_namespaces 为空元组，表示不保护任何命名空间。
    """

    model: str
    model_type: ModelType
    provider: DefaultModelProviderEntity

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())

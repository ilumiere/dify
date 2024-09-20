from enum import Enum

from extensions.ext_database import db

from .types import StringUUID

# 在函数 process_provider 中，首先将传入的字符串转换为枚举类型，然后根据枚举类型执行不同的逻辑。
# ProviderType 枚举类可以帮助你更好地管理和使用提供者类型，避免硬编码字符串，提高代码的可读性和可维护性。
# ProviderType.name CUSTOM
# ProviderType.value custom
#  
class ProviderType(Enum):
    """
    枚举类，用于表示提供者类型。
    主要用途：管理和使用提供者类型，避免硬编码字符串，提高代码的可读性和可维护性。
    """
    CUSTOM = "custom"  # 自定义提供者类型
    SYSTEM = "system"  # 系统提供者类型

    @staticmethod
    def value_of(value):
        """
        静态方法，根据传入的字符串值返回对应的枚举成员。
        参数：
        - value: 字符串，表示提供者类型的值。
        返回值：
        - 对应的枚举成员。
        异常：
        - 如果找不到匹配的枚举成员，抛出 ValueError 异常。
        """
        for member in ProviderType:  # 遍历枚举成员
            if member.value == value:  # 如果找到匹配的值
                return member  # 返回对应的枚举成员
        raise ValueError(f"No matching enum found for value '{value}'")  # 抛出异常

# print(ProviderType.CUSTOM)  # 打印 CUSTOM 枚举成员
# print(ProviderType.value_of("custom"))  # 打印通过 value_of 方法找到的 CUSTOM 枚举成员


class ProviderQuotaType(Enum):
    """
    枚举类，用于表示提供者的配额类型。
    主要用途：管理和使用提供者的配额类型，避免硬编码字符串，提高代码的可读性和可维护性。
    """
    PAID = "paid"  # 托管付费配额
    """hosted paid quota"""

    FREE = "free"  # 第三方免费配额
    """third-party free quota"""

    TRIAL = "trial"  # 托管试用配额
    """hosted trial quota"""

    @staticmethod
    def value_of(value):
        """
        静态方法，根据传入的字符串值返回对应的枚举成员。
        参数：
        - value: 字符串，表示配额类型的值。
        返回值：
        - 对应的枚举成员。
        异常：
        - 如果找不到匹配的枚举成员，抛出 ValueError 异常。
        """
        for member in ProviderQuotaType:  # 遍历枚举成员
            if member.value == value:  # 如果找到匹配的值
                return member  # 返回对应的枚举成员
        raise ValueError(f"No matching enum found for value '{value}'")  # 抛出异常


class Provider(db.Model):
    """
    提供者模型，表示 API 提供者及其配置。
    主要用途：存储和管理 API 提供者的信息和配置。
    """

    __tablename__ = "providers"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="provider_pkey"),  # 主键约束
        db.Index("provider_tenant_id_provider_idx", "tenant_id", "provider_name"),  # 索引
        db.UniqueConstraint(
            "tenant_id", "provider_name", "provider_type", "quota_type", name="unique_provider_name_type_quota"
        ),  # 唯一约束
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    provider_type = db.Column(db.String(40), nullable=False, server_default=db.text("'custom'::character varying"))  # 提供者类型，默认值为 'custom'
    encrypted_config = db.Column(db.Text, nullable=True)  # 加密配置，可为空
    is_valid = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))  # 是否有效，默认值为 False
    last_used = db.Column(db.DateTime, nullable=True)  # 最后使用时间，可为空

    quota_type = db.Column(db.String(40), nullable=True, server_default=db.text("''::character varying"))  # 配额类型，默认值为空字符串
    quota_limit = db.Column(db.BigInteger, nullable=True)  # 配额限制，可为空
    quota_used = db.Column(db.BigInteger, default=0)  # 已用配额，默认值为 0

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间

    def __repr__(self):
        """
        返回对象的字符串表示形式。
        返回值：
        - 字符串，包含对象的主要属性。
        """
        return (
            f"<Provider(id={self.id}, tenant_id={self.tenant_id}, provider_name='{self.provider_name}',"
            f" provider_type='{self.provider_type}')>"
        )

    @property
    def token_is_set(self):
        """
        属性方法，检查加密配置是否已设置。
        返回值：
        - 布尔值，True 表示加密配置已设置，False 表示未设置。
        """
        return self.encrypted_config is not None

    @property
    def is_enabled(self):
        """
        属性方法，检查提供者是否已启用。
        返回值：
        - 布尔值，True 表示提供者已启用，False 表示未启用。
        """
        if self.provider_type == ProviderType.SYSTEM.value:  # 如果是系统提供者
            return self.is_valid  # 返回是否有效
        else:  # 如果是自定义提供者
            return self.is_valid and self.token_is_set  # 返回是否有效且令牌已设置


class ProviderModel(db.Model):
    """
    提供者模型，表示 API 提供者的模型及其配置。
    主要用途：存储和管理 API 提供者的模型信息和配置。
    """

    __tablename__ = "provider_models"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="provider_model_pkey"),  # 主键约束
        db.Index("provider_model_tenant_id_provider_idx", "tenant_id", "provider_name"),  # 索引
        db.UniqueConstraint(
            "tenant_id", "provider_name", "model_name", "model_type", name="unique_provider_model_name"
        ),  # 唯一约束
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    model_name = db.Column(db.String(255), nullable=False)  # 模型名称，不可为空
    model_type = db.Column(db.String(40), nullable=False)  # 模型类型，不可为空
    encrypted_config = db.Column(db.Text, nullable=True)  # 加密配置，可为空
    is_valid = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))  # 是否有效，默认值为 False
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间


class TenantDefaultModel(db.Model):
    """
    租户默认模型，表示租户的默认模型及其配置。
    主要用途：存储和管理租户的默认模型信息和配置。
    """

    __tablename__ = "tenant_default_models"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="tenant_default_model_pkey"),  # 主键约束
        db.Index("tenant_default_model_tenant_id_provider_type_idx", "tenant_id", "provider_name", "model_type"),  # 索引
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    model_name = db.Column(db.String(255), nullable=False)  # 模型名称，不可为空
    model_type = db.Column(db.String(40), nullable=False)  # 模型类型，不可为空
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间


class TenantPreferredModelProvider(db.Model):
    """
    租户首选模型提供者，表示租户的首选模型提供者及其配置。
    主要用途：存储和管理租户的首选模型提供者信息和配置。
    """

    __tablename__ = "tenant_preferred_model_providers"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="tenant_preferred_model_provider_pkey"),  # 主键约束
        db.Index("tenant_preferred_model_provider_tenant_provider_idx", "tenant_id", "provider_name"),  # 索引
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    preferred_provider_type = db.Column(db.String(40), nullable=False)  # 首选提供者类型，不可为空
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间


class ProviderOrder(db.Model):
    """
    提供者订单，表示提供者的订单及其配置。
    主要用途：存储和管理提供者的订单信息和配置。
    """

    __tablename__ = "provider_orders"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="provider_order_pkey"),  # 主键约束
        db.Index("provider_order_tenant_provider_idx", "tenant_id", "provider_name"),  # 索引
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    account_id = db.Column(StringUUID, nullable=False)  # 账户 ID，不可为空
    payment_product_id = db.Column(db.String(191), nullable=False)  # 支付产品 ID，不可为空
    payment_id = db.Column(db.String(191))  # 支付 ID，可为空
    transaction_id = db.Column(db.String(191))  # 交易 ID，可为空
    quantity = db.Column(db.Integer, nullable=False, server_default=db.text("1"))  # 数量，默认值为 1
    currency = db.Column(db.String(40))  # 货币类型，可为空
    total_amount = db.Column(db.Integer)  # 总金额，可为空
    payment_status = db.Column(db.String(40), nullable=False, server_default=db.text("'wait_pay'::character varying"))  # 支付状态，默认值为 'wait_pay'
    paid_at = db.Column(db.DateTime)  # 支付时间，可为空
    pay_failed_at = db.Column(db.DateTime)  # 支付失败时间，可为空
    refunded_at = db.Column(db.DateTime)  # 退款时间，可为空
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间


class ProviderModelSetting(db.Model):
    """
    提供者模型设置，记录模型的启用状态和负载均衡状态。
    主要用途：存储和管理提供者模型的设置信息。
    """

    __tablename__ = "provider_model_settings"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="provider_model_setting_pkey"),  # 主键约束
        db.Index("provider_model_setting_tenant_provider_model_idx", "tenant_id", "provider_name", "model_type"),  # 索引
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    model_name = db.Column(db.String(255), nullable=False)  # 模型名称，不可为空
    model_type = db.Column(db.String(40), nullable=False)  # 模型类型，不可为空
    enabled = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))  # 是否启用，默认值为 True
    load_balancing_enabled = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))  # 是否启用负载均衡，默认值为 False
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间


class LoadBalancingModelConfig(db.Model):
    """
    负载均衡模型配置，表示负载均衡模型的配置。
    主要用途：存储和管理负载均衡模型的配置信息。
    """

    __tablename__ = "load_balancing_model_configs"  # 数据库表名
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="load_balancing_model_config_pkey"),  # 主键约束
        db.Index("load_balancing_model_config_tenant_provider_model_idx", "tenant_id", "provider_name", "model_type"),  # 索引
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # UUID 主键
    tenant_id = db.Column(StringUUID, nullable=False)  # 租户 ID，不可为空
    provider_name = db.Column(db.String(255), nullable=False)  # 提供者名称，不可为空
    model_name = db.Column(db.String(255), nullable=False)  # 模型名称，不可为空
    model_type = db.Column(db.String(40), nullable=False)  # 模型类型，不可为空
    name = db.Column(db.String(255), nullable=False)  # 配置名称，不可为空
    encrypted_config = db.Column(db.Text, nullable=True)  # 加密的配置信息，可为空
    enabled = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))  # 是否启用，默认值为 True
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间，默认值为当前时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 更新时间，默认值为当前时间

from typing import Any, Optional
from urllib.parse import quote_plus

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt, computed_field
from pydantic_settings import BaseSettings

from configs.middleware.cache.redis_config import RedisConfig
from configs.middleware.storage.aliyun_oss_storage_config import AliyunOSSStorageConfig
from configs.middleware.storage.amazon_s3_storage_config import S3StorageConfig
from configs.middleware.storage.azure_blob_storage_config import AzureBlobStorageConfig
from configs.middleware.storage.google_cloud_storage_config import GoogleCloudStorageConfig
from configs.middleware.storage.huawei_obs_storage_config import HuaweiCloudOBSStorageConfig
from configs.middleware.storage.oci_storage_config import OCIStorageConfig
from configs.middleware.storage.tencent_cos_storage_config import TencentCloudCOSStorageConfig
from configs.middleware.storage.volcengine_tos_storage_config import VolcengineTOSStorageConfig
from configs.middleware.vdb.analyticdb_config import AnalyticdbConfig
from configs.middleware.vdb.chroma_config import ChromaConfig
from configs.middleware.vdb.elasticsearch_config import ElasticsearchConfig
from configs.middleware.vdb.milvus_config import MilvusConfig
from configs.middleware.vdb.myscale_config import MyScaleConfig
from configs.middleware.vdb.opensearch_config import OpenSearchConfig
from configs.middleware.vdb.oracle_config import OracleConfig
from configs.middleware.vdb.pgvector_config import PGVectorConfig
from configs.middleware.vdb.pgvectors_config import PGVectoRSConfig
from configs.middleware.vdb.qdrant_config import QdrantConfig
from configs.middleware.vdb.relyt_config import RelytConfig
from configs.middleware.vdb.tencent_vector_config import TencentVectorDBConfig
from configs.middleware.vdb.tidb_vector_config import TiDBVectorConfig
from configs.middleware.vdb.weaviate_config import WeaviateConfig


class StorageConfig(BaseSettings):
    """
    存储配置类，用于定义和管理不同类型的存储配置。

    该类继承自 `BaseSettings`，提供了存储类型和本地存储路径的配置选项。
    """

    STORAGE_TYPE: str = Field(
        description="存储类型，默认值为 `local`，可选值包括 `local`, `s3`, `azure-blob`, `aliyun-oss`, `google-storage`。",
        default="local",
    )
    """
    STORAGE_TYPE 属性用于指定存储类型。
    - 默认值为 `local`，表示使用本地存储。
    - 可选值包括 `local`, `s3`, `azure-blob`, `aliyun-oss`, `google-storage`，分别表示本地存储、Amazon S3、Azure Blob 存储、阿里云 OSS 存储和 Google 云存储。
    """

    STORAGE_LOCAL_PATH: str = Field(
        description="本地存储路径，默认值为 `storage`。",
        default="storage",
    )
    """
    STORAGE_LOCAL_PATH 属性用于指定本地存储的路径。
    - 默认值为 `storage`，表示本地存储的根目录为 `storage`。
    """


class VectorStoreConfig(BaseSettings):
    """
    VectorStoreConfig 类用于定义和管理向量存储的配置。

    主要用途和功能：
    - 提供向量存储类型的配置选项。
    - 使用 Pydantic 的 Field 来定义配置项的类型、描述和默认值。

    属性详细解释：
    - VECTOR_STORE: 可选字符串，表示向量存储的类型。默认值为 None，表示未设置。
    """

    VECTOR_STORE: Optional[str] = Field(
        description="向量存储类型",
        default=None,
    )
    """
    VECTOR_STORE 属性用于指定向量存储的类型。
    - 类型为可选字符串。
    - 描述: 用于指定向量存储的类型。
    - 默认值: None，表示未设置向量存储类型。
    """


class KeywordStoreConfig(BaseSettings):
    """
    KeywordStoreConfig 类用于定义和管理关键词存储的配置。

    主要用途和功能：
    - 提供关键词存储类型的配置选项。
    - 使用 Pydantic 的 Field 来定义配置项的类型、描述和默认值。

    属性详细解释：
    - KEYWORD_STORE: 字符串类型，表示关键词存储的类型。默认值为 "jieba"，表示使用 Jieba 分词器作为关键词存储的类型。
    """

    KEYWORD_STORE: str = Field(
        description="关键词存储类型",
        default="jieba",
    )
    """
    KEYWORD_STORE 属性用于指定关键词存储的类型。
    - 类型为字符串。
    - 描述: 用于指定关键词存储的类型。
    - 默认值: "jieba"，表示使用 Jieba 分词器作为关键词存储的类型。
    """



class DatabaseConfig:
    """
    DatabaseConfig 类用于定义和管理数据库连接的配置。

    主要用途和功能：
    - 提供数据库连接所需的配置参数。
    - 使用 Pydantic 的 Field 来定义配置项的类型、描述和默认值。
    - 包含一个计算属性 `SQLALCHEMY_DATABASE_URI`，用于生成数据库连接 URI。
    - 包含另一个计算属性 `SQLALCHEMY_ENGINE_OPTIONS`，用于生成 SQLAlchemy 引擎选项。

    属性详细解释：
    - DB_HOST: 字符串类型，表示数据库的主机地址。默认值为 "localhost"。
    - DB_PORT: 正整数类型，表示数据库的端口号。默认值为 5432。
    - DB_USERNAME: 字符串类型，表示数据库的用户名。默认值为 "postgres"。
    - DB_PASSWORD: 字符串类型，表示数据库的密码。默认值为空字符串。
    - DB_DATABASE: 字符串类型，表示数据库的名称。默认值为 "dify"。
    - DB_CHARSET: 字符串类型，表示数据库的字符集。默认值为空字符串。
    - DB_EXTRAS: 字符串类型，表示数据库的额外选项。默认值为空字符串。
    - SQLALCHEMY_DATABASE_URI_SCHEME: 字符串类型，表示数据库 URI 的方案。默认值为 "postgresql"。
    - SQLALCHEMY_POOL_SIZE: 非负整数类型，表示 SQLAlchemy 连接池的大小。默认值为 30。
    - SQLALCHEMY_MAX_OVERFLOW: 非负整数类型，表示 SQLAlchemy 连接池的最大溢出数。默认值为 10。
    - SQLALCHEMY_POOL_RECYCLE: 非负整数类型，表示 SQLAlchemy 连接池的回收时间（以秒为单位）。默认值为 3600。
    - SQLALCHEMY_POOL_PRE_PING: 布尔类型，表示是否启用 SQLAlchemy 连接池的预 ping 功能。默认值为 False。
    - SQLALCHEMY_ECHO: 布尔或字符串类型，表示是否启用 SQLAlchemy 的 echo 功能。默认值为 False。
    """

    DB_HOST: str = Field(
        description="数据库的主机地址",
        default="localhost",
    )

    DB_PORT: PositiveInt = Field(
        description="数据库的端口号",
        default=5432,
    )

    DB_USERNAME: str = Field(
        description="数据库的用户名",
        default="postgres",
    )

    DB_PASSWORD: str = Field(
        description="数据库的密码",
        default="",
    )

    DB_DATABASE: str = Field(
        description="数据库的名称",
        default="dify",
    )

    DB_CHARSET: str = Field(
        description="数据库的字符集",
        default="",
    )

    DB_EXTRAS: str = Field(
        description="数据库的额外选项。例如：keepalives_idle=60&keepalives=1",
        default="",
    )

    SQLALCHEMY_DATABASE_URI_SCHEME: str = Field(
        description="数据库 URI 的方案",
        default="postgresql",
    )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        计算属性，用于生成数据库连接 URI。

        返回值：
        - 字符串类型，表示数据库连接 URI。

        逻辑解释：
        - 首先，根据 `DB_CHARSET` 是否存在，生成 `db_extras` 字符串。
        - 然后，去除 `db_extras` 字符串中的多余 "&" 符号。
        - 最后，拼接数据库连接 URI，包括方案、用户名、密码、主机地址、端口号、数据库名称和额外选项。
        """
        db_extras = (
            f"{self.DB_EXTRAS}&client_encoding={self.DB_CHARSET}" if self.DB_CHARSET else self.DB_EXTRAS
        ).strip("&")
        db_extras = f"?{db_extras}" if db_extras else ""
        return (
            f"{self.SQLALCHEMY_DATABASE_URI_SCHEME}://"
            f"{quote_plus(self.DB_USERNAME)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
            f"{db_extras}"
        )

    SQLALCHEMY_POOL_SIZE: NonNegativeInt = Field(
        description="SQLAlchemy 连接池的大小",
        default=30,
    )

    SQLALCHEMY_MAX_OVERFLOW: NonNegativeInt = Field(
        description="SQLAlchemy 连接池的最大溢出数",
        default=10,
    )

    SQLALCHEMY_POOL_RECYCLE: NonNegativeInt = Field(
        description="SQLAlchemy 连接池的回收时间（以秒为单位）",
        default=3600,
    )

    SQLALCHEMY_POOL_PRE_PING: bool = Field(
        description="是否启用 SQLAlchemy 连接池的预 ping 功能",
        default=False,
    )

    SQLALCHEMY_ECHO: bool | str = Field(
        description="是否启用 SQLAlchemy 的 echo 功能",
        default=False,
    )

    @computed_field
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict[str, Any]:
        """
        计算属性，用于生成 SQLAlchemy 引擎选项。

        返回值：
        - 字典类型，包含 SQLAlchemy 引擎的配置选项。

        逻辑解释：
        - 返回一个字典，包含连接池大小、最大溢出数、连接池回收时间、预 ping 功能和连接参数。
        """
        return {
            "pool_size": self.SQLALCHEMY_POOL_SIZE,
            "max_overflow": self.SQLALCHEMY_MAX_OVERFLOW,
            "pool_recycle": self.SQLALCHEMY_POOL_RECYCLE,
            "pool_pre_ping": self.SQLALCHEMY_POOL_PRE_PING,
            "connect_args": {"options": "-c timezone=UTC"},
        }


class CeleryConfig(DatabaseConfig):
    """
    CeleryConfig 类用于配置与 Celery 任务队列相关的参数。

    主要用途和功能：
    - 提供与 Celery 任务队列连接所需的配置参数。
    - 使用 Pydantic 的 Field 来定义每个配置项的类型、描述和默认值。

    属性详细解释：
    - CELERY_BACKEND: 字符串类型，表示 Celery 的后端存储方式。可选值为 `database` 或 `redis`，默认值为 `database`。
    - CELERY_BROKER_URL: 可选字符串类型，表示 Celery 的代理 URL。默认值为 None，表示未设置。
    - CELERY_USE_SENTINEL: 可选布尔类型，表示是否使用 Redis Sentinel 模式。默认值为 False，表示不使用。
    - CELERY_SENTINEL_MASTER_NAME: 可选字符串类型，表示 Redis Sentinel 的主节点名称。默认值为 None，表示未设置。
    - CELERY_SENTINEL_SOCKET_TIMEOUT: 可选正浮点数类型，表示 Redis Sentinel 的套接字超时时间。默认值为 0.1 秒。
    """

    CELERY_BACKEND: str = Field(
        description="Celery 后端存储方式，可选值为 `database` 或 `redis`",
        default="database",
    )

    CELERY_BROKER_URL: Optional[str] = Field(
        description="Celery 代理 URL",
        default=None,
    )

    CELERY_USE_SENTINEL: Optional[bool] = Field(
        description="是否使用 Redis Sentinel 模式",
        default=False,
    )

    CELERY_SENTINEL_MASTER_NAME: Optional[str] = Field(
        description="Redis Sentinel 主节点名称",
        default=None,
    )

    CELERY_SENTINEL_SOCKET_TIMEOUT: Optional[PositiveFloat] = Field(
        description="Redis Sentinel 套接字超时时间",
        default=0.1,
    )

    @computed_field
    @property
    def CELERY_RESULT_BACKEND(self) -> str | None:
        """
        计算属性，用于生成 Celery 结果后端 URL。

        返回值：
        - 字符串类型或 None，表示 Celery 结果后端 URL。

        逻辑解释：
        - 如果 CELERY_BACKEND 为 `database`，则返回格式为 `db+SQLALCHEMY_DATABASE_URI` 的字符串。
        - 否则，返回 CELERY_BROKER_URL。
        """
        return (
            "db+{}".format(self.SQLALCHEMY_DATABASE_URI)
            if self.CELERY_BACKEND == "database"
            else self.CELERY_BROKER_URL
        )

    @computed_field
    @property
    def BROKER_USE_SSL(self) -> bool:
        """
        计算属性，用于判断是否使用 SSL 连接 Celery 代理。

        返回值：
        - 布尔类型，表示是否使用 SSL 连接 Celery 代理。

        逻辑解释：
        - 如果 CELERY_BROKER_URL 以 `rediss://` 开头，则返回 True，表示使用 SSL。
        - 否则，返回 False。
        """
        return self.CELERY_BROKER_URL.startswith("rediss://") if self.CELERY_BROKER_URL else False


class MiddlewareConfig(
    # 按照字母顺序排列配置类
    CeleryConfig,
    DatabaseConfig,
    KeywordStoreConfig,
    RedisConfig,
    # 存储和存储提供者的配置类
    StorageConfig,
    AliyunOSSStorageConfig,
    AzureBlobStorageConfig,
    GoogleCloudStorageConfig,
    TencentCloudCOSStorageConfig,
    HuaweiCloudOBSStorageConfig,
    VolcengineTOSStorageConfig,
    S3StorageConfig,
    OCIStorageConfig,
    # vdb 和 vdb 提供者的配置类
    VectorStoreConfig,
    AnalyticdbConfig,
    ChromaConfig,
    MilvusConfig,
    MyScaleConfig,
    OpenSearchConfig,
    OracleConfig,
    PGVectorConfig,
    PGVectoRSConfig,
    QdrantConfig,
    RelytConfig,
    TencentVectorDBConfig,
    TiDBVectorConfig,
    WeaviateConfig,
    ElasticsearchConfig,
):
    """
    中间件配置类，用于整合和管理各种配置类。

    主要用途和功能：
    - 该类继承了多个配置类，用于统一管理和配置各种中间件相关的设置。
    - 通过继承这些配置类，MiddlewareConfig 可以访问和使用这些配置类的属性和方法。

    继承的配置类包括：
    - CeleryConfig: 用于配置 Celery 相关的设置。
    - DatabaseConfig: 用于配置数据库相关的设置。
    - KeywordStoreConfig: 用于配置关键词存储相关的设置。
    - RedisConfig: 用于配置 Redis 相关的设置。
    - StorageConfig: 用于配置存储相关的设置。
    - AliyunOSSStorageConfig: 用于配置阿里云 OSS 存储相关的设置。
    - AzureBlobStorageConfig: 用于配置 Azure Blob 存储相关的设置。
    - GoogleCloudStorageConfig: 用于配置 Google Cloud 存储相关的设置。
    - TencentCloudCOSStorageConfig: 用于配置腾讯云 COS 存储相关的设置。
    - HuaweiCloudOBSStorageConfig: 用于配置华为云 OBS 存储相关的设置。
    - VolcengineTOSStorageConfig: 用于配置火山引擎 TOS 存储相关的设置。
    - S3StorageConfig: 用于配置 S3 存储相关的设置。
    - OCIStorageConfig: 用于配置 OCI 存储相关的设置。
    - VectorStoreConfig: 用于配置向量存储相关的设置。
    - AnalyticdbConfig: 用于配置 AnalyticDB 相关的设置。
    - ChromaConfig: 用于配置 Chroma 相关的设置。
    - MilvusConfig: 用于配置 Milvus 相关的设置。
    - MyScaleConfig: 用于配置 MyScale 相关的设置。
    - OpenSearchConfig: 用于配置 OpenSearch 相关的设置。
    - OracleConfig: 用于配置 Oracle 相关的设置。
    - PGVectorConfig: 用于配置 PGVector 相关的设置。
    - PGVectoRSConfig: 用于配置 PGVectoRS 相关的设置。
    - QdrantConfig: 用于配置 Qdrant 相关的设置。
    - RelytConfig: 用于配置 Relyt 相关的设置。
    - TencentVectorDBConfig: 用于配置腾讯云向量数据库相关的设置。
    - TiDBVectorConfig: 用于配置 TiDB 向量相关的设置。
    - WeaviateConfig: 用于配置 Weaviate 相关的设置。
    - ElasticsearchConfig: 用于配置 Elasticsearch 相关的设置。

    该类本身没有定义额外的属性和方法，仅用于整合和管理继承的配置类。
    """
    pass

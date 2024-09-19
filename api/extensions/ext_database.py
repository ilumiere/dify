from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# 定义 PostgreSQL 索引命名约定
# 该字典用于指定不同类型的索引在 PostgreSQL 中的命名规则。
# 键是索引类型，值是命名模板。模板中的占位符将在创建索引时被替换为实际的表名和列名。
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",  # 普通索引的命名模板
    "uq": "%(table_name)s_%(column_0_name)s_key",  # 唯一约束的命名模板
    "ck": "%(table_name)s_%(constraint_name)s_check",  # 检查约束的命名模板
    "fk": "%(table_name)s_%(column_0_name)s_fkey",  # 外键约束的命名模板
    "pk": "%(table_name)s_pkey",  # 主键约束的命名模板
}

# 创建一个 MetaData 实例，并应用上述命名约定
# MetaData 是 SQLAlchemy 中用于管理数据库元数据的对象。
# naming_convention 参数指定了索引和约束的命名规则。
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

# 创建 SQLAlchemy 实例，并传入 metadata 参数
# SQLAlchemy 是 Flask-SQLAlchemy 扩展的核心类，用于管理数据库连接和操作。
# metadata 参数指定了数据库元数据的命名规则。
db = SQLAlchemy(metadata=metadata)


# 初始化 Flask 应用
# 该函数用于将 SQLAlchemy 实例与 Flask 应用关联起来。
# 参数:
#   app: Flask 应用实例，类型为 Flask。
def init_app(app):
    # 调用 SQLAlchemy 实例的 init_app 方法，将应用实例传递给它
    # 该方法会初始化 SQLAlchemy 实例，并将其与 Flask 应用关联起来。
    db.init_app(app)

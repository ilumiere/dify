import flask_migrate


def init(app, db):
    """
    初始化 Flask-Migrate 扩展。

    该函数的主要用途是初始化 Flask-Migrate 扩展，以便在 Flask 应用程序中进行数据库迁移。

    参数:
    app (Flask): Flask 应用程序实例，用于初始化 Flask-Migrate 扩展。
    db (SQLAlchemy): SQLAlchemy 实例，用于与数据库进行交互。

    函数内部的每一行代码或每个代码块的详细解释:
    1. `flask_migrate.Migrate(app, db)`: 初始化 Flask-Migrate 扩展，将 Flask 应用程序实例和 SQLAlchemy 实例传递给 Flask-Migrate。

    返回值:
    该函数没有返回值。
    """
    flask_migrate.Migrate(app, db)

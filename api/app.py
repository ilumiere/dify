import os

# 检查是否处于调试模式，如果不是，则使用 gevent 进行 monkey patch 和 gRPC 初始化
# gevent 是一个基于协程的 Python 网络库，它通过使用轻量级线程（称为 greenlet）来实现并发。
# gevent 的 monkey 模块可以对标准库进行 monkey patch，使得标准库中的阻塞操作（如 socket）变成非阻塞的，从而提高并发性能。
# grpc.experimental.gevent 是 gRPC 的一个实验性模块，用于与 gevent 集成。
# 通过调用 grpc.experimental.gevent.init_gevent()，可以将 gRPC 的阻塞操作转换为非阻塞操作，从而与 gevent 的协程模型兼容。
# 假设你有一个 Flask 应用，需要处理多个并发请求，并且每个请求都需要进行一些 I/O 操作（例如数据库查询、文件读写、网络请求等）。
# 如果使用阻塞编程，每个请求都会阻塞主线程，导致其他请求需要等待。而使用非阻塞编程，可以在等待 I/O 操作时处理其他请求，从而提高并发处理能力。

if os.environ.get("DEBUG", "false").lower() != "true":
    from gevent import monkey

    monkey.patch_all()

    import grpc.experimental.gevent

    grpc.experimental.gevent.init_gevent()

import json
import logging
import sys
import threading
import time
import warnings
from logging.handlers import RotatingFileHandler

from flask import Flask, Response, request
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized

import contexts
from commands import register_commands
from configs import dify_config

# DO NOT REMOVE BELOW
from events import event_handlers
from extensions import (
    ext_celery,
    ext_code_based_extension,
    ext_compress,
    ext_database,
    ext_hosting_provider,
    ext_login,
    ext_mail,
    ext_migrate,
    ext_redis,
    ext_sentry,
    ext_storage,
)
from extensions.ext_database import db
from extensions.ext_login import login_manager
from libs.passport import PassportService

# TODO: Find a way to avoid importing models here
from models import account, dataset, model, source, task, tool, tools, web
from services.account_service import AccountService

# DO NOT REMOVE ABOVE


warnings.simplefilter("ignore", ResourceWarning)

# 修复 Windows 平台上的时区设置
if os.name == "nt":
    os.system('tzutil /s "UTC"')
else:
    os.environ["TZ"] = "UTC"
    time.tzset()


class DifyApp(Flask):
    """
    自定义的 Flask 应用类，继承自 Flask 类，目前没有添加额外功能。
    """
    pass


# -------------
# Configuration
# -------------


config_type = os.getenv("EDITION", default="SELF_HOSTED")  # 默认使用 SELF_HOSTED 版本


# ----------------------------
# Application Factory Function
# ----------------------------


def create_flask_app_with_configs() -> Flask:
    """
    创建一个带有配置的 Flask 应用实例。
    配置从 .env 文件中加载。
    """
    dify_app = DifyApp(__name__)
    # from_mapping 是 Flask 应用配置的一个方法，用于从字典中加载配置。
    # 这个方法允许你将一个字典中的键值对直接映射到 Flask 应用的配置中。
    # 假设 dify_config.model_dump() 返回以下字典：
    # {
    #     "SECRET_KEY": "your_secret_key",
    #     "DEBUG": True,
    #     "SQLALCHEMY_DATABASE_URI": "postgresql://user:password@localhost/dbname"
    # }   
    # 加载进去之后就可以使用app.config["SECRECT_KEY"]
    # print(app.config["SECRET_KEY"])  # 输出: your_secret_key

    dify_app.config.from_mapping(dify_config.model_dump())

    # 将配置项填充到系统环境变量中
    for key, value in dify_app.config.items():
        if isinstance(value, str):
            os.environ[key] = value
        elif isinstance(value, int | float | bool):
            os.environ[key] = str(value)
        elif value is None:
            os.environ[key] = ""

    return dify_app


def create_app() -> Flask:
    """
    创建并配置 Flask 应用实例。

    该函数的主要用途是创建一个 Flask 应用实例，并对其进行配置。配置包括设置密钥、日志处理、初始化扩展、注册蓝图和命令等。

    参数:
    无

    返回值:
    Flask: 配置好的 Flask 应用实例。
    """
    # 调用 create_flask_app_with_configs 函数创建一个带有配置的 Flask 应用实例
    app = create_flask_app_with_configs()

    # 设置 Flask 应用的 secret_key，用于加密会话等安全操作
    app.secret_key = app.config["SECRET_KEY"]

    # 初始化日志处理程序列表，默认为 None
    log_handlers = None

    # 从配置中获取日志文件路径
    log_file = app.config.get("LOG_FILE")

    # 如果日志文件路径存在，则配置日志处理程序
    if log_file:
        # 获取日志文件所在的目录
        log_dir = os.path.dirname(log_file)

        # 确保日志目录存在，如果不存在则创建
        os.makedirs(log_dir, exist_ok=True)

        # 配置日志处理程序，包括文件处理程序和标准输出处理程序
        log_handlers = [
            RotatingFileHandler(
                filename=log_file,  # 日志文件路径
                maxBytes=1024 * 1024 * 1024,  # 每个日志文件的最大大小为 1GB
                backupCount=5,  # 保留 5 个备份日志文件
            ),
            logging.StreamHandler(sys.stdout),  # 标准输出处理程序
        ]

    # 配置日志记录器
    logging.basicConfig(
        level=app.config.get("LOG_LEVEL"),  # 日志级别
        format=app.config.get("LOG_FORMAT"),  # 日志格式
        datefmt=app.config.get("LOG_DATEFORMAT"),  # 日期格式
        handlers=log_handlers,  # 日志处理程序
        force=True,  # 强制重新配置日志记录器
    )

    # 从配置中获取日志时区
    log_tz = app.config.get("LOG_TZ")

    # 如果日志时区存在，则配置时区转换
    if log_tz:
        from datetime import datetime
        import pytz

        # 获取指定时区的时区对象
        timezone = pytz.timezone(log_tz)

        # 定义时间转换函数，将 UTC 时间转换为指定时区的时间
        def time_converter(seconds):
            return datetime.utcfromtimestamp(seconds).astimezone(timezone).timetuple()

        # 为每个日志处理程序设置时间转换函数
        for handler in logging.root.handlers:
            handler.formatter.converter = time_converter

    # 初始化所有 Flask 扩展
    initialize_extensions(app)

    # 注册所有蓝图路由
    register_blueprints(app)

    # 注册所有命令
    register_commands(app)

    # 返回配置好的 Flask 应用实例
    return app


def initialize_extensions(app):
    """
    初始化所有 Flask 扩展。
    将 Flask 应用实例传递给每个扩展实例，以绑定到 Flask 应用实例。
    """
    ext_compress.init_app(app)
    ext_code_based_extension.init()
    ext_database.init_app(app)
    ext_migrate.init(app, db)
    ext_redis.init_app(app)
    ext_storage.init_app(app)
    ext_celery.init_app(app)
    ext_login.init_app(app)
    ext_mail.init_app(app)
    ext_hosting_provider.init_app(app)
    ext_sentry.init_app(app)


# Flask-Login configuration
@login_manager.request_loader
def load_user_from_request(request_from_flask_login):
    """
    根据请求加载用户。
    """
    if request.blueprint not in {"console", "inner_api"}:
        return None
    # 检查 user_id 是否包含点，表示旧格式
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        auth_token = request.args.get("_token")
        if not auth_token:
            raise Unauthorized("Invalid Authorization token.")
    else:
        if " " not in auth_header:
            raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")
        auth_scheme, auth_token = auth_header.split(None, 1)
        auth_scheme = auth_scheme.lower()
        if auth_scheme != "bearer":
            raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")

    decoded = PassportService().verify(auth_token)
    user_id = decoded.get("user_id")

    account = AccountService.load_logged_in_account(account_id=user_id, token=auth_token)
    if account:
        contexts.tenant_id.set(account.current_tenant_id)
    return account


@login_manager.unauthorized_handler
def unauthorized_handler():
    """
    处理未授权的请求。
    """
    return Response(
        json.dumps({"code": "unauthorized", "message": "Unauthorized."}),
        status=401,
        content_type="application/json",
    )


# register blueprint routers
def register_blueprints(app):
    """
    注册所有蓝图路由。
    """
    from controllers.console import bp as console_app_bp
    from controllers.files import bp as files_bp
    from controllers.inner_api import bp as inner_api_bp
    from controllers.service_api import bp as service_api_bp
    from controllers.web import bp as web_bp

    CORS(
        service_api_bp,
        allow_headers=["Content-Type", "Authorization", "X-App-Code"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    )
    app.register_blueprint(service_api_bp)

    CORS(
        web_bp,
        resources={r"/*": {"origins": app.config["WEB_API_CORS_ALLOW_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-App-Code"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    app.register_blueprint(web_bp)

    CORS(
        console_app_bp,
        resources={r"/*": {"origins": app.config["CONSOLE_CORS_ALLOW_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    app.register_blueprint(console_app_bp)

    CORS(files_bp, allow_headers=["Content-Type"], methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"])
    app.register_blueprint(files_bp)

    app.register_blueprint(inner_api_bp)


# create app
app = create_app()
celery = app.extensions["celery"]

if app.config.get("TESTING"):
    print("App is running in TESTING mode")


@app.after_request
def after_request(response):
    """
    在请求结束后添加版本头到响应中。
    """
    response.set_cookie("remember_token", "", expires=0)
    response.headers.add("X-Version", app.config["CURRENT_VERSION"])
    response.headers.add("X-Env", app.config["DEPLOY_ENV"])
    return response


@app.route("/health")
def health():
    """
    健康检查路由，返回当前进程 ID 和应用版本。
    """
    return Response(
        json.dumps({"pid": os.getpid(), "status": "ok", "version": app.config["CURRENT_VERSION"]}),
        status=200,
        content_type="application/json",
    )


@app.route("/threads")
def threads():
    """
    返回当前进程的线程信息。
    """
    num_threads = threading.active_count()
    threads = threading.enumerate()

    thread_list = []
    for thread in threads:
        thread_name = thread.name
        thread_id = thread.ident
        is_alive = thread.is_alive()

        thread_list.append(
            {
                "name": thread_name,
                "id": thread_id,
                "is_alive": is_alive,
            }
        )

    return {
        "pid": os.getpid(),
        "thread_num": num_threads,
        "threads": thread_list,
    }


@app.route("/db-pool-stat")
def pool_stat():
    """
    返回数据库连接池的状态信息。
    """
    engine = db.engine
    return {
        "pid": os.getpid(),
        "pool_size": engine.pool.size(),
        "checked_in_connections": engine.pool.checkedin(),
        "checked_out_connections": engine.pool.checkedout(),
        "overflow_connections": engine.pool.overflow(),
        "connection_timeout": engine.pool.timeout(),
        "recycle_time": db.engine.pool._recycle,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

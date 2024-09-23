import openai
import sentry_sdk
from langfuse import parse_error
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException


def before_send(event, hint):
    """
    该函数用于在将事件发送到 Sentry 之前对其进行预处理。
    主要用途是检查异常信息，如果异常类型为 `parse_error.defaultErrorResponse`，则不发送该事件。

    参数:
    - event: 要发送到 Sentry 的事件对象。
    - hint: 包含异常信息的提示对象。

    返回值:
    - 如果异常类型为 `parse_error.defaultErrorResponse`，则返回 `None`，表示不发送该事件。
    - 否则返回 `event`，表示继续发送该事件。
    """
    # 检查提示对象中是否包含异常信息
    if "exc_info" in hint:
        # 获取异常类型、异常值和回溯信息
        exc_type, exc_value, tb = hint["exc_info"]
        # 检查异常值是否包含 `parse_error.defaultErrorResponse`
        if parse_error.defaultErrorResponse in str(exc_value):
            # 如果包含，则返回 `None`，表示不发送该事件
            return None

    # 如果不包含，则返回 `event`，表示继续发送该事件
    return event


def init_app(app):
    """
    该函数用于初始化 Sentry SDK，并配置相关参数。
    主要用途是将 Flask 和 Celery 集成到 Sentry 中，并设置忽略某些错误类型。

    参数:
    - app: Flask 应用程序对象。

    返回值:
    - 无返回值。
    """
    # 检查应用配置中是否存在 SENTRY_DSN
    if app.config.get("SENTRY_DSN"):
        # 初始化 Sentry SDK
        sentry_sdk.init(
            dsn=app.config.get("SENTRY_DSN"),  # Sentry 数据源名称
            integrations=[FlaskIntegration(), CeleryIntegration()],  # 集成 Flask 和 Celery
            ignore_errors=[HTTPException, ValueError, openai.APIStatusError, parse_error.defaultErrorResponse],  # 忽略的错误类型
            traces_sample_rate=app.config.get("SENTRY_TRACES_SAMPLE_RATE", 1.0),  # 跟踪采样率
            profiles_sample_rate=app.config.get("SENTRY_PROFILES_SAMPLE_RATE", 1.0),  # 性能分析采样率
            environment=app.config.get("DEPLOY_ENV"),  # 部署环境
            release=f"dify-{app.config.get('CURRENT_VERSION')}-{app.config.get('COMMIT_SHA')}",  # 发布版本
            before_send=before_send,  # 事件发送前的预处理函数
        )

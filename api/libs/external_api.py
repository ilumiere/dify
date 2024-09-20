import re
import sys

from flask import current_app, got_request_exception
from flask_restful import Api, http_status_message
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException

from core.errors.error import AppInvokeQuotaExceededError

# ExternalApi 继承了 flask_restful.Api 的所有功能，同时增加了自定义的错误处理逻辑。例如，它添加了对 AppInvokeQuotaExceededError 和 ValueError 的处理。它通过覆盖 handle_error 方法来定制错误处理行为，保证系统在面对不同类型的错误时返回合适的 HTTP 状态码和消息。
# 覆盖 handle_error 的原因通常包括以下几点：

# 统一的错误处理：可以为 API 请求中的所有错误提供一致的处理方式和响应格式。
# 自定义错误响应：可以根据业务需求，为不同类型的异常返回不同的 HTTP 状态码和详细的错误信息，而不是依赖默认的行为。
# 更好的日志记录：你可以在错误处理时记录更详细的异常信息，方便排查问题。
# 自定义响应头：可以在错误发生时修改或移除某些 HTTP 响应头，确保返回的响应符合预期的格式。

class ExternalApi(Api):
    """
    外部API类，继承自Flask-RESTful的Api类，主要用于处理API请求中的错误。
    """

    def handle_error(self, e):
        """
        错误处理函数，将引发的异常转换为Flask响应，包含适当的HTTP状态码和响应体。

        :param e: 引发的异常对象
        :type e: Exception
        :return: Flask响应对象
        :rtype: Response
        """
        # 发送请求异常信号，通知当前应用有异常发生
        got_request_exception.send(current_app, exception=e)

        # 初始化响应头
        headers = Headers()

        # 处理HTTP异常
        if isinstance(e, HTTPException):
            # 如果异常已经有响应对象，直接返回该响应
            if e.response is not None:
                resp = e.get_response()
                return resp

            # 获取异常的状态码
            status_code = e.code
            # 生成默认的响应数据
            default_data = {
                "code": re.sub(r"(?<!^)(?=[A-Z])", "_", type(e).__name__).lower(),
                "message": getattr(e, "description", http_status_message(status_code)),
                "status": status_code,
            }

            # 特殊处理JSON解码失败的错误信息
            if (
                default_data["message"]
                and default_data["message"] == "Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)"
            ):
                default_data["message"] = "Invalid JSON payload received or JSON payload is empty."

            # 获取异常的响应头
            headers = e.get_response().headers

        # 处理值错误
        elif isinstance(e, ValueError):
            status_code = 400
            default_data = {
                "code": "invalid_param",
                "message": str(e),
                "status": status_code,
            }

        # 处理应用调用配额超限错误
        elif isinstance(e, AppInvokeQuotaExceededError):
            status_code = 429
            default_data = {
                "code": "too_many_requests",
                "message": str(e),
                "status": status_code,
            }

        # 处理其他未知的错误
        else:
            status_code = 500
            default_data = {
                "message": http_status_message(status_code),
            }

        # Werkzeug exceptions generate a content-length header which is added
        # to the response in addition to the actual content-length header
        # https://github.com/flask-restful/flask-restful/issues/534
        # 移除Werkzeug异常生成的Content-Length头
        remove_headers = ("Content-Length",)

        for header in remove_headers:
            headers.pop(header, None)

        # 获取异常的自定义数据，如果没有则使用默认数据
        data = getattr(e, "data", default_data)

        # 如果异常类型在自定义错误列表中，更新响应数据
        error_cls_name = type(e).__name__
        if error_cls_name in self.errors:
            custom_data = self.errors.get(error_cls_name, {})
            custom_data = custom_data.copy()
            status_code = custom_data.get("status", 500)

            if "message" in custom_data:
                custom_data["message"] = custom_data["message"].format(
                    message=str(e.description if hasattr(e, "description") else e)
                )
            data.update(custom_data)

        # 记录服务器错误（状态码为500或更高）的异常信息
        if status_code and status_code >= 500:
            exc_info = sys.exc_info()
            if exc_info[1] is None:
                exc_info = None
            current_app.log_exception(exc_info)

        # 处理406 NotAcceptable错误
        if status_code == 406 and self.default_mediatype is None:
            # if we are handling NotAcceptable (406), make sure that
            # make_response uses a representation we support as the
            # default mediatype (so that make_response doesn't throw
            # another NotAcceptable error).
            supported_mediatypes = list(self.representations.keys())  # only supported application/json
            fallback_mediatype = supported_mediatypes[0] if supported_mediatypes else "text/plain"
            data = {"code": "not_acceptable", "message": data.get("message")}
            resp = self.make_response(data, status_code, headers, fallback_mediatype=fallback_mediatype)

        # 处理400 BadRequest错误
        elif status_code == 400:
            if isinstance(data.get("message"), dict):
                param_key, param_value = list(data.get("message").items())[0]
                data = {"code": "invalid_param", "message": param_value, "params": param_key}
            else:
                if "code" not in data:
                    data["code"] = "unknown"

            resp = self.make_response(data, status_code, headers)

        # 处理其他状态码的错误
        else:
            if "code" not in data:
                data["code"] = "unknown"

            resp = self.make_response(data, status_code, headers)

        # 处理401 Unauthorized错误
        if status_code == 401:
            resp = self.unauthorized(resp)

        return resp

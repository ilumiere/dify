import logging
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Union

from core.app.entities.app_invoke_entities import InvokeFrom
from core.app.entities.task_entities import AppBlockingResponse, AppStreamResponse
from core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, QuotaExceededError
from core.model_runtime.errors.invoke import InvokeError


class AppGenerateResponseConverter(ABC):
    """
    这是一个抽象基类，用于将应用程序生成的响应转换为不同的格式。
    主要用途是根据调用来源和响应类型，将阻塞响应或流式响应转换为适当的格式。
    """

    _blocking_response_type: type[AppBlockingResponse]
    """
    这是一个类属性，表示阻塞响应的类型。
    """

    @classmethod
    def convert(
        cls, response: Union[AppBlockingResponse, Generator[AppStreamResponse, Any, None]], invoke_from: InvokeFrom
    ) -> dict[str, Any] | Generator[str, Any, None]:
        """
        这是一个类方法，用于将应用程序生成的响应转换为适当的格式。

        参数:
        - response: 应用程序生成的响应，可以是阻塞响应或流式响应。
        - invoke_from: 调用来源，可以是调试器或服务API。

        返回值:
        - 如果响应是阻塞响应，返回一个字典；如果响应是流式响应，返回一个生成器。
        """
        if invoke_from in {InvokeFrom.DEBUGGER, InvokeFrom.SERVICE_API}:
            """
            如果调用来源是调试器或服务API，执行以下逻辑：
            """
            if isinstance(response, AppBlockingResponse):
                """
                如果响应是阻塞响应，调用 `convert_blocking_full_response` 方法进行转换。
                """
                return cls.convert_blocking_full_response(response)
            else:
                """
                如果响应是流式响应，定义一个生成器函数 `_generate_full_response` 进行转换。
                """
                def _generate_full_response() -> Generator[str, Any, None]:
                    """
                    生成器函数，用于将流式响应转换为完整响应格式。
                    """
                    for chunk in cls.convert_stream_full_response(response):
                        """
                        遍历流式响应的每个块，并根据块的内容生成相应的响应。
                        """
                        if chunk == "ping":
                            """
                            如果块内容是 "ping"，生成一个事件响应。
                            """
                            yield f"event: {chunk}\n\n"
                        else:
                            """
                            否则，生成一个数据响应。
                            """
                            yield f"data: {chunk}\n\n"

                return _generate_full_response()
        else:
            """
            如果调用来源不是调试器或服务API，执行以下逻辑：
            """
            if isinstance(response, AppBlockingResponse):
                """
                如果响应是阻塞响应，调用 `convert_blocking_simple_response` 方法进行转换。
                """
                return cls.convert_blocking_simple_response(response)
            else:
                """
                如果响应是流式响应，定义一个生成器函数 `_generate_simple_response` 进行转换。
                """
                def _generate_simple_response() -> Generator[str, Any, None]:
                    """
                    生成器函数，用于将流式响应转换为简单响应格式。
                    """
                    for chunk in cls.convert_stream_simple_response(response):
                        """
                        遍历流式响应的每个块，并根据块的内容生成相应的响应。
                        """
                        if chunk == "ping":
                            """
                            如果块内容是 "ping"，生成一个事件响应。
                            """
                            yield f"event: {chunk}\n\n"
                        else:
                            """
                            否则，生成一个数据响应。
                            """
                            yield f"data: {chunk}\n\n"

                return _generate_simple_response()

    @classmethod
    @abstractmethod
    def convert_blocking_full_response(cls, blocking_response: AppBlockingResponse) -> dict[str, Any]:
        """
        这是一个抽象类方法，用于将阻塞响应转换为完整响应格式。

        参数:
        - blocking_response: 阻塞响应对象。

        返回值:
        - 一个字典，表示转换后的完整响应。
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def convert_blocking_simple_response(cls, blocking_response: AppBlockingResponse) -> dict[str, Any]:
        """
        这是一个抽象类方法，用于将阻塞响应转换为简单响应格式。

        参数:
        - blocking_response: 阻塞响应对象。

        返回值:
        - 一个字典，表示转换后的简单响应。
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def convert_stream_full_response(
        cls, stream_response: Generator[AppStreamResponse, None, None]
    ) -> Generator[str, None, None]:
        """
        这是一个抽象类方法，用于将流式响应转换为完整响应格式。

        参数:
        - stream_response: 流式响应生成器。

        返回值:
        - 一个生成器，表示转换后的完整响应。
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def convert_stream_simple_response(
        cls, stream_response: Generator[AppStreamResponse, None, None]
    ) -> Generator[str, None, None]:
        """
        这是一个抽象类方法，用于将流式响应转换为简单响应格式。

        参数:
        - stream_response: 流式响应生成器。

        返回值:
        - 一个生成器，表示转换后的简单响应。
        """
        raise NotImplementedError

    @classmethod
    def _get_simple_metadata(cls, metadata: dict[str, Any]):
        """
        这是一个类方法，用于获取简化后的元数据。

        参数:
        - metadata: 原始元数据字典。

        返回值:
        - 简化后的元数据字典。
        """
        if "retriever_resources" in metadata:
            """
            如果元数据中包含 "retriever_resources" 字段，则对其进行简化处理。
            """
            metadata["retriever_resources"] = []
            for resource in metadata["retriever_resources"]:
                """
                遍历 "retriever_resources" 中的每个资源，并提取关键信息。
                """
                metadata["retriever_resources"].append(
                    {
                        "segment_id": resource["segment_id"],
                        "position": resource["position"],
                        "document_name": resource["document_name"],
                        "score": resource["score"],
                        "content": resource["content"],
                    }
                )

        if "annotation_reply" in metadata:
            """
            如果元数据中包含 "annotation_reply" 字段，则删除该字段。
            """
            del metadata["annotation_reply"]

        if "usage" in metadata:
            """
            如果元数据中包含 "usage" 字段，则删除该字段。
            """
            del metadata["usage"]

        return metadata

    @classmethod
    def _error_to_stream_response(cls, e: Exception) -> dict:
        """
        这是一个类方法，用于将异常转换为流式响应。

        参数:
        - e: 异常对象。

        返回值:
        - 一个字典，表示转换后的错误响应。
        """
        error_responses = {
            ValueError: {"code": "invalid_param", "status": 400},
            ProviderTokenNotInitError: {"code": "provider_not_initialize", "status": 400},
            QuotaExceededError: {
                "code": "provider_quota_exceeded",
                "message": "Your quota for Dify Hosted Model Provider has been exhausted. "
                "Please go to Settings -> Model Provider to complete your own provider credentials.",
                "status": 400,
            },
            ModelCurrentlyNotSupportError: {"code": "model_currently_not_support", "status": 400},
            InvokeError: {"code": "completion_request_error", "status": 400},
        }

        data = None
        for k, v in error_responses.items():
            """
            遍历预定义的错误响应字典，根据异常类型确定响应内容。
            """
            if isinstance(e, k):
                data = v

        if data:
            """
            如果找到了对应的错误响应，设置默认消息。
            """
            data.setdefault("message", getattr(e, "description", str(e)))
        else:
            """
            如果没有找到对应的错误响应，记录错误日志并返回内部服务器错误响应。
            """
            logging.error(e)
            data = {
                "code": "internal_server_error",
                "message": "Internal Server Error, please contact support.",
                "status": 500,
            }

        return data

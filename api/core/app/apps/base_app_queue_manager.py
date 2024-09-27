import queue
import time
from abc import abstractmethod
from collections.abc import Generator
from enum import Enum
from typing import Any

from sqlalchemy.orm import DeclarativeMeta

from configs import dify_config
from core.app.entities.app_invoke_entities import InvokeFrom
from core.app.entities.queue_entities import (
    AppQueueEvent,
    QueueErrorEvent,
    QueuePingEvent,
    QueueStopEvent,
)
from extensions.ext_redis import redis_client


class PublishFrom(Enum):
    """
    定义发布来源的枚举类。

    属性:
    - APPLICATION_MANAGER: 表示发布来源为应用程序管理器。
    - TASK_PIPELINE: 表示发布来源为任务管道。
    """
    APPLICATION_MANAGER = 1
    TASK_PIPELINE = 2


class AppQueueManager:
    """
    应用程序队列管理器类，负责管理任务队列的监听、发布和停止等操作。

    属性:
    - _task_id: 任务ID，类型为字符串。
    - _user_id: 用户ID，类型为字符串。
    - _invoke_from: 调用来源，类型为 InvokeFrom 枚举。
    - _q: 队列对象，类型为 queue.Queue。
    """

    def __init__(self, task_id: str, user_id: str, invoke_from: InvokeFrom) -> None:
        """
        初始化方法，用于创建 AppQueueManager 实例。

        参数:
        - task_id: 任务ID，类型为字符串。
        - user_id: 用户ID，类型为字符串。
        - invoke_from: 调用来源，类型为 InvokeFrom 枚举。

        异常:
        - ValueError: 如果 user_id 为空，抛出此异常。
        """
        if not user_id:
            raise ValueError("user is required")

        self._task_id = task_id
        self._user_id = user_id
        self._invoke_from = invoke_from

        user_prefix = "account" if self._invoke_from in {InvokeFrom.EXPLORE, InvokeFrom.DEBUGGER} else "end-user"
        redis_client.setex(
            AppQueueManager._generate_task_belong_cache_key(self._task_id), 1800, f"{user_prefix}-{self._user_id}"
        )

        q = queue.Queue()

        self._q = q

    def listen(self) -> Generator:
        """
        监听队列的方法，返回一个生成器。

        返回值:
        - 生成器，用于逐个返回队列中的消息。
        """
        # 等待 APP_MAX_EXECUTION_TIME 秒后停止监听
        listen_timeout = dify_config.APP_MAX_EXECUTION_TIME
        start_time = time.time()
        last_ping_time = 0
        while True:
            try:
                message = self._q.get(timeout=1)
                if message is None:
                    break

                yield message
            except queue.Empty:
                continue
            finally:
                elapsed_time = time.time() - start_time
                if elapsed_time >= listen_timeout or self._is_stopped():
                    # 发布两条消息以确保客户端能够接收到停止信号
                    # 并在处理完停止信号后停止监听
                    self.publish(
                        QueueStopEvent(stopped_by=QueueStopEvent.StopBy.USER_MANUAL), PublishFrom.TASK_PIPELINE
                    )

                if elapsed_time // 10 > last_ping_time:
                    self.publish(QueuePingEvent(), PublishFrom.TASK_PIPELINE)
                    last_ping_time = elapsed_time // 10

    def stop_listen(self) -> None:
        """
        停止监听队列的方法。

        返回值:
        - None
        """
        self._q.put(None)

    def publish_error(self, e, pub_from: PublishFrom) -> None:
        """
        发布错误消息的方法。

        参数:
        - e: 错误对象。
        - pub_from: 发布来源，类型为 PublishFrom 枚举。

        返回值:
        - None
        """
        self.publish(QueueErrorEvent(error=e), pub_from)

    def publish(self, event: AppQueueEvent, pub_from: PublishFrom) -> None:
        """
        发布事件到队列的方法。

        参数:
        - event: 事件对象，类型为 AppQueueEvent。
        - pub_from: 发布来源，类型为 PublishFrom 枚举。

        返回值:
        - None
        """
        self._check_for_sqlalchemy_models(event.model_dump())
        self._publish(event, pub_from)

    @abstractmethod
    def _publish(self, event: AppQueueEvent, pub_from: PublishFrom) -> None:
        """
        抽象方法，用于发布事件到队列。

        参数:
        - event: 事件对象，类型为 AppQueueEvent。
        - pub_from: 发布来源，类型为 PublishFrom 枚举。

        返回值:
        - None

        异常:
        - NotImplementedError: 如果子类未实现此方法，抛出此异常。
        """
        raise NotImplementedError

    @classmethod
    def set_stop_flag(cls, task_id: str, invoke_from: InvokeFrom, user_id: str) -> None:
        """
        设置任务停止标志的方法。

        参数:
        - task_id: 任务ID，类型为字符串。
        - invoke_from: 调用来源，类型为 InvokeFrom 枚举。
        - user_id: 用户ID，类型为字符串。

        返回值:
        - None
        """
        result = redis_client.get(cls._generate_task_belong_cache_key(task_id))
        if result is None:
            return

        user_prefix = "account" if invoke_from in {InvokeFrom.EXPLORE, InvokeFrom.DEBUGGER} else "end-user"
        if result.decode("utf-8") != f"{user_prefix}-{user_id}":
            return

        stopped_cache_key = cls._generate_stopped_cache_key(task_id)
        redis_client.setex(stopped_cache_key, 600, 1)

    def _is_stopped(self) -> bool:
        """
        检查任务是否已停止的方法。

        返回值:
        - 布尔值，表示任务是否已停止。
        """
        stopped_cache_key = AppQueueManager._generate_stopped_cache_key(self._task_id)
        result = redis_client.get(stopped_cache_key)
        if result is not None:
            return True

        return False

    @classmethod
    def _generate_task_belong_cache_key(cls, task_id: str) -> str:
        """
        生成任务所属缓存键的方法。

        参数:
        - task_id: 任务ID，类型为字符串。

        返回值:
        - 字符串，表示任务所属缓存键。
        """
        return f"generate_task_belong:{task_id}"

    @classmethod
    def _generate_stopped_cache_key(cls, task_id: str) -> str:
        """
        生成任务停止缓存键的方法。

        参数:
        - task_id: 任务ID，类型为字符串。

        返回值:
        - 字符串，表示任务停止缓存键。
        """
        return f"generate_task_stopped:{task_id}"

    def _check_for_sqlalchemy_models(self, data: Any):
        """
        检查数据中是否包含 SQLAlchemy 模型实例的方法。

        参数:
        - data: 需要检查的数据，类型为 Any。

        异常:
        - TypeError: 如果数据中包含 SQLAlchemy 模型实例，抛出此异常。
        """
        # 从实体转换为字典或列表
        if isinstance(data, dict):
            for key, value in data.items():
                self._check_for_sqlalchemy_models(value)
        elif isinstance(data, list):
            for item in data:
                self._check_for_sqlalchemy_models(item)
        else:
            if isinstance(data, DeclarativeMeta) or hasattr(data, "_sa_instance_state"):
                raise TypeError(
                    "Critical Error: Passing SQLAlchemy Model instances "
                    "that cause thread safety issues is not allowed."
                )


class GenerateTaskStoppedError(Exception):
    """
    生成任务停止错误的异常类。
    """
    pass

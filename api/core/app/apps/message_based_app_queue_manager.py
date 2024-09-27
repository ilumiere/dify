from core.app.apps.base_app_queue_manager import AppQueueManager, GenerateTaskStoppedError, PublishFrom
from core.app.entities.app_invoke_entities import InvokeFrom
from core.app.entities.queue_entities import (
    AppQueueEvent,
    MessageQueueMessage,
    QueueAdvancedChatMessageEndEvent,
    QueueErrorEvent,
    QueueMessage,
    QueueMessageEndEvent,
    QueueStopEvent,
)


class MessageBasedAppQueueManager(AppQueueManager):
    """
    消息基础应用程序队列管理器类，继承自 AppQueueManager。
    该类主要用于管理基于消息的应用程序队列，包括初始化、构造队列消息和发布事件到队列等操作。
    """

    def __init__(
        self, task_id: str, user_id: str, invoke_from: InvokeFrom, conversation_id: str, app_mode: str, message_id: str
    ) -> None:
        """
        初始化方法，用于创建 MessageBasedAppQueueManager 实例。

        参数:
        - task_id: 任务ID，类型为字符串。
        - user_id: 用户ID，类型为字符串。
        - invoke_from: 调用来源，类型为 InvokeFrom 枚举。
        - conversation_id: 对话ID，类型为字符串。
        - app_mode: 应用程序模式，类型为字符串。
        - message_id: 消息ID，类型为字符串。

        返回值:
        - None
        """
        super().__init__(task_id, user_id, invoke_from)  # 调用父类的初始化方法

        self._conversation_id = str(conversation_id)  # 将对话ID转换为字符串并赋值给私有属性
        self._app_mode = app_mode  # 将应用程序模式赋值给私有属性
        self._message_id = str(message_id)  # 将消息ID转换为字符串并赋值给私有属性

    def construct_queue_message(self, event: AppQueueEvent) -> QueueMessage:
        """
        构造队列消息的方法。

        参数:
        - event: 队列事件，类型为 AppQueueEvent。

        返回值:
        - 构造的队列消息，类型为 QueueMessage。
        """
        return MessageQueueMessage(
            task_id=self._task_id,  # 任务ID
            message_id=self._message_id,  # 消息ID
            conversation_id=self._conversation_id,  # 对话ID
            app_mode=self._app_mode,  # 应用程序模式
            event=event,  # 队列事件
        )

    def _publish(self, event: AppQueueEvent, pub_from: PublishFrom) -> None:
        """
        发布事件到队列的方法。

        参数:
        - event: 队列事件，类型为 AppQueueEvent。
        - pub_from: 发布来源，类型为 PublishFrom 枚举。

        返回值:
        - None
        """
        message = MessageQueueMessage(
            task_id=self._task_id,  # 任务ID
            message_id=self._message_id,  # 消息ID
            conversation_id=self._conversation_id,  # 对话ID
            app_mode=self._app_mode,  # 应用程序模式
            event=event,  # 队列事件
        )

        self._q.put(message)  # 将消息放入队列

        # 如果事件是停止事件、错误事件、消息结束事件或高级聊天消息结束事件，停止监听
        if isinstance(
            event, QueueStopEvent | QueueErrorEvent | QueueMessageEndEvent | QueueAdvancedChatMessageEndEvent
        ):
            self.stop_listen()

        # 如果发布来源是应用程序管理器且任务已停止，抛出 GenerateTaskStoppedError 异常
        if pub_from == PublishFrom.APPLICATION_MANAGER and self._is_stopped():
            raise GenerateTaskStoppedError()

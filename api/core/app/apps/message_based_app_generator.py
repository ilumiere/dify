import json
import logging
from collections.abc import Generator
from datetime import datetime, timezone
from typing import Optional, Union

from sqlalchemy import and_

from core.app.app_config.entities import EasyUIBasedAppModelConfigFrom
from core.app.apps.base_app_generator import BaseAppGenerator
from core.app.apps.base_app_queue_manager import AppQueueManager, GenerateTaskStoppedError
from core.app.entities.app_invoke_entities import (
    AdvancedChatAppGenerateEntity,
    AgentChatAppGenerateEntity,
    AppGenerateEntity,
    ChatAppGenerateEntity,
    CompletionAppGenerateEntity,
    InvokeFrom,
)
from core.app.entities.task_entities import (
    ChatbotAppBlockingResponse,
    ChatbotAppStreamResponse,
    CompletionAppBlockingResponse,
    CompletionAppStreamResponse,
)
from core.app.task_pipeline.easy_ui_based_generate_task_pipeline import EasyUIBasedGenerateTaskPipeline
from core.prompt.utils.prompt_template_parser import PromptTemplateParser
from extensions.ext_database import db
from models.account import Account
from models.model import App, AppMode, AppModelConfig, Conversation, EndUser, Message, MessageFile
from services.errors.app_model_config import AppModelConfigBrokenError
from services.errors.conversation import ConversationCompletedError, ConversationNotExistsError

logger = logging.getLogger(__name__)


class MessageBasedAppGenerator(BaseAppGenerator):
    """
    基于消息的应用程序生成器类，继承自 BaseAppGenerator。
    主要用途是处理应用程序生成的响应，并根据不同的生成实体类型进行相应的处理。
    """

    def _handle_response(
        self,
        application_generate_entity: Union[
            ChatAppGenerateEntity,
            CompletionAppGenerateEntity,
            AgentChatAppGenerateEntity,
            AdvancedChatAppGenerateEntity,
        ],
        queue_manager: AppQueueManager,
        conversation: Conversation,
        message: Message,
        user: Union[Account, EndUser],
        stream: bool = False,
    ) -> Union[
        ChatbotAppBlockingResponse,
        CompletionAppBlockingResponse,
        Generator[Union[ChatbotAppStreamResponse, CompletionAppStreamResponse], None, None],
    ]:
        """
        处理应用程序生成的响应。

        参数:
        - application_generate_entity: 应用程序生成实体，可以是 ChatAppGenerateEntity, CompletionAppGenerateEntity, AgentChatAppGenerateEntity, 或 AdvancedChatAppGenerateEntity。
        - queue_manager: 队列管理器，用于管理任务队列。
        - conversation: 对话对象，表示当前的对话。
        - message: 消息对象，表示当前的消息。
        - user: 用户对象，可以是 Account 或 EndUser。
        - stream: 是否为流式响应，默认为 False。

        返回值:
        - 如果 stream 为 False，返回 ChatbotAppBlockingResponse 或 CompletionAppBlockingResponse。
        - 如果 stream 为 True，返回一个生成器，生成 ChatbotAppStreamResponse 或 CompletionAppStreamResponse。
        """
        # 初始化生成任务管道
        generate_task_pipeline = EasyUIBasedGenerateTaskPipeline(
            application_generate_entity=application_generate_entity,
            queue_manager=queue_manager,
            conversation=conversation,
            message=message,
            user=user,
            stream=stream,
        )

        try:
            # 处理生成任务管道
            return generate_task_pipeline.process()
        except ValueError as e:
            # 捕获 ValueError 异常，如果是 "I/O operation on closed file." 错误，则抛出 GenerateTaskStoppedError
            if e.args[0] == "I/O operation on closed file.":
                raise GenerateTaskStoppedError()
            else:
                # 记录异常并重新抛出
                logger.exception(e)
                raise e

    def _get_conversation_by_user(
        self, app_model: App, conversation_id: str, user: Union[Account, EndUser]
    ) -> Conversation:
        """
        根据用户和对话ID获取对话对象。

        参数:
        - app_model: 应用程序模型对象。
        - conversation_id: 对话ID。
        - user: 用户对象，可以是 Account 或 EndUser。

        返回值:
        - 对话对象。

        异常:
        - ConversationNotExistsError: 如果对话不存在，抛出此异常。
        - ConversationCompletedError: 如果对话已完成，抛出此异常。
        """
        # 构建对话过滤条件
        conversation_filter = [
            Conversation.id == conversation_id,
            Conversation.app_id == app_model.id,
            Conversation.status == "normal",
        ]

        # 根据用户类型添加过滤条件
        if isinstance(user, Account):
            conversation_filter.append(Conversation.from_account_id == user.id)
        else:
            conversation_filter.append(Conversation.from_end_user_id == user.id if user else None)

        # 查询对话对象
        conversation = db.session.query(Conversation).filter(and_(*conversation_filter)).first()

        # 如果对话不存在，抛出异常
        if not conversation:
            raise ConversationNotExistsError()

        # 如果对话已完成，抛出异常
        if conversation.status != "normal":
            raise ConversationCompletedError()

        return conversation

    def _get_app_model_config(self, app_model: App, conversation: Optional[Conversation] = None) -> AppModelConfig:
        """
        获取应用程序模型配置。

        参数:
        - app_model: 应用程序模型对象。
        - conversation: 对话对象，可选。

        返回值:
        - 应用程序模型配置对象。

        异常:
        - AppModelConfigBrokenError: 如果应用程序模型配置不存在或损坏，抛出此异常。
        """
        if conversation:
            # 根据对话对象获取应用程序模型配置
            app_model_config = (
                db.session.query(AppModelConfig)
                .filter(AppModelConfig.id == conversation.app_model_config_id, AppModelConfig.app_id == app_model.id)
                .first()
            )

            # 如果应用程序模型配置不存在，抛出异常
            if not app_model_config:
                raise AppModelConfigBrokenError()
        else:
            # 如果对话对象不存在，直接从应用程序模型中获取配置
            if app_model.app_model_config_id is None:
                raise AppModelConfigBrokenError()

            app_model_config = app_model.app_model_config

            # 如果应用程序模型配置不存在，抛出异常
            if not app_model_config:
                raise AppModelConfigBrokenError()

        return app_model_config

    def _init_generate_records(
        self,
        application_generate_entity: Union[
            ChatAppGenerateEntity,
            CompletionAppGenerateEntity,
            AgentChatAppGenerateEntity,
            AdvancedChatAppGenerateEntity,
        ],
        conversation: Optional[Conversation] = None,
    ) -> tuple[Conversation, Message]:
        """
        初始化生成记录。

        参数:
        - application_generate_entity: 应用程序生成实体，可以是 ChatAppGenerateEntity, CompletionAppGenerateEntity, AgentChatAppGenerateEntity, 或 AdvancedChatAppGenerateEntity。
        - conversation: 对话对象，可选。

        返回值:
        - 包含对话对象和消息对象的元组。
        """
        app_config = application_generate_entity.app_config

        # 获取来源
        end_user_id = None
        account_id = None
        if application_generate_entity.invoke_from in {InvokeFrom.WEB_APP, InvokeFrom.SERVICE_API}:
            from_source = "api"
            end_user_id = application_generate_entity.user_id
        else:
            from_source = "console"
            account_id = application_generate_entity.user_id

        # 如果是 AdvancedChatAppGenerateEntity，设置相关配置为 None
        if isinstance(application_generate_entity, AdvancedChatAppGenerateEntity):
            app_model_config_id = None
            override_model_configs = None
            model_provider = None
            model_id = None
        else:
            app_model_config_id = app_config.app_model_config_id
            model_provider = application_generate_entity.model_conf.provider
            model_id = application_generate_entity.model_conf.model
            override_model_configs = None
            if app_config.app_model_config_from == EasyUIBasedAppModelConfigFrom.ARGS and app_config.app_mode in {
                AppMode.AGENT_CHAT,
                AppMode.CHAT,
                AppMode.COMPLETION,
            }:
                override_model_configs = app_config.app_model_config_dict

        # 获取对话介绍
        introduction = self._get_conversation_introduction(application_generate_entity)

        # 如果没有对话对象，创建新的对话对象
        if not conversation:
            conversation = Conversation(
                app_id=app_config.app_id,
                app_model_config_id=app_model_config_id,
                model_provider=model_provider,
                model_id=model_id,
                override_model_configs=json.dumps(override_model_configs) if override_model_configs else None,
                mode=app_config.app_mode.value,
                name="New conversation",
                inputs=application_generate_entity.inputs,
                introduction=introduction,
                system_instruction="",
                system_instruction_tokens=0,
                status="normal",
                invoke_from=application_generate_entity.invoke_from.value,
                from_source=from_source,
                from_end_user_id=end_user_id,
                from_account_id=account_id,
            )

            db.session.add(conversation)
            db.session.commit()
            db.session.refresh(conversation)
        else:
            # 更新对话对象的更新时间
            conversation.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db.session.commit()

        # 创建消息对象
        message = Message(
            app_id=app_config.app_id,
            model_provider=model_provider,
            model_id=model_id,
            override_model_configs=json.dumps(override_model_configs) if override_model_configs else None,
            conversation_id=conversation.id,
            inputs=application_generate_entity.inputs,
            query=application_generate_entity.query or "",
            message="",
            message_tokens=0,
            message_unit_price=0,
            message_price_unit=0,
            answer="",
            answer_tokens=0,
            answer_unit_price=0,
            answer_price_unit=0,
            provider_response_latency=0,
            total_price=0,
            currency="USD",
            invoke_from=application_generate_entity.invoke_from.value,
            from_source=from_source,
            from_end_user_id=end_user_id,
            from_account_id=account_id,
        )

        db.session.add(message)
        db.session.commit()
        db.session.refresh(message)

        # 处理文件
        for file in application_generate_entity.files:
            message_file = MessageFile(
                message_id=message.id,
                type=file.type.value,
                transfer_method=file.transfer_method.value,
                belongs_to="user",
                url=file.url,
                upload_file_id=file.related_id,
                created_by_role=("account" if account_id else "end_user"),
                created_by=account_id or end_user_id,
            )
            db.session.add(message_file)
            db.session.commit()

        return conversation, message

    def _get_conversation_introduction(self, application_generate_entity: AppGenerateEntity) -> str:
        """
        获取对话介绍。

        参数:
        - application_generate_entity: 应用程序生成实体。

        返回值:
        - 对话介绍字符串。
        """
        app_config = application_generate_entity.app_config
        introduction = app_config.additional_features.opening_statement

        # 如果存在对话介绍，尝试格式化
        if introduction:
            try:
                inputs = application_generate_entity.inputs
                prompt_template = PromptTemplateParser(template=introduction)
                prompt_inputs = {k: inputs[k] for k in prompt_template.variable_keys if k in inputs}
                introduction = prompt_template.format(prompt_inputs)
            except KeyError:
                pass

        return introduction

    def _get_conversation(self, conversation_id: str) -> Conversation:
        """
        根据对话ID获取对话对象。

        参数:
        - conversation_id: 对话ID。

        返回值:
        - 对话对象。

        异常:
        - ConversationNotExistsError: 如果对话不存在，抛出此异常。
        """
        conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()

        if not conversation:
            raise ConversationNotExistsError()

        return conversation

    def _get_message(self, message_id: str) -> Message:
        """
        根据消息ID获取消息对象。

        参数:
        - message_id: 消息ID。

        返回值:
        - 消息对象。
        """
        message = db.session.query(Message).filter(Message.id == message_id).first()

        return message

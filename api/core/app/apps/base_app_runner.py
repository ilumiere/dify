import time
from collections.abc import Generator, Mapping
from typing import TYPE_CHECKING, Any, Optional, Union

from core.app.app_config.entities import ExternalDataVariableEntity, PromptTemplateEntity
from core.app.apps.base_app_queue_manager import AppQueueManager, PublishFrom
from core.app.entities.app_invoke_entities import (
    AppGenerateEntity,
    EasyUIBasedAppGenerateEntity,
    InvokeFrom,
    ModelConfigWithCredentialsEntity,
)
from core.app.entities.queue_entities import QueueAgentMessageEvent, QueueLLMChunkEvent, QueueMessageEndEvent
from core.app.features.annotation_reply.annotation_reply import AnnotationReplyFeature
from core.app.features.hosting_moderation.hosting_moderation import HostingModerationFeature
from core.external_data_tool.external_data_fetch import ExternalDataFetch
from core.memory.token_buffer_memory import TokenBufferMemory
from core.model_manager import ModelInstance
from core.model_runtime.entities.llm_entities import LLMResult, LLMResultChunk, LLMResultChunkDelta, LLMUsage
from core.model_runtime.entities.message_entities import AssistantPromptMessage, PromptMessage
from core.model_runtime.entities.model_entities import ModelPropertyKey
from core.model_runtime.errors.invoke import InvokeBadRequestError
from core.moderation.input_moderation import InputModeration
from core.prompt.advanced_prompt_transform import AdvancedPromptTransform
from core.prompt.entities.advanced_prompt_entities import ChatModelMessage, CompletionModelPromptTemplate, MemoryConfig
from core.prompt.simple_prompt_transform import ModelMode, SimplePromptTransform
from models.model import App, AppMode, Message, MessageAnnotation

if TYPE_CHECKING:
    from core.file.file_obj import FileVar


class AppRunner:
    """
    该类负责应用程序的运行和管理，包括预计算剩余令牌、重新计算最大令牌、组织提示消息、直接输出结果、处理调用结果、输入审查、主机审查、填充外部数据工具输入以及查询应用程序注释以回复等功能。
    """

    def get_pre_calculate_rest_tokens(
        self,
        app_record: App,
        model_config: ModelConfigWithCredentialsEntity,
        prompt_template_entity: PromptTemplateEntity,
        inputs: dict[str, str],
        files: list["FileVar"],
        query: Optional[str] = None,
    ) -> int:
        """
        预计算剩余令牌数。

        :param app_record: 应用程序记录
        :param model_config: 模型配置实体
        :param prompt_template_entity: 提示模板实体
        :param inputs: 输入数据
        :param files: 文件列表
        :param query: 查询字符串，默认为None
        :return: 剩余令牌数
        """
        # 创建模型实例
        model_instance = ModelInstance(
            provider_model_bundle=model_config.provider_model_bundle, model=model_config.model
        )

        # 获取模型上下文令牌数
        model_context_tokens = model_config.model_schema.model_properties.get(ModelPropertyKey.CONTEXT_SIZE)

        # 初始化最大令牌数
        max_tokens = 0
        for parameter_rule in model_config.model_schema.parameter_rules:
            if parameter_rule.name == "max_tokens" or (
                parameter_rule.use_template and parameter_rule.use_template == "max_tokens"
            ):
                max_tokens = (
                    model_config.parameters.get(parameter_rule.name)
                    or model_config.parameters.get(parameter_rule.use_template)
                ) or 0

        # 如果模型上下文令牌数为None，返回-1
        if model_context_tokens is None:
            return -1

        # 如果最大令牌数为None，设置为0
        if max_tokens is None:
            max_tokens = 0

        # 获取不带记忆和上下文的提示消息
        prompt_messages, stop = self.organize_prompt_messages(
            app_record=app_record,
            model_config=model_config,
            prompt_template_entity=prompt_template_entity,
            inputs=inputs,
            files=files,
            query=query,
        )

        # 计算提示消息的令牌数
        prompt_tokens = model_instance.get_llm_num_tokens(prompt_messages)

        # 计算剩余令牌数
        rest_tokens = model_context_tokens - max_tokens - prompt_tokens
        if rest_tokens < 0:
            raise InvokeBadRequestError(
                "查询或前缀提示过长，可以减少前缀提示，缩小最大令牌数，或切换到令牌限制更大的模型。"
            )

        return rest_tokens

    def recalc_llm_max_tokens(
        self, model_config: ModelConfigWithCredentialsEntity, prompt_messages: list[PromptMessage]
    ):
        """
        重新计算最大令牌数，如果提示令牌数加上最大令牌数超过模型令牌限制。

        :param model_config: 模型配置实体
        :param prompt_messages: 提示消息列表
        """
        # 创建模型实例
        model_instance = ModelInstance(
            provider_model_bundle=model_config.provider_model_bundle, model=model_config.model
        )

        # 获取模型上下文令牌数
        model_context_tokens = model_config.model_schema.model_properties.get(ModelPropertyKey.CONTEXT_SIZE)

        # 初始化最大令牌数
        max_tokens = 0
        for parameter_rule in model_config.model_schema.parameter_rules:
            if parameter_rule.name == "max_tokens" or (
                parameter_rule.use_template and parameter_rule.use_template == "max_tokens"
            ):
                max_tokens = (
                    model_config.parameters.get(parameter_rule.name)
                    or model_config.parameters.get(parameter_rule.use_template)
                ) or 0

        # 如果模型上下文令牌数为None，返回-1
        if model_context_tokens is None:
            return -1

        # 如果最大令牌数为None，设置为0
        if max_tokens is None:
            max_tokens = 0

        # 计算提示消息的令牌数
        prompt_tokens = model_instance.get_llm_num_tokens(prompt_messages)

        # 如果提示令牌数加上最大令牌数超过模型令牌限制，重新计算最大令牌数
        if prompt_tokens + max_tokens > model_context_tokens:
            max_tokens = max(model_context_tokens - prompt_tokens, 16)

            for parameter_rule in model_config.model_schema.parameter_rules:
                if parameter_rule.name == "max_tokens" or (
                    parameter_rule.use_template and parameter_rule.use_template == "max_tokens"
                ):
                    model_config.parameters[parameter_rule.name] = max_tokens

    def organize_prompt_messages(
        self,
        app_record: App,
        model_config: ModelConfigWithCredentialsEntity,
        prompt_template_entity: PromptTemplateEntity,
        inputs: dict[str, str],
        files: list["FileVar"],
        query: Optional[str] = None,
        context: Optional[str] = None,
        memory: Optional[TokenBufferMemory] = None,
    ) -> tuple[list[PromptMessage], Optional[list[str]]]:
        """
        组织提示消息。

        :param app_record: 应用程序记录
        :param model_config: 模型配置实体
        :param prompt_template_entity: 提示模板实体
        :param inputs: 输入数据
        :param files: 文件列表
        :param query: 查询字符串，默认为None
        :param context: 上下文字符串，默认为None
        :param memory: 记忆对象，默认为None
        :return: 提示消息列表和停止条件列表
        """
        # 获取不带记忆和上下文的提示消息
        if prompt_template_entity.prompt_type == PromptTemplateEntity.PromptType.SIMPLE:
            prompt_transform = SimplePromptTransform()
            prompt_messages, stop = prompt_transform.get_prompt(
                app_mode=AppMode.value_of(app_record.mode),
                prompt_template_entity=prompt_template_entity,
                inputs=inputs,
                query=query or "",
                files=files,
                context=context,
                memory=memory,
                model_config=model_config,
            )
        else:
            memory_config = MemoryConfig(window=MemoryConfig.WindowConfig(enabled=False))

            model_mode = ModelMode.value_of(model_config.mode)
            if model_mode == ModelMode.COMPLETION:
                advanced_completion_prompt_template = prompt_template_entity.advanced_completion_prompt_template
                prompt_template = CompletionModelPromptTemplate(text=advanced_completion_prompt_template.prompt)

                if advanced_completion_prompt_template.role_prefix:
                    memory_config.role_prefix = MemoryConfig.RolePrefix(
                        user=advanced_completion_prompt_template.role_prefix.user,
                        assistant=advanced_completion_prompt_template.role_prefix.assistant,
                    )
            else:
                prompt_template = []
                for message in prompt_template_entity.advanced_chat_prompt_template.messages:
                    prompt_template.append(ChatModelMessage(text=message.text, role=message.role))

            prompt_transform = AdvancedPromptTransform()
            prompt_messages = prompt_transform.get_prompt(
                prompt_template=prompt_template,
                inputs=inputs,
                query=query or "",
                files=files,
                context=context,
                memory_config=memory_config,
                memory=memory,
                model_config=model_config,
            )
            stop = model_config.stop

        return prompt_messages, stop

    def direct_output(
        self,
        queue_manager: AppQueueManager,
        app_generate_entity: EasyUIBasedAppGenerateEntity,
        prompt_messages: list,
        text: str,
        stream: bool,
        usage: Optional[LLMUsage] = None,
    ) -> None:
        """
        直接输出结果。

        :param queue_manager: 应用程序队列管理器
        :param app_generate_entity: 应用程序生成实体
        :param prompt_messages: 提示消息列表
        :param text: 文本内容
        :param stream: 是否流式输出
        :param usage: 使用情况，默认为None
        """
        if stream:
            index = 0
            for token in text:
                chunk = LLMResultChunk(
                    model=app_generate_entity.model_conf.model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(index=index, message=AssistantPromptMessage(content=token)),
                )

                queue_manager.publish(QueueLLMChunkEvent(chunk=chunk), PublishFrom.APPLICATION_MANAGER)
                index += 1
                time.sleep(0.01)

        queue_manager.publish(
            QueueMessageEndEvent(
                llm_result=LLMResult(
                    model=app_generate_entity.model_conf.model,
                    prompt_messages=prompt_messages,
                    message=AssistantPromptMessage(content=text),
                    usage=usage or LLMUsage.empty_usage(),
                ),
            ),
            PublishFrom.APPLICATION_MANAGER,
        )

    def _handle_invoke_result(
        self,
        invoke_result: Union[LLMResult, Generator],
        queue_manager: AppQueueManager,
        stream: bool,
        agent: bool = False,
    ) -> None:
        """
        处理调用结果。

        :param invoke_result: 调用结果
        :param queue_manager: 应用程序队列管理器
        :param stream: 是否流式输出
        :param agent: 是否为代理，默认为False
        """
        if not stream:
            self._handle_invoke_result_direct(invoke_result=invoke_result, queue_manager=queue_manager, agent=agent)
        else:
            self._handle_invoke_result_stream(invoke_result=invoke_result, queue_manager=queue_manager, agent=agent)

    def _handle_invoke_result_direct(
        self, invoke_result: LLMResult, queue_manager: AppQueueManager, agent: bool
    ) -> None:
        """
        直接处理调用结果。

        :param invoke_result: 调用结果
        :param queue_manager: 应用程序队列管理器
        :param agent: 是否为代理
        """
        queue_manager.publish(
            QueueMessageEndEvent(
                llm_result=invoke_result,
            ),
            PublishFrom.APPLICATION_MANAGER,
        )

    def _handle_invoke_result_stream(
        self, invoke_result: Generator, queue_manager: AppQueueManager, agent: bool
    ) -> None:
        """
        流式处理调用结果。

        :param invoke_result: 调用结果
        :param queue_manager: 应用程序队列管理器
        :param agent: 是否为代理
        """
        model = None
        prompt_messages = []
        text = ""
        usage = None
        for result in invoke_result:
            if not agent:
                queue_manager.publish(QueueLLMChunkEvent(chunk=result), PublishFrom.APPLICATION_MANAGER)
            else:
                queue_manager.publish(QueueAgentMessageEvent(chunk=result), PublishFrom.APPLICATION_MANAGER)

            text += result.delta.message.content

            if not model:
                model = result.model

            if not prompt_messages:
                prompt_messages = result.prompt_messages

            if not usage and result.delta.usage:
                usage = result.delta.usage

        if not usage:
            usage = LLMUsage.empty_usage()

        llm_result = LLMResult(
            model=model, prompt_messages=prompt_messages, message=AssistantPromptMessage(content=text), usage=usage
        )

        queue_manager.publish(
            QueueMessageEndEvent(
                llm_result=llm_result,
            ),
            PublishFrom.APPLICATION_MANAGER,
        )

    def moderation_for_inputs(
        self,
        app_id: str,
        tenant_id: str,
        app_generate_entity: AppGenerateEntity,
        inputs: Mapping[str, Any],
        query: str,
        message_id: str,
    ) -> tuple[bool, dict, str]:
        """
        处理输入的敏感词审查。

        :param app_id: 应用程序ID
        :param tenant_id: 租户ID
        :param app_generate_entity: 应用程序生成实体
        :param inputs: 输入数据
        :param query: 查询字符串
        :param message_id: 消息ID
        :return: 审查结果、审查数据和审查消息
        """
        moderation_feature = InputModeration()
        return moderation_feature.check(
            app_id=app_id,
            tenant_id=tenant_id,
            app_config=app_generate_entity.app_config,
            inputs=inputs,
            query=query or "",
            message_id=message_id,
            trace_manager=app_generate_entity.trace_manager,
        )

    def check_hosting_moderation(
        self,
        application_generate_entity: EasyUIBasedAppGenerateEntity,
        queue_manager: AppQueueManager,
        prompt_messages: list[PromptMessage],
    ) -> bool:
        """
        检查主机审查。

        :param application_generate_entity: 应用程序生成实体
        :param queue_manager: 队列管理器
        :param prompt_messages: 提示消息列表
        :return: 审查结果
        """
        hosting_moderation_feature = HostingModerationFeature()
        moderation_result = hosting_moderation_feature.check(
            application_generate_entity=application_generate_entity, prompt_messages=prompt_messages
        )

        if moderation_result:
            self.direct_output(
                queue_manager=queue_manager,
                app_generate_entity=application_generate_entity,
                prompt_messages=prompt_messages,
                text="I apologize for any confusion, but I'm an AI assistant to be helpful, harmless, and honest.",
                stream=application_generate_entity.stream,
            )

        return moderation_result

    def fill_in_inputs_from_external_data_tools(
        self,
        tenant_id: str,
        app_id: str,
        external_data_tools: list[ExternalDataVariableEntity],
        inputs: dict,
        query: str,
    ) -> dict:
        """
        从外部数据工具填充变量输入（如果存在）。

        :param tenant_id: 工作区ID
        :param app_id: 应用程序ID
        :param external_data_tools: 外部数据工具配置
        :param inputs: 输入数据
        :param query: 查询字符串
        :return: 填充后的输入数据
        """
        external_data_fetch_feature = ExternalDataFetch()
        return external_data_fetch_feature.fetch(
            tenant_id=tenant_id, app_id=app_id, external_data_tools=external_data_tools, inputs=inputs, query=query
        )

    def query_app_annotations_to_reply(
        self, app_record: App, message: Message, query: str, user_id: str, invoke_from: InvokeFrom
    ) -> Optional[MessageAnnotation]:
        """
        查询应用程序注释以回复。

        :param app_record: 应用程序记录
        :param message: 消息
        :param query: 查询字符串
        :param user_id: 用户ID
        :param invoke_from: 调用来源
        :return: 消息注释
        """
        annotation_reply_feature = AnnotationReplyFeature()
        return annotation_reply_feature.query(
            app_record=app_record, message=message, query=query, user_id=user_id, invoke_from=invoke_from
        )

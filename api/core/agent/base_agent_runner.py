import json
import logging
import uuid
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Optional, Union, cast

from core.agent.entities import AgentEntity, AgentToolEntity
from core.app.app_config.features.file_upload.manager import FileUploadConfigManager
from core.app.apps.agent_chat.app_config_manager import AgentChatAppConfig
from core.app.apps.base_app_queue_manager import AppQueueManager
from core.app.apps.base_app_runner import AppRunner
from core.app.entities.app_invoke_entities import (
    AgentChatAppGenerateEntity,
    ModelConfigWithCredentialsEntity,
)
from core.callback_handler.agent_tool_callback_handler import DifyAgentCallbackHandler
from core.callback_handler.index_tool_callback_handler import DatasetIndexToolCallbackHandler
from core.file.message_file_parser import MessageFileParser
from core.memory.token_buffer_memory import TokenBufferMemory
from core.model_manager import ModelInstance
from core.model_runtime.entities.llm_entities import LLMUsage
from core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    PromptMessage,
    PromptMessageTool,
    SystemPromptMessage,
    TextPromptMessageContent,
    ToolPromptMessage,
    UserPromptMessage,
)
from core.model_runtime.entities.model_entities import ModelFeature
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from core.model_runtime.utils.encoders import jsonable_encoder
from core.tools.entities.tool_entities import (
    ToolParameter,
    ToolRuntimeVariablePool,
)
from core.tools.tool.dataset_retriever_tool import DatasetRetrieverTool
from core.tools.tool.tool import Tool
from core.tools.tool_manager import ToolManager
from core.tools.utils.tool_parameter_converter import ToolParameterConverter
from extensions.ext_database import db
from models.model import Conversation, Message, MessageAgentThought
from models.tools import ToolConversationVariables

logger = logging.getLogger(__name__)


class BaseAgentRunner(AppRunner):
    """
    BaseAgentRunner 类是用于管理和执行代理运行的基类。它继承自 AppRunner，并负责初始化代理运行所需的各种参数和工具。
    """

    def __init__(
        self,
        tenant_id: str,
        application_generate_entity: AgentChatAppGenerateEntity,
        conversation: Conversation,
        app_config: AgentChatAppConfig,
        model_config: ModelConfigWithCredentialsEntity,
        config: AgentEntity,
        queue_manager: AppQueueManager,
        message: Message,
        user_id: str,
        memory: Optional[TokenBufferMemory] = None,
        prompt_messages: Optional[list[PromptMessage]] = None,
        variables_pool: Optional[ToolRuntimeVariablePool] = None,
        db_variables: Optional[ToolConversationVariables] = None,
        model_instance: ModelInstance = None,
    ) -> None:
        """
        初始化 BaseAgentRunner 实例。

        :param tenant_id: 租户ID，标识租户的唯一字符串。
        :param application_generate_entity: 应用生成实体，包含应用生成的相关信息。
        :param conversation: 对话对象，包含当前对话的所有信息。
        :param app_config: 应用配置对象，包含应用的配置信息。
        :param model_config: 模型配置对象，包含模型的配置信息。
        :param config: 数据集配置对象，包含数据集的配置信息。
        :param queue_manager: 队列管理器对象，用于管理任务队列。
        :param message: 消息对象，包含当前消息的所有信息。
        :param user_id: 用户ID，标识用户的唯一字符串。
        :param memory: 可选参数，内存对象，用于存储和管理内存数据。
        :param prompt_messages: 可选参数，提示消息列表，包含所有提示消息。
        :param variables_pool: 可选参数，变量池对象，用于存储和管理变量。
        :param db_variables: 可选参数，数据库变量对象，用于存储和管理数据库变量。
        :param model_instance: 可选参数，模型实例对象，用于存储和管理模型实例。
        """
        self.tenant_id = tenant_id
        self.application_generate_entity = application_generate_entity
        self.conversation = conversation
        self.app_config = app_config
        self.model_config = model_config
        self.config = config
        self.queue_manager = queue_manager
        self.message = message
        self.user_id = user_id
        self.memory = memory
        self.history_prompt_messages = self.organize_agent_history(prompt_messages=prompt_messages or [])
        self.variables_pool = variables_pool
        self.db_variables_pool = db_variables
        self.model_instance = model_instance

        # 初始化回调处理程序
        self.agent_callback = DifyAgentCallbackHandler()
        # 初始化数据集工具
        hit_callback = DatasetIndexToolCallbackHandler(
            queue_manager=queue_manager,
            app_id=self.app_config.app_id,
            message_id=message.id,
            user_id=user_id,
            invoke_from=self.application_generate_entity.invoke_from,
        )
        self.dataset_tools = DatasetRetrieverTool.get_dataset_tools(
            tenant_id=tenant_id,
            dataset_ids=app_config.dataset.dataset_ids if app_config.dataset else [],
            retrieve_config=app_config.dataset.retrieve_config if app_config.dataset else None,
            return_resource=app_config.additional_features.show_retrieve_source,
            invoke_from=application_generate_entity.invoke_from,
            hit_callback=hit_callback,
        )
        # 获取已创建的代理思考数量
        self.agent_thought_count = (
            db.session.query(MessageAgentThought)
            .filter(
                MessageAgentThought.message_id == self.message.id,
            )
            .count()
        )
        db.session.close()

        # 检查模型是否支持流式工具调用
        llm_model = cast(LargeLanguageModel, model_instance.model_type_instance)
        model_schema = llm_model.get_model_schema(model_instance.model, model_instance.credentials)
        if model_schema and ModelFeature.STREAM_TOOL_CALL in (model_schema.features or []):
            self.stream_tool_call = True
        else:
            self.stream_tool_call = False

        # 检查模型是否支持视觉功能
        if model_schema and ModelFeature.VISION in (model_schema.features or []):
            self.files = application_generate_entity.files
        else:
            self.files = []
        self.query = None
        self._current_thoughts: list[PromptMessage] = []

    def _repack_app_generate_entity(
        self, app_generate_entity: AgentChatAppGenerateEntity
    ) -> AgentChatAppGenerateEntity:
        """
        重新打包应用生成实体。

        如果应用生成实体的简单提示模板为空，则将其设置为空字符串。

        :param app_generate_entity: 应用生成实体对象。
        :return: 重新打包后的应用生成实体对象。
        """
        if app_generate_entity.app_config.prompt_template.simple_prompt_template is None:
            app_generate_entity.app_config.prompt_template.simple_prompt_template = ""

        return app_generate_entity

    def _convert_tool_to_prompt_message_tool(self, tool: AgentToolEntity) -> tuple[PromptMessageTool, Tool]:
        """
        将工具转换为提示消息工具。

        获取工具的运行时参数，并将其转换为提示消息工具的参数格式。

        :param tool: 工具实体对象。
        :return: 包含提示消息工具和工具实体的元组。
        """
        tool_entity = ToolManager.get_agent_tool_runtime(
            tenant_id=self.tenant_id,
            app_id=self.app_config.app_id,
            agent_tool=tool,
            invoke_from=self.application_generate_entity.invoke_from,
        )
        tool_entity.load_variables(self.variables_pool)

        message_tool = PromptMessageTool(
            name=tool.tool_name,
            description=tool_entity.description.llm,
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )

        parameters = tool_entity.get_all_runtime_parameters()
        for parameter in parameters:
            if parameter.form != ToolParameter.ToolParameterForm.LLM:
                continue

            parameter_type = ToolParameterConverter.get_parameter_type(parameter.type)
            enum = []
            if parameter.type == ToolParameter.ToolParameterType.SELECT:
                enum = [option.value for option in parameter.options]

            message_tool.parameters["properties"][parameter.name] = {
                "type": parameter_type,
                "description": parameter.llm_description or "",
            }

            if len(enum) > 0:
                message_tool.parameters["properties"][parameter.name]["enum"] = enum

            if parameter.required:
                message_tool.parameters["required"].append(parameter.name)

        return message_tool, tool_entity

    def _convert_dataset_retriever_tool_to_prompt_message_tool(self, tool: DatasetRetrieverTool) -> PromptMessageTool:
        """
        将数据集检索工具转换为提示消息工具。

        获取数据集检索工具的运行时参数，并将其转换为提示消息工具的参数格式。

        :param tool: 数据集检索工具对象。
        :return: 提示消息工具对象。
        """
        prompt_tool = PromptMessageTool(
            name=tool.identity.name,
            description=tool.description.llm,
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )

        for parameter in tool.get_runtime_parameters():
            parameter_type = "string"

            prompt_tool.parameters["properties"][parameter.name] = {
                "type": parameter_type,
                "description": parameter.llm_description or "",
            }

            if parameter.required:
                if parameter.name not in prompt_tool.parameters["required"]:
                    prompt_tool.parameters["required"].append(parameter.name)

        return prompt_tool

    def _init_prompt_tools(self) -> tuple[Mapping[str, Tool], Sequence[PromptMessageTool]]:
        """
        初始化提示工具。

        遍历应用配置中的工具和数据集工具，将其转换为提示消息工具，并保存工具实例和提示消息工具。

        :return: 包含工具实例映射和提示消息工具序列的元组。
        """
        tool_instances = {}
        prompt_messages_tools = []

        for tool in self.app_config.agent.tools if self.app_config.agent else []:
            try:
                prompt_tool, tool_entity = self._convert_tool_to_prompt_message_tool(tool)
            except Exception:
                # 工具可能已被删除
                continue
            # 保存工具实体
            tool_instances[tool.tool_name] = tool_entity
            # 保存提示工具
            prompt_messages_tools.append(prompt_tool)

        # 将数据集工具转换为 ModelRuntime 工具格式
        for dataset_tool in self.dataset_tools:
            prompt_tool = self._convert_dataset_retriever_tool_to_prompt_message_tool(dataset_tool)
            # 保存提示工具
            prompt_messages_tools.append(prompt_tool)
            # 保存工具实体
            tool_instances[dataset_tool.identity.name] = dataset_tool

        return tool_instances, prompt_messages_tools

    def update_prompt_message_tool(self, tool: Tool, prompt_tool: PromptMessageTool) -> PromptMessageTool:
        """
        更新提示消息工具。

        获取工具的运行时参数，并更新提示消息工具的参数。

        :param tool: 工具对象。
        :param prompt_tool: 提示消息工具对象。
        :return: 更新后的提示消息工具对象。
        """
        # 尝试获取工具运行时参数
        tool_runtime_parameters = tool.get_runtime_parameters() or []

        for parameter in tool_runtime_parameters:
            if parameter.form != ToolParameter.ToolParameterForm.LLM:
                continue

            parameter_type = ToolParameterConverter.get_parameter_type(parameter.type)
            enum = []
            if parameter.type == ToolParameter.ToolParameterType.SELECT:
                enum = [option.value for option in parameter.options]

            prompt_tool.parameters["properties"][parameter.name] = {
                "type": parameter_type,
                "description": parameter.llm_description or "",
            }

            if len(enum) > 0:
                prompt_tool.parameters["properties"][parameter.name]["enum"] = enum

            if parameter.required:
                if parameter.name not in prompt_tool.parameters["required"]:
                    prompt_tool.parameters["required"].append(parameter.name)

        return prompt_tool

    def create_agent_thought(
        self, message_id: str, message: str, tool_name: str, tool_input: str, messages_ids: list[str]
    ) -> MessageAgentThought:
        """
        创建代理思考。

        创建一个新的代理思考对象，并将其保存到数据库中。

        :param message_id: 消息ID，标识消息的唯一字符串。
        :param message: 消息内容，包含消息的文本内容。
        :param tool_name: 工具名称，标识工具的唯一字符串。
        :param tool_input: 工具输入，包含工具的输入数据。
        :param messages_ids: 消息文件ID列表，包含消息文件的唯一ID。
        :return: 创建的代理思考对象。
        """
        thought = MessageAgentThought(
            message_id=message_id,
            message_chain_id=None,
            thought="",
            tool=tool_name,
            tool_labels_str="{}",
            tool_meta_str="{}",
            tool_input=tool_input,
            message=message,
            message_token=0,
            message_unit_price=0,
            message_price_unit=0,
            message_files=json.dumps(messages_ids) if messages_ids else "",
            answer="",
            observation="",
            answer_token=0,
            answer_unit_price=0,
            answer_price_unit=0,
            tokens=0,
            total_price=0,
            position=self.agent_thought_count + 1,
            currency="USD",
            latency=0,
            created_by_role="account",
            created_by=self.user_id,
        )

        db.session.add(thought)
        db.session.commit()
        db.session.refresh(thought)
        db.session.close()

        self.agent_thought_count += 1

        return thought

    def save_agent_thought(
        self,
        agent_thought: MessageAgentThought,
        tool_name: str,
        tool_input: Union[str, dict],
        thought: str,
        observation: Union[str, dict],
        tool_invoke_meta: Union[str, dict],
        answer: str,
        messages_ids: list[str],
        llm_usage: LLMUsage = None,
    ) -> MessageAgentThought:
        """
        保存代理思考。

        更新代理思考对象的属性，并将其保存到数据库中。

        :param agent_thought: 代理思考对象。
        :param tool_name: 工具名称，标识工具的唯一字符串。
        :param tool_input: 工具输入，包含工具的输入数据。
        :param thought: 思考内容，包含代理的思考内容。
        :param observation: 观察内容，包含代理的观察结果。
        :param tool_invoke_meta: 工具调用元数据，包含工具调用的元数据。
        :param answer: 回答内容，包含代理的回答内容。
        :param messages_ids: 消息文件ID列表，包含消息文件的唯一ID。
        :param llm_usage: 可选参数，LLM使用情况对象，包含LLM的使用情况。
        :return: 更新后的代理思考对象。
        """
        agent_thought = db.session.query(MessageAgentThought).filter(MessageAgentThought.id == agent_thought.id).first()

        if thought is not None:
            agent_thought.thought = thought

        if tool_name is not None:
            agent_thought.tool = tool_name

        if tool_input is not None:
            if isinstance(tool_input, dict):
                try:
                    tool_input = json.dumps(tool_input, ensure_ascii=False)
                except Exception as e:
                    tool_input = json.dumps(tool_input)

            agent_thought.tool_input = tool_input

        if observation is not None:
            if isinstance(observation, dict):
                try:
                    observation = json.dumps(observation, ensure_ascii=False)
                except Exception as e:
                    observation = json.dumps(observation)

            agent_thought.observation = observation

        if answer is not None:
            agent_thought.answer = answer

        if messages_ids is not None and len(messages_ids) > 0:
            agent_thought.message_files = json.dumps(messages_ids)

        if llm_usage:
            agent_thought.message_token = llm_usage.prompt_tokens
            agent_thought.message_price_unit = llm_usage.prompt_price_unit
            agent_thought.message_unit_price = llm_usage.prompt_unit_price
            agent_thought.answer_token = llm_usage.completion_tokens
            agent_thought.answer_price_unit = llm_usage.completion_price_unit
            agent_thought.answer_unit_price = llm_usage.completion_unit_price
            agent_thought.tokens = llm_usage.total_tokens
            agent_thought.total_price = llm_usage.total_price

        # 检查工具标签是否为空
        labels = agent_thought.tool_labels or {}
        tools = agent_thought.tool.split(";") if agent_thought.tool else []
        for tool in tools:
            if not tool:
                continue
            if tool not in labels:
                tool_label = ToolManager.get_tool_label(tool)
                if tool_label:
                    labels[tool] = tool_label.to_dict()
                else:
                    labels[tool] = {"en_US": tool, "zh_Hans": tool}

        agent_thought.tool_labels_str = json.dumps(labels)

        if tool_invoke_meta is not None:
            if isinstance(tool_invoke_meta, dict):
                try:
                    tool_invoke_meta = json.dumps(tool_invoke_meta, ensure_ascii=False)
                except Exception as e:
                    tool_invoke_meta = json.dumps(tool_invoke_meta)

            agent_thought.tool_meta_str = tool_invoke_meta

        db.session.commit()
        db.session.close()

    def update_db_variables(self, tool_variables: ToolRuntimeVariablePool, db_variables: ToolConversationVariables):
        """
        convert tool variables to db variables
        """
        db_variables = (
            db.session.query(ToolConversationVariables)
            .filter(
                ToolConversationVariables.conversation_id == self.message.conversation_id,
            )
            .first()
        )

        db_variables.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db_variables.variables_str = json.dumps(jsonable_encoder(tool_variables.pool))
        db.session.commit()
        db.session.close()

    def organize_agent_history(self, prompt_messages: list[PromptMessage]) -> list[PromptMessage]:
        """
        组织代理历史记录。

        该函数的主要用途是根据给定的提示消息列表和数据库中的消息记录，组织并返回一个包含系统消息、用户消息、助手消息和工具调用消息的列表。

        参数:
        - prompt_messages: 提示消息列表，包含系统消息和其他提示消息。

        返回值:
        - 返回一个包含组织后的提示消息的列表。
        """
        result = []
        # 检查对话开始时是否有系统消息
        for prompt_message in prompt_messages:
            if isinstance(prompt_message, SystemPromptMessage):
                result.append(prompt_message)

        # 从数据库中查询与当前对话相关的所有消息，并按创建时间升序排列
        messages: list[Message] = (
            db.session.query(Message)
            .filter(
                Message.conversation_id == self.message.conversation_id,
            )
            .order_by(Message.created_at.asc())
            .all()
        )

        # 遍历所有消息
        for message in messages:
            # 跳过当前消息
            if message.id == self.message.id:
                continue

            # 将用户消息添加到结果列表中
            result.append(self.organize_agent_user_prompt(message))
            # 获取消息的代理思考记录
            agent_thoughts: list[MessageAgentThought] = message.agent_thoughts
            if agent_thoughts:
                for agent_thought in agent_thoughts:
                    tools = agent_thought.tool
                    if tools:
                        # 将工具名称按分号分割
                        tools = tools.split(";")
                        tool_calls: list[AssistantPromptMessage.ToolCall] = []
                        tool_call_response: list[ToolPromptMessage] = []
                        try:
                            # 尝试解析工具输入
                            tool_inputs = json.loads(agent_thought.tool_input)
                        except Exception as e:
                            # 如果解析失败，为每个工具创建一个空输入
                            tool_inputs = {tool: {} for tool in tools}
                        try:
                            # 尝试解析工具响应
                            tool_responses = json.loads(agent_thought.observation)
                        except Exception as e:
                            # 如果解析失败，为每个工具创建一个默认响应
                            tool_responses = dict.fromkeys(tools, agent_thought.observation)

                        for tool in tools:
                            # 为工具调用生成一个UUID
                            tool_call_id = str(uuid.uuid4())
                            tool_calls.append(
                                AssistantPromptMessage.ToolCall(
                                    id=tool_call_id,
                                    type="function",
                                    function=AssistantPromptMessage.ToolCall.ToolCallFunction(
                                        name=tool,
                                        arguments=json.dumps(tool_inputs.get(tool, {})),
                                    ),
                                )
                            )
                            tool_call_response.append(
                                ToolPromptMessage(
                                    content=tool_responses.get(tool, agent_thought.observation),
                                    name=tool,
                                    tool_call_id=tool_call_id,
                                )
                            )

                        # 将助手消息和工具调用响应添加到结果列表中
                        result.extend(
                            [
                                AssistantPromptMessage(
                                    content=agent_thought.thought,
                                    tool_calls=tool_calls,
                                ),
                                *tool_call_response,
                            ]
                        )
                    if not tools:
                        # 如果没有工具，直接添加助手消息
                        result.append(AssistantPromptMessage(content=agent_thought.thought))
            else:
                # 如果没有代理思考记录，直接添加助手消息
                if message.answer:
                    result.append(AssistantPromptMessage(content=message.answer))

        # 关闭数据库会话
        db.session.close()

        return result

    def organize_agent_user_prompt(self, message: Message) -> UserPromptMessage:
        """
        组织用户提示消息。

        该函数的主要用途是根据给定的消息对象，生成并返回一个包含用户提示消息的对象。

        参数:
        - message: 消息对象，包含用户查询和相关文件信息。

        返回值:
        - 返回一个包含用户提示消息的对象。
        """
        # 创建消息文件解析器
        message_file_parser = MessageFileParser(
            tenant_id=self.tenant_id,
            app_id=self.app_config.app_id,
        )

        # 获取消息中的文件列表
        files = message.message_files
        if files:
            # 转换文件上传配置
            file_extra_config = FileUploadConfigManager.convert(message.app_model_config.to_dict())

            if file_extra_config:
                # 转换消息文件
                file_objs = message_file_parser.transform_message_files(files, file_extra_config)
            else:
                file_objs = []

            if not file_objs:
                # 如果没有文件对象，直接返回用户查询
                return UserPromptMessage(content=message.query)
            else:
                # 创建包含文本和文件内容的提示消息内容列表
                prompt_message_contents = [TextPromptMessageContent(data=message.query)]
                for file_obj in file_objs:
                    prompt_message_contents.append(file_obj.prompt_message_content)

                return UserPromptMessage(content=prompt_message_contents)
        else:
            # 如果没有文件，直接返回用户查询
            return UserPromptMessage(content=message.query)

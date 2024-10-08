from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from core.model_runtime.entities.llm_entities import LLMUsage
from models import WorkflowNodeExecutionStatus


class NodeType(Enum):
    """
    节点类型枚举类。

    该类定义了工作流中可能出现的各种节点类型。每个节点类型都有一个对应的字符串值。
    """

    START = "start"  # 开始节点
    END = "end"  # 结束节点
    ANSWER = "answer"  # 回答节点
    LLM = "llm"  # 语言模型节点
    KNOWLEDGE_RETRIEVAL = "knowledge-retrieval"  # 知识检索节点
    IF_ELSE = "if-else"  # 条件判断节点
    CODE = "code"  # 代码执行节点
    TEMPLATE_TRANSFORM = "template-transform"  # 模板转换节点
    QUESTION_CLASSIFIER = "question-classifier"  # 问题分类节点
    HTTP_REQUEST = "http-request"  # HTTP请求节点
    TOOL = "tool"  # 工具节点
    VARIABLE_AGGREGATOR = "variable-aggregator"  # 变量聚合节点
    # TODO: 将此节点合并到 VARIABLE_AGGREGATOR
    VARIABLE_ASSIGNER = "variable-assigner"  # 变量赋值节点
    LOOP = "loop"  # 循环节点
    ITERATION = "iteration"  # 迭代节点
    ITERATION_START = "iteration-start"  # 迭代的伪开始节点
    PARAMETER_EXTRACTOR = "parameter-extractor"  # 参数提取节点
    CONVERSATION_VARIABLE_ASSIGNER = "assigner"  # 对话变量赋值节点

    @classmethod
    def value_of(cls, value: str) -> "NodeType":
        """
        根据给定的节点类型值获取对应的节点类型枚举。

        :param value: 节点类型的字符串值
        :return: 对应的节点类型枚举
        :raises ValueError: 如果提供的值无效
        """
        for node_type in cls:
            if node_type.value == value:
                return node_type
        raise ValueError(f"无效的节点类型值 {value}")


class NodeRunMetadataKey(Enum):
    """
    节点运行元数据键枚举类。

    该类定义了节点运行时可能记录的各种元数据键。
    """

    TOTAL_TOKENS = "total_tokens"  # 总令牌数
    TOTAL_PRICE = "total_price"  # 总价格
    CURRENCY = "currency"  # 货币类型
    TOOL_INFO = "tool_info"  # 工具信息
    ITERATION_ID = "iteration_id"  # 迭代ID
    ITERATION_INDEX = "iteration_index"  # 迭代索引
    PARALLEL_ID = "parallel_id"  # 并行ID
    PARALLEL_START_NODE_ID = "parallel_start_node_id"  # 并行开始节点ID
    PARENT_PARALLEL_ID = "parent_parallel_id"  # 父并行ID
    PARENT_PARALLEL_START_NODE_ID = "parent_parallel_start_node_id"  # 父并行开始节点ID


class NodeRunResult(BaseModel):
    """
    节点运行结果类。

    该类定义了节点运行后的结果结构，包括状态、输入、处理数据、输出、元数据、LLM使用情况、错误信息等。
    """

    status: WorkflowNodeExecutionStatus = WorkflowNodeExecutionStatus.RUNNING  # 节点执行状态

    inputs: Optional[dict[str, Any]] = None  # 节点输入
    process_data: Optional[dict[str, Any]] = None  # 处理数据
    outputs: Optional[dict[str, Any]] = None  # 节点输出
    metadata: Optional[dict[NodeRunMetadataKey, Any]] = None  # 节点元数据
    llm_usage: Optional[LLMUsage] = None  # LLM使用情况

    edge_source_handle: Optional[str] = None  # 多分支节点的源句柄ID

    error: Optional[str] = None  # 错误信息，如果状态为失败


class UserFrom(Enum):
    """
    用户来源枚举类。

    该类定义了用户的来源类型。
    """

    ACCOUNT = "account"  # 账户用户
    END_USER = "end-user"  # 终端用户

    @classmethod
    def value_of(cls, value: str) -> "UserFrom":
        """
        根据给定的值获取对应的用户来源枚举。

        :param value: 用户来源的字符串值
        :return: 对应的用户来源枚举
        :raises ValueError: 如果提供的值无效
        """
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"无效的值: {value}")

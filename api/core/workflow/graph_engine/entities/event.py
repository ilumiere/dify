from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from core.workflow.entities.base_node_data_entities import BaseNodeData
from core.workflow.entities.node_entities import NodeType
from core.workflow.graph_engine.entities.runtime_route_state import RouteNodeState


class GraphEngineEvent(BaseModel):
    """
    图引擎事件的基类，继承自 Pydantic 的 BaseModel。
    该类作为所有图引擎事件的基类，定义了事件的基本结构和行为。
    """
    pass


###########################################
# Graph Events
###########################################


class BaseGraphEvent(GraphEngineEvent):
    """
    图事件的基类，继承自 GraphEngineEvent。
    该类定义了所有图事件的通用属性和方法。
    """
    pass


class GraphRunStartedEvent(BaseGraphEvent):
    """
    图运行开始事件，继承自 BaseGraphEvent。
    该事件表示图的运行已经开始。
    """
    pass


class GraphRunSucceededEvent(BaseGraphEvent):
    """
    图运行成功事件，继承自 BaseGraphEvent。
    该事件表示图的运行已经成功完成，并包含输出的数据。
    """
    outputs: Optional[dict[str, Any]] = None
    """
    图运行成功后的输出数据，类型为字典，键为字符串，值为任意类型。
    """


class GraphRunFailedEvent(BaseGraphEvent):
    """
    图运行失败事件，继承自 BaseGraphEvent。
    该事件表示图的运行失败，并包含失败的原因。
    """
    error: str = Field(..., description="failed reason")
    """
    图运行失败的原因，类型为字符串。
    """


###########################################
# Node Events
###########################################

# ... 是 Python 中的一个特殊语法，表示“省略号”。
# 在 Pydantic 中，Field(..., ) 表示该字段是必需的，并且没有默认值。
class BaseNodeEvent(GraphEngineEvent):
    """
    节点事件的基类，继承自 GraphEngineEvent。
    该类定义了所有节点事件的通用属性和方法。
    """
    id: str = Field(..., description="node execution id")
    """
    节点执行的唯一标识符，类型为字符串。
    """
    node_id: str = Field(..., description="node id")
    """
    节点的唯一标识符，类型为字符串。
    """
    node_type: NodeType = Field(..., description="node type")
    """
    节点的类型，类型为 NodeType。
    """
    node_data: BaseNodeData = Field(..., description="node data")
    """
    节点的数据，类型为 BaseNodeData。
    """
    route_node_state: RouteNodeState = Field(..., description="route node state")
    """
    路由节点的状态，类型为 RouteNodeState。
    """
    parallel_id: Optional[str] = None
    """
    并行节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parallel_start_node_id: Optional[str] = None
    """
    并行起始节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parent_parallel_id: Optional[str] = None
    """
    父并行节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parent_parallel_start_node_id: Optional[str] = None
    """
    父并行起始节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    in_iteration_id: Optional[str] = None
    """
    迭代节点的唯一标识符，类型为字符串，如果节点不在迭代中则为 None。
    """


class NodeRunStartedEvent(BaseNodeEvent):
    """
    节点运行开始事件，继承自 BaseNodeEvent。
    该事件表示节点的运行已经开始。
    """
    predecessor_node_id: Optional[str] = None
    """
    前驱节点的唯一标识符，类型为字符串，如果节点没有前驱节点则为 None。
    """


class NodeRunStreamChunkEvent(BaseNodeEvent):
    """
    节点运行流块事件，继承自 BaseNodeEvent。
    该事件表示节点运行过程中产生的流块。
    """
    chunk_content: str = Field(..., description="chunk content")
    """
    流块的内容，类型为字符串。
    """
    from_variable_selector: Optional[list[str]] = None
    """
    从变量选择器中选择的变量列表，类型为字符串列表，如果未选择变量则为 None。
    """


class NodeRunRetrieverResourceEvent(BaseNodeEvent):
    """
    节点运行资源检索事件，继承自 BaseNodeEvent。
    该事件表示节点运行过程中检索到的资源。
    """
    retriever_resources: list[dict] = Field(..., description="retriever resources")
    """
    检索到的资源列表，类型为字典列表。
    """
    context: str = Field(..., description="context")
    """
    检索资源时的上下文信息，类型为字符串。
    """


class NodeRunSucceededEvent(BaseNodeEvent):
    """
    节点运行成功事件，继承自 BaseNodeEvent。
    该事件表示节点的运行已经成功完成。
    """
    pass


class NodeRunFailedEvent(BaseNodeEvent):
    """
    节点运行失败事件，继承自 BaseNodeEvent。
    该事件表示节点的运行失败，并包含失败的原因。
    """
    error: str = Field(..., description="error")
    """
    节点运行失败的原因，类型为字符串。
    """


###########################################
# Parallel Branch Events
###########################################


class BaseParallelBranchEvent(GraphEngineEvent):
    """
    并行分支事件的基类，继承自 GraphEngineEvent。
    该类定义了所有并行分支事件的通用属性和方法。
    """
    parallel_id: str = Field(..., description="parallel id")
    """
    并行分支的唯一标识符，类型为字符串。
    """
    parallel_start_node_id: str = Field(..., description="parallel start node id")
    """
    并行起始节点的唯一标识符，类型为字符串。
    """
    parent_parallel_id: Optional[str] = None
    """
    父并行分支的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parent_parallel_start_node_id: Optional[str] = None
    """
    父并行起始节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    in_iteration_id: Optional[str] = None
    """
    迭代节点的唯一标识符，类型为字符串，如果节点不在迭代中则为 None。
    """


class ParallelBranchRunStartedEvent(BaseParallelBranchEvent):
    """
    并行分支运行开始事件，继承自 BaseParallelBranchEvent。
    该事件表示并行分支的运行已经开始。
    """
    pass


class ParallelBranchRunSucceededEvent(BaseParallelBranchEvent):
    """
    并行分支运行成功事件，继承自 BaseParallelBranchEvent。
    该事件表示并行分支的运行已经成功完成。
    """
    pass


class ParallelBranchRunFailedEvent(BaseParallelBranchEvent):
    """
    并行分支运行失败事件，继承自 BaseParallelBranchEvent。
    该事件表示并行分支的运行失败，并包含失败的原因。
    """
    error: str = Field(..., description="failed reason")
    """
    并行分支运行失败的原因，类型为字符串。
    """


###########################################
# Iteration Events
###########################################


class BaseIterationEvent(GraphEngineEvent):
    """
    迭代事件的基类，继承自 GraphEngineEvent。
    该类定义了所有迭代事件的通用属性和方法。
    """
    iteration_id: str = Field(..., description="iteration node execution id")
    """
    迭代节点的执行唯一标识符，类型为字符串。
    """
    iteration_node_id: str = Field(..., description="iteration node id")
    """
    迭代节点的唯一标识符，类型为字符串。
    """
    iteration_node_type: NodeType = Field(..., description="node type, iteration or loop")
    """
    迭代节点的类型，类型为 NodeType。
    """
    iteration_node_data: BaseNodeData = Field(..., description="node data")
    """
    迭代节点的数据，类型为 BaseNodeData。
    """
    parallel_id: Optional[str] = None
    """
    并行节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parallel_start_node_id: Optional[str] = None
    """
    并行起始节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parent_parallel_id: Optional[str] = None
    """
    父并行节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """
    parent_parallel_start_node_id: Optional[str] = None
    """
    父并行起始节点的唯一标识符，类型为字符串，如果节点不在并行中则为 None。
    """


class IterationRunStartedEvent(BaseIterationEvent):
    """
    迭代运行开始事件，继承自 BaseIterationEvent。
    该事件表示迭代的运行已经开始。
    """
    start_at: datetime = Field(..., description="start at")
    """
    迭代开始的时间，类型为 datetime。
    """
    inputs: Optional[dict[str, Any]] = None
    """
    迭代的输入数据，类型为字典，键为字符串，值为任意类型。
    """
    metadata: Optional[dict[str, Any]] = None
    """
    迭代的元数据，类型为字典，键为字符串，值为任意类型。
    """
    predecessor_node_id: Optional[str] = None
    """
    前驱节点的唯一标识符，类型为字符串，如果节点没有前驱节点则为 None。
    """


class IterationRunNextEvent(BaseIterationEvent):
    """
    迭代运行下一步事件，继承自 BaseIterationEvent。
    该事件表示迭代的下一步运行。
    """
    index: int = Field(..., description="index")
    """
    迭代的当前索引，类型为整数。
    """
    pre_iteration_output: Optional[Any] = Field(None, description="pre iteration output")
    """
    上一次迭代的输出，类型为任意类型。
    """


class IterationRunSucceededEvent(BaseIterationEvent):
    """
    迭代运行成功事件，继承自 BaseIterationEvent。
    该事件表示迭代的运行已经成功完成。
    """
    start_at: datetime = Field(..., description="start at")
    """
    迭代开始的时间，类型为 datetime。
    """
    inputs: Optional[dict[str, Any]] = None
    """
    迭代的输入数据，类型为字典，键为字符串，值为任意类型。
    """
    outputs: Optional[dict[str, Any]] = None
    """
    迭代的输出数据，类型为字典，键为字符串，值为任意类型。
    """
    metadata: Optional[dict[str, Any]] = None
    """
    迭代的元数据，类型为字典，键为字符串，值为任意类型。
    """
    steps: int = 0
    """
    迭代的步数，类型为整数。
    """


class IterationRunFailedEvent(BaseIterationEvent):
    """
    迭代运行失败事件，继承自 BaseIterationEvent。
    该事件表示迭代的运行失败，并包含失败的原因。
    """
    start_at: datetime = Field(..., description="start at")
    """
    迭代开始的时间，类型为 datetime。
    """
    inputs: Optional[dict[str, Any]] = None
    """
    迭代的输入数据，类型为字典，键为字符串，值为任意类型。
    """
    outputs: Optional[dict[str, Any]] = None
    """
    迭代的输出数据，类型为字典，键为字符串，值为任意类型。
    """
    metadata: Optional[dict[str, Any]] = None
    """
    迭代的元数据，类型为字典，键为字符串，值为任意类型。
    """
    steps: int = 0
    """
    迭代的步数，类型为整数。
    """
    error: str = Field(..., description="failed reason")
    """
    迭代运行失败的原因，类型为字符串。
    """


InNodeEvent = BaseNodeEvent | BaseParallelBranchEvent | BaseIterationEvent
"""
节点事件的联合类型，包括 BaseNodeEvent、BaseParallelBranchEvent 和 BaseIterationEvent。
"""

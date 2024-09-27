from collections.abc import Mapping
from typing import Any, Optional, cast

from core.app.apps.base_app_queue_manager import AppQueueManager, PublishFrom
from core.app.apps.base_app_runner import AppRunner
from core.app.entities.queue_entities import (
    AppQueueEvent,
    QueueIterationCompletedEvent,
    QueueIterationNextEvent,
    QueueIterationStartEvent,
    QueueNodeFailedEvent,
    QueueNodeStartedEvent,
    QueueNodeSucceededEvent,
    QueueParallelBranchRunFailedEvent,
    QueueParallelBranchRunStartedEvent,
    QueueParallelBranchRunSucceededEvent,
    QueueRetrieverResourcesEvent,
    QueueTextChunkEvent,
    QueueWorkflowFailedEvent,
    QueueWorkflowStartedEvent,
    QueueWorkflowSucceededEvent,
)
from core.workflow.entities.node_entities import NodeType
from core.workflow.entities.variable_pool import VariablePool
from core.workflow.graph_engine.entities.event import (
    GraphEngineEvent,
    GraphRunFailedEvent,
    GraphRunStartedEvent,
    GraphRunSucceededEvent,
    IterationRunFailedEvent,
    IterationRunNextEvent,
    IterationRunStartedEvent,
    IterationRunSucceededEvent,
    NodeRunFailedEvent,
    NodeRunRetrieverResourceEvent,
    NodeRunStartedEvent,
    NodeRunStreamChunkEvent,
    NodeRunSucceededEvent,
    ParallelBranchRunFailedEvent,
    ParallelBranchRunStartedEvent,
    ParallelBranchRunSucceededEvent,
)
from core.workflow.graph_engine.entities.graph import Graph
from core.workflow.nodes.base_node import BaseNode
from core.workflow.nodes.iteration.entities import IterationNodeData
from core.workflow.nodes.node_mapping import node_classes
from core.workflow.workflow_entry import WorkflowEntry
from extensions.ext_database import db
from models.model import App
from models.workflow import Workflow


class WorkflowBasedAppRunner(AppRunner):
    """
    基于工作流的App运行器类，继承自AppRunner。主要用于管理和执行工作流相关的操作。
    """

    def __init__(self, queue_manager: AppQueueManager):
        """
        初始化方法，设置队列管理器。

        :param queue_manager: 队列管理器对象，用于发布事件。
        """
        self.queue_manager = queue_manager

    def _init_graph(self, graph_config: Mapping[str, Any]) -> Graph:
        """
        初始化工作流图。

        :param graph_config: 图配置，包含节点和边的信息。
        :return: 初始化后的图对象。
        :raises ValueError: 如果配置中缺少节点或边，或者节点和边不是列表类型，则抛出异常。
        """
        # 检查配置中是否包含节点和边
        if "nodes" not in graph_config or "edges" not in graph_config:
            raise ValueError("nodes or edges not found in workflow graph")

        # 检查节点是否为列表类型
        if not isinstance(graph_config.get("nodes"), list):
            raise ValueError("nodes in workflow graph must be a list")

        # 检查边是否为列表类型
        if not isinstance(graph_config.get("edges"), list):
            raise ValueError("edges in workflow graph must be a list")

        # 初始化图
        graph = Graph.init(graph_config=graph_config)

        # 检查图是否成功初始化
        if not graph:
            raise ValueError("graph not found in workflow")

        return graph

    def _get_graph_and_variable_pool_of_single_iteration(
        self,
        workflow: Workflow,
        node_id: str,
        user_inputs: dict,
    ) -> tuple[Graph, VariablePool]:
        """
        获取单次迭代的图和变量池。

        :param workflow: 工作流对象。
        :param node_id: 节点ID。
        :param user_inputs: 用户输入。
        :return: 图对象和变量池对象的元组。
        :raises ValueError: 如果工作流图中缺少节点或边，或者节点和边不是列表类型，则抛出异常。
        """
        # 获取工作流图配置
        graph_config = workflow.graph_dict
        if not graph_config:
            raise ValueError("workflow graph not found")

        graph_config = cast(dict[str, Any], graph_config)

        # 检查配置中是否包含节点和边
        if "nodes" not in graph_config or "edges" not in graph_config:
            raise ValueError("nodes or edges not found in workflow graph")

        # 检查节点是否为列表类型
        if not isinstance(graph_config.get("nodes"), list):
            raise ValueError("nodes in workflow graph must be a list")

        # 检查边是否为列表类型
        if not isinstance(graph_config.get("edges"), list):
            raise ValueError("edges in workflow graph must be a list")

        # 过滤出迭代中的节点
        node_configs = [
            node
            for node in graph_config.get("nodes", [])
            if node.get("id") == node_id or node.get("data", {}).get("iteration_id", "") == node_id
        ]

        graph_config["nodes"] = node_configs

        node_ids = [node.get("id") for node in node_configs]

        # 过滤出迭代中的边
        edge_configs = [
            edge
            for edge in graph_config.get("edges", [])
            if (edge.get("source") is None or edge.get("source") in node_ids)
            and (edge.get("target") is None or edge.get("target") in node_ids)
        ]

        graph_config["edges"] = edge_configs

        # 初始化图
        graph = Graph.init(graph_config=graph_config, root_node_id=node_id)

        if not graph:
            raise ValueError("graph not found in workflow")

        # 根据节点ID获取节点配置
        iteration_node_config = None
        for node in node_configs:
            if node.get("id") == node_id:
                iteration_node_config = node
                break

        if not iteration_node_config:
            raise ValueError("iteration node id not found in workflow graph")

        # 获取节点类
        node_type = NodeType.value_of(iteration_node_config.get("data", {}).get("type"))
        node_cls = node_classes.get(node_type)
        node_cls = cast(type[BaseNode], node_cls)

        # 初始化变量池
        variable_pool = VariablePool(
            system_variables={},
            user_inputs={},
            environment_variables=workflow.environment_variables,
        )

        try:
            variable_mapping = node_cls.extract_variable_selector_to_variable_mapping(
                graph_config=workflow.graph_dict, config=iteration_node_config
            )
        except NotImplementedError:
            variable_mapping = {}

        WorkflowEntry.mapping_user_inputs_to_variable_pool(
            variable_mapping=variable_mapping,
            user_inputs=user_inputs,
            variable_pool=variable_pool,
            tenant_id=workflow.tenant_id,
            node_type=node_type,
            node_data=IterationNodeData(**iteration_node_config.get("data", {})),
        )

        return graph, variable_pool

    def _handle_event(self, workflow_entry: WorkflowEntry, event: GraphEngineEvent) -> None:
        """
        处理事件。

        :param workflow_entry: 工作流入口对象。
        :param event: 事件对象。
        """
        # 根据事件类型发布相应的事件
        if isinstance(event, GraphRunStartedEvent):
            self._publish_event(
                QueueWorkflowStartedEvent(graph_runtime_state=workflow_entry.graph_engine.graph_runtime_state)
            )
        elif isinstance(event, GraphRunSucceededEvent):
            self._publish_event(QueueWorkflowSucceededEvent(outputs=event.outputs))
        elif isinstance(event, GraphRunFailedEvent):
            self._publish_event(QueueWorkflowFailedEvent(error=event.error))
        elif isinstance(event, NodeRunStartedEvent):
            self._publish_event(
                QueueNodeStartedEvent(
                    node_execution_id=event.id,
                    node_id=event.node_id,
                    node_type=event.node_type,
                    node_data=event.node_data,
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    start_at=event.route_node_state.start_at,
                    node_run_index=event.route_node_state.index,
                    predecessor_node_id=event.predecessor_node_id,
                    in_iteration_id=event.in_iteration_id,
                )
            )
        elif isinstance(event, NodeRunSucceededEvent):
            self._publish_event(
                QueueNodeSucceededEvent(
                    node_execution_id=event.id,
                    node_id=event.node_id,
                    node_type=event.node_type,
                    node_data=event.node_data,
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    start_at=event.route_node_state.start_at,
                    inputs=event.route_node_state.node_run_result.inputs
                    if event.route_node_state.node_run_result
                    else {},
                    process_data=event.route_node_state.node_run_result.process_data
                    if event.route_node_state.node_run_result
                    else {},
                    outputs=event.route_node_state.node_run_result.outputs
                    if event.route_node_state.node_run_result
                    else {},
                    execution_metadata=event.route_node_state.node_run_result.metadata
                    if event.route_node_state.node_run_result
                    else {},
                    in_iteration_id=event.in_iteration_id,
                )
            )
        elif isinstance(event, NodeRunFailedEvent):
            self._publish_event(
                QueueNodeFailedEvent(
                    node_execution_id=event.id,
                    node_id=event.node_id,
                    node_type=event.node_type,
                    node_data=event.node_data,
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    start_at=event.route_node_state.start_at,
                    inputs=event.route_node_state.node_run_result.inputs
                    if event.route_node_state.node_run_result
                    else {},
                    process_data=event.route_node_state.node_run_result.process_data
                    if event.route_node_state.node_run_result
                    else {},
                    outputs=event.route_node_state.node_run_result.outputs
                    if event.route_node_state.node_run_result
                    else {},
                    error=event.route_node_state.node_run_result.error
                    if event.route_node_state.node_run_result and event.route_node_state.node_run_result.error
                    else "Unknown error",
                    in_iteration_id=event.in_iteration_id,
                )
            )
        elif isinstance(event, NodeRunStreamChunkEvent):
            self._publish_event(
                QueueTextChunkEvent(
                    text=event.chunk_content,
                    from_variable_selector=event.from_variable_selector,
                    in_iteration_id=event.in_iteration_id,
                )
            )
        elif isinstance(event, NodeRunRetrieverResourceEvent):
            self._publish_event(
                QueueRetrieverResourcesEvent(
                    retriever_resources=event.retriever_resources, in_iteration_id=event.in_iteration_id
                )
            )
        elif isinstance(event, ParallelBranchRunStartedEvent):
            self._publish_event(
                QueueParallelBranchRunStartedEvent(
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    in_iteration_id=event.in_iteration_id,
                )
            )
        elif isinstance(event, ParallelBranchRunSucceededEvent):
            self._publish_event(
                QueueParallelBranchRunSucceededEvent(
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    in_iteration_id=event.in_iteration_id,
                )
            )
        elif isinstance(event, ParallelBranchRunFailedEvent):
            self._publish_event(
                QueueParallelBranchRunFailedEvent(
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    in_iteration_id=event.in_iteration_id,
                    error=event.error,
                )
            )
        elif isinstance(event, IterationRunStartedEvent):
            self._publish_event(
                QueueIterationStartEvent(
                    node_execution_id=event.iteration_id,
                    node_id=event.iteration_node_id,
                    node_type=event.iteration_node_type,
                    node_data=event.iteration_node_data,
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    start_at=event.start_at,
                    node_run_index=workflow_entry.graph_engine.graph_runtime_state.node_run_steps,
                    inputs=event.inputs,
                    predecessor_node_id=event.predecessor_node_id,
                    metadata=event.metadata,
                )
            )
        elif isinstance(event, IterationRunNextEvent):
            self._publish_event(
                QueueIterationNextEvent(
                    node_execution_id=event.iteration_id,
                    node_id=event.iteration_node_id,
                    node_type=event.iteration_node_type,
                    node_data=event.iteration_node_data,
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    index=event.index,
                    node_run_index=workflow_entry.graph_engine.graph_runtime_state.node_run_steps,
                    output=event.pre_iteration_output,
                )
            )
        elif isinstance(event, (IterationRunSucceededEvent | IterationRunFailedEvent)):
            self._publish_event(
                QueueIterationCompletedEvent(
                    node_execution_id=event.iteration_id,
                    node_id=event.iteration_node_id,
                    node_type=event.iteration_node_type,
                    node_data=event.iteration_node_data,
                    parallel_id=event.parallel_id,
                    parallel_start_node_id=event.parallel_start_node_id,
                    parent_parallel_id=event.parent_parallel_id,
                    parent_parallel_start_node_id=event.parent_parallel_start_node_id,
                    start_at=event.start_at,
                    node_run_index=workflow_entry.graph_engine.graph_runtime_state.node_run_steps,
                    inputs=event.inputs,
                    outputs=event.outputs,
                    metadata=event.metadata,
                    steps=event.steps,
                    error=event.error if isinstance(event, IterationRunFailedEvent) else None,
                )
            )

    def get_workflow(self, app_model: App, workflow_id: str) -> Optional[Workflow]:
        """
        获取工作流。

        :param app_model: 应用模型对象。
        :param workflow_id: 工作流ID。
        :return: 工作流对象，如果未找到则返回None。
        """
        # 根据工作流ID查询工作流
        workflow = (
            db.session.query(Workflow)
            .filter(
                Workflow.tenant_id == app_model.tenant_id, Workflow.app_id == app_model.id, Workflow.id == workflow_id
            )
            .first()
        )

        # 返回工作流
        return workflow

    def _publish_event(self, event: AppQueueEvent) -> None:
        """
        发布事件。

        :param event: 事件对象。
        """
        self.queue_manager.publish(event, PublishFrom.APPLICATION_MANAGER)

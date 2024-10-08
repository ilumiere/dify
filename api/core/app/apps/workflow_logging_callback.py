from typing import Optional

from core.model_runtime.utils.encoders import jsonable_encoder
from core.workflow.callbacks.base_workflow_callback import WorkflowCallback
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
    NodeRunStartedEvent,
    NodeRunStreamChunkEvent,
    NodeRunSucceededEvent,
    ParallelBranchRunFailedEvent,
    ParallelBranchRunStartedEvent,
    ParallelBranchRunSucceededEvent,
)

_TEXT_COLOR_MAPPING = {
    "blue": "36;1",
    "yellow": "33;1",
    "pink": "38;5;200",
    "green": "32;1",
    "red": "31;1",
}


class WorkflowLoggingCallback(WorkflowCallback):
    """
    工作流日志回调类，用于处理和记录工作流事件。

    该类继承自 `WorkflowCallback`，并提供了多种方法来处理不同类型的工作流事件，并将这些事件记录到控制台。
    """

    def __init__(self) -> None:
        """
        初始化 `WorkflowLoggingCallback` 实例。

        属性:
        - `current_node_id`: 当前节点的ID，初始值为 `None`。
        """
        self.current_node_id = None

    def on_event(self, event: GraphEngineEvent) -> None:
        """
        处理工作流事件的方法。

        参数:
        - `event`: 工作流事件对象，类型为 `GraphEngineEvent`。

        该方法根据事件的类型调用相应的方法来处理事件，并将事件信息记录到控制台。
        """
        if isinstance(event, GraphRunStartedEvent):
            self.print_text("\n[GraphRunStartedEvent]", color="pink")
        elif isinstance(event, GraphRunSucceededEvent):
            self.print_text("\n[GraphRunSucceededEvent]", color="green")
        elif isinstance(event, GraphRunFailedEvent):
            self.print_text(f"\n[GraphRunFailedEvent] reason: {event.error}", color="red")
        elif isinstance(event, NodeRunStartedEvent):
            self.on_workflow_node_execute_started(event=event)
        elif isinstance(event, NodeRunSucceededEvent):
            self.on_workflow_node_execute_succeeded(event=event)
        elif isinstance(event, NodeRunFailedEvent):
            self.on_workflow_node_execute_failed(event=event)
        elif isinstance(event, NodeRunStreamChunkEvent):
            self.on_node_text_chunk(event=event)
        elif isinstance(event, ParallelBranchRunStartedEvent):
            self.on_workflow_parallel_started(event=event)
        elif isinstance(event, ParallelBranchRunSucceededEvent | ParallelBranchRunFailedEvent):
            self.on_workflow_parallel_completed(event=event)
        elif isinstance(event, IterationRunStartedEvent):
            self.on_workflow_iteration_started(event=event)
        elif isinstance(event, IterationRunNextEvent):
            self.on_workflow_iteration_next(event=event)
        elif isinstance(event, IterationRunSucceededEvent | IterationRunFailedEvent):
            self.on_workflow_iteration_completed(event=event)
        else:
            self.print_text(f"\n[{event.__class__.__name__}]", color="blue")

    def on_workflow_node_execute_started(self, event: NodeRunStartedEvent) -> None:
        """
        处理节点执行开始事件的方法。

        参数:
        - `event`: 节点执行开始事件对象，类型为 `NodeRunStartedEvent`。

        该方法将节点执行开始的信息记录到控制台。
        """
        self.print_text("\n[NodeRunStartedEvent]", color="yellow")
        self.print_text(f"Node ID: {event.node_id}", color="yellow")
        self.print_text(f"Node Title: {event.node_data.title}", color="yellow")
        self.print_text(f"Type: {event.node_type.value}", color="yellow")

    def on_workflow_node_execute_succeeded(self, event: NodeRunSucceededEvent) -> None:
        """
        处理节点执行成功事件的方法。

        参数:
        - `event`: 节点执行成功事件对象，类型为 `NodeRunSucceededEvent`。

        该方法将节点执行成功的信息记录到控制台，并输出节点的输入、处理数据、输出和元数据。
        """
        route_node_state = event.route_node_state

        self.print_text("\n[NodeRunSucceededEvent]", color="green")
        self.print_text(f"Node ID: {event.node_id}", color="green")
        self.print_text(f"Node Title: {event.node_data.title}", color="green")
        self.print_text(f"Type: {event.node_type.value}", color="green")

        if route_node_state.node_run_result:
            node_run_result = route_node_state.node_run_result
            self.print_text(
                f"Inputs: {jsonable_encoder(node_run_result.inputs) if node_run_result.inputs else ''}",
                color="green",
            )
            self.print_text(
                f"Process Data: "
                f"{jsonable_encoder(node_run_result.process_data) if node_run_result.process_data else ''}",
                color="green",
            )
            self.print_text(
                f"Outputs: {jsonable_encoder(node_run_result.outputs) if node_run_result.outputs else ''}",
                color="green",
            )
            self.print_text(
                f"Metadata: {jsonable_encoder(node_run_result.metadata) if node_run_result.metadata else ''}",
                color="green",
            )

    def on_workflow_node_execute_failed(self, event: NodeRunFailedEvent) -> None:
        """
        处理节点执行失败事件的方法。

        参数:
        - `event`: 节点执行失败事件对象，类型为 `NodeRunFailedEvent`。

        该方法将节点执行失败的信息记录到控制台，并输出节点的错误信息、输入、处理数据和输出。
        """
        route_node_state = event.route_node_state

        self.print_text("\n[NodeRunFailedEvent]", color="red")
        self.print_text(f"Node ID: {event.node_id}", color="red")
        self.print_text(f"Node Title: {event.node_data.title}", color="red")
        self.print_text(f"Type: {event.node_type.value}", color="red")

        if route_node_state.node_run_result:
            node_run_result = route_node_state.node_run_result
            self.print_text(f"Error: {node_run_result.error}", color="red")
            self.print_text(
                f"Inputs: {jsonable_encoder(node_run_result.inputs) if node_run_result.inputs else ''}",
                color="red",
            )
            self.print_text(
                f"Process Data: "
                f"{jsonable_encoder(node_run_result.process_data) if node_run_result.process_data else ''}",
                color="red",
            )
            self.print_text(
                f"Outputs: {jsonable_encoder(node_run_result.outputs) if node_run_result.outputs else ''}",
                color="red",
            )

    def on_node_text_chunk(self, event: NodeRunStreamChunkEvent) -> None:
        """
        处理节点文本块事件的方法。

        参数:
        - `event`: 节点文本块事件对象，类型为 `NodeRunStreamChunkEvent`。

        该方法将节点文本块的信息记录到控制台，并输出节点的元数据和文本块内容。
        """
        route_node_state = event.route_node_state
        if not self.current_node_id or self.current_node_id != route_node_state.node_id:
            self.current_node_id = route_node_state.node_id
            self.print_text("\n[NodeRunStreamChunkEvent]")
            self.print_text(f"Node ID: {route_node_state.node_id}")

            node_run_result = route_node_state.node_run_result
            if node_run_result:
                self.print_text(
                    f"Metadata: {jsonable_encoder(node_run_result.metadata) if node_run_result.metadata else ''}"
                )

        self.print_text(event.chunk_content, color="pink", end="")

    def on_workflow_parallel_started(self, event: ParallelBranchRunStartedEvent) -> None:
        """
        处理并行分支开始事件的方法。

        参数:
        - `event`: 并行分支开始事件对象，类型为 `ParallelBranchRunStartedEvent`。

        该方法将并行分支开始的信息记录到控制台，并输出并行ID、分支ID和迭代ID（如果有）。
        """
        self.print_text("\n[ParallelBranchRunStartedEvent]", color="blue")
        self.print_text(f"Parallel ID: {event.parallel_id}", color="blue")
        self.print_text(f"Branch ID: {event.parallel_start_node_id}", color="blue")
        if event.in_iteration_id:
            self.print_text(f"Iteration ID: {event.in_iteration_id}", color="blue")

    def on_workflow_parallel_completed(
        self, event: ParallelBranchRunSucceededEvent | ParallelBranchRunFailedEvent
    ) -> None:
        """
        处理并行分支完成事件的方法。

        参数:
        - `event`: 并行分支完成事件对象，类型为 `ParallelBranchRunSucceededEvent` 或 `ParallelBranchRunFailedEvent`。

        该方法将并行分支完成的信息记录到控制台，并输出并行ID、分支ID和迭代ID（如果有），以及错误信息（如果失败）。
        """
        if isinstance(event, ParallelBranchRunSucceededEvent):
            color = "blue"
        elif isinstance(event, ParallelBranchRunFailedEvent):
            color = "red"

        self.print_text(
            "\n[ParallelBranchRunSucceededEvent]"
            if isinstance(event, ParallelBranchRunSucceededEvent)
            else "\n[ParallelBranchRunFailedEvent]",
            color=color,
        )
        self.print_text(f"Parallel ID: {event.parallel_id}", color=color)
        self.print_text(f"Branch ID: {event.parallel_start_node_id}", color=color)
        if event.in_iteration_id:
            self.print_text(f"Iteration ID: {event.in_iteration_id}", color=color)

        if isinstance(event, ParallelBranchRunFailedEvent):
            self.print_text(f"Error: {event.error}", color=color)

    def on_workflow_iteration_started(self, event: IterationRunStartedEvent) -> None:
        """
        处理迭代开始事件的方法。

        参数:
        - `event`: 迭代开始事件对象，类型为 `IterationRunStartedEvent`。

        该方法将迭代开始的信息记录到控制台，并输出迭代节点ID。
        """
        self.print_text("\n[IterationRunStartedEvent]", color="blue")
        self.print_text(f"Iteration Node ID: {event.iteration_id}", color="blue")

    def on_workflow_iteration_next(self, event: IterationRunNextEvent) -> None:
        """
        处理迭代下一步事件的方法。

        参数:
        - `event`: 迭代下一步事件对象，类型为 `IterationRunNextEvent`。

        该方法将迭代下一步的信息记录到控制台，并输出迭代节点ID和迭代索引。
        """
        self.print_text("\n[IterationRunNextEvent]", color="blue")
        self.print_text(f"Iteration Node ID: {event.iteration_id}", color="blue")
        self.print_text(f"Iteration Index: {event.index}", color="blue")

    def on_workflow_iteration_completed(self, event: IterationRunSucceededEvent | IterationRunFailedEvent) -> None:
        """
        处理迭代完成事件的方法。

        参数:
        - `event`: 迭代完成事件对象，类型为 `IterationRunSucceededEvent` 或 `IterationRunFailedEvent`。

        该方法将迭代完成的信息记录到控制台，并输出节点ID。
        """
        self.print_text(
            "\n[IterationRunSucceededEvent]"
            if isinstance(event, IterationRunSucceededEvent)
            else "\n[IterationRunFailedEvent]",
            color="blue",
        )
        self.print_text(f"Node ID: {event.iteration_id}", color="blue")

    def print_text(self, text: str, color: Optional[str] = None, end: str = "\n") -> None:
        """
        打印带有高亮和无结束字符的文本。

        参数:
        - `text`: 要打印的文本，类型为 `str`。
        - `color`: 文本的颜色，类型为 `Optional[str]`，默认为 `None`。
        - `end`: 打印文本后的结束字符，类型为 `str`，默认为 `\n`。

        该方法根据颜色参数生成带有颜色的文本，并将其打印到控制台。
        """
        text_to_print = self._get_colored_text(text, color) if color else text
        print(f"{text_to_print}", end=end)

    def _get_colored_text(self, text: str, color: str) -> str:
        """
        获取带有颜色的文本。

        参数:
        - `text`: 要着色的文本，类型为 `str`。
        - `color`: 文本的颜色，类型为 `str`。

        返回值:
        - 带有颜色的文本，类型为 `str`。

        该方法根据颜色映射表生成带有颜色的文本。
        """
        color_str = _TEXT_COLOR_MAPPING[color]
        return f"\u001b[{color_str}m\033[1;3m{text}\u001b[0m"

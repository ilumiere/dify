import uuid
from collections.abc import Mapping
from typing import Any, Optional, cast

from pydantic import BaseModel, Field

from core.workflow.entities.node_entities import NodeType
from core.workflow.graph_engine.entities.run_condition import RunCondition
from core.workflow.nodes.answer.answer_stream_generate_router import AnswerStreamGeneratorRouter
from core.workflow.nodes.answer.entities import AnswerStreamGenerateRoute
from core.workflow.nodes.end.end_stream_generate_router import EndStreamGeneratorRouter
from core.workflow.nodes.end.entities import EndStreamParam


class GraphEdge(BaseModel):
    """
    GraphEdge 类表示图中的边，连接两个节点。它继承自 Pydantic 的 BaseModel，用于数据验证和序列化。

    主要用途和功能：
    - 描述图中两个节点之间的关系。
    - 存储边的源节点和目标节点的 ID。
    - 可选地存储运行条件，用于控制边的执行。
    """

    source_node_id: str = Field(..., description="源节点的唯一标识符。表示边的起始节点。")
    """
    源节点的唯一标识符。表示边的起始节点。
    """

    target_node_id: str = Field(..., description="目标节点的唯一标识符。表示边的结束节点。")
    """
    目标节点的唯一标识符。表示边的结束节点。
    """

    run_condition: Optional[RunCondition] = None
    """
    运行条件。可选字段，用于指定边的执行条件。如果为 None，表示没有特定的执行条件。
    """


class GraphParallel(BaseModel):
    """
    GraphParallel 类表示图中的并行结构，继承自 Pydantic 的 BaseModel，用于数据验证和序列化。

    主要用途和功能：
    - 描述图中的并行结构，通常用于表示多个节点之间的并行执行关系。
    - 存储并行结构的唯一标识符、起始节点、父并行结构等信息。
    - 可选地存储父并行结构的标识符和起始节点，以及并行结构的结束节点。
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="随机生成的 UUID 并行标识符。")
    """
    随机生成的 UUID 并行标识符。用于唯一标识该并行结构。
    """

    start_from_node_id: str = Field(..., description="并行结构的起始节点标识符。")
    """
    并行结构的起始节点标识符。表示并行结构从哪个节点开始执行。
    """

    parent_parallel_id: Optional[str] = None
    """
    父并行结构的标识符。可选字段，用于指定当前并行结构的父并行结构。
    """

    parent_parallel_start_node_id: Optional[str] = None
    """
    父并行结构的起始节点标识符。可选字段，用于指定父并行结构的起始节点。
    """

    end_to_node_id: Optional[str] = None
    """
    并行结构的结束节点标识符。可选字段，用于指定并行结构的结束节点。
    """


class Graph(BaseModel):
    """
    Graph 类表示图结构，继承自 Pydantic 的 BaseModel，用于数据验证和序列化。

    主要用途和功能：
    - 描述图的结构，包括节点、边、并行结构等信息。
    - 存储图的根节点、节点列表、节点配置映射、边映射、反向边映射、并行结构映射、节点与并行结构映射、答案流生成路由和结束流参数。
    - 提供初始化图对象的方法，解析图的配置信息并构建图的结构。
    """

    root_node_id: str = Field(..., description="图的根节点ID。表示图的起始节点。")
    """
    图的根节点ID。表示图的起始节点。
    """

    node_ids: list[str] = Field(default_factory=list, description="图的节点ID列表。")
    """
    图的节点ID列表。包含图中所有节点的唯一标识符。
    """

    node_id_config_mapping: dict[str, dict] = Field(
        default_factory=list, description="节点配置映射。键为节点ID，值为节点的配置信息。"
    )
    """
    节点配置映射。键为节点ID，值为节点的配置信息。用于存储每个节点的详细配置。
    """

    edge_mapping: dict[str, list[GraphEdge]] = Field(
        default_factory=dict, description="图的边映射。键为源节点ID，值为从该节点出发的边列表。"
    )
    """
    图的边映射。键为源节点ID，值为从该节点出发的边列表。用于存储图中所有边的信息。
    """

    reverse_edge_mapping: dict[str, list[GraphEdge]] = Field(
        default_factory=dict, description="图的反向边映射。键为目标节点ID，值为指向该节点的边列表。"
    )
    """
    图的反向边映射。键为目标节点ID，值为指向该节点的边列表。用于反向查找边的信息。
    """

    parallel_mapping: dict[str, GraphParallel] = Field(
        default_factory=dict, description="图的并行结构映射。键为并行结构ID，值为并行结构对象。"
    )
    """
    图的并行结构映射。键为并行结构ID，值为并行结构对象。用于存储图中所有并行结构的信息。
    """

    node_parallel_mapping: dict[str, str] = Field(
        default_factory=dict, description="图的节点与并行结构映射。键为节点ID，值为并行结构ID。"
    )
    """
    图的节点与并行结构映射。键为节点ID，值为并行结构ID。用于存储节点与并行结构之间的关系。
    """

    answer_stream_generate_routes: AnswerStreamGenerateRoute = Field(..., description="答案流生成路由。")
    """
    答案流生成路由。用于指定答案流的生成路径。
    """

    end_stream_param: EndStreamParam = Field(..., description="结束流参数。")
    """
    结束流参数。用于指定流的结束参数。
    """

    @classmethod
    def init(cls, graph_config: Mapping[str, Any], root_node_id: Optional[str] = None) -> "Graph":
        """
        初始化图对象。

        该函数的主要用途是根据传入的图配置信息初始化一个图对象。它会解析图的边和节点配置，构建边映射和节点映射，并检查图的连通性和并行层级限制。

        参数:
        - graph_config (Mapping[str, Any]): 图的配置信息，包含节点和边的配置。
        - root_node_id (Optional[str]): 根节点的ID。如果未提供，则自动选择一个START类型的节点作为根节点。

        返回值:
        - Graph: 初始化后的图对象。
        """
        # 获取边配置信息
        edge_configs = graph_config.get("edges")
        if edge_configs is None:
            edge_configs = []

        edge_configs = cast(list, edge_configs)

        # 重新组织边映射
        edge_mapping: dict[str, list[GraphEdge]] = {}
        reverse_edge_mapping: dict[str, list[GraphEdge]] = {}
        target_edge_ids = set()
        for edge_config in edge_configs:
            source_node_id = edge_config.get("source")
            if not source_node_id:
                continue

            if source_node_id not in edge_mapping:
                edge_mapping[source_node_id] = []

            target_node_id = edge_config.get("target")
            if not target_node_id:
                continue

            if target_node_id not in reverse_edge_mapping:
                reverse_edge_mapping[target_node_id] = []

            target_edge_ids.add(target_node_id)

            # 解析运行条件
            run_condition = None
            if edge_config.get("sourceHandle") and edge_config.get("sourceHandle") != "source":
                run_condition = RunCondition(type="branch_identify", branch_identify=edge_config.get("sourceHandle"))

            graph_edge = GraphEdge(
                source_node_id=source_node_id, target_node_id=target_node_id, run_condition=run_condition
            )

            edge_mapping[source_node_id].append(graph_edge)
            reverse_edge_mapping[target_node_id].append(graph_edge)

        # 获取节点配置信息
        node_configs = graph_config.get("nodes")
        if not node_configs:
            raise ValueError("Graph must have at least one node")

        node_configs = cast(list, node_configs)

        # 获取没有前驱节点的节点配置
        root_node_configs = []
        all_node_id_config_mapping: dict[str, dict] = {}
        for node_config in node_configs:
            node_id = node_config.get("id")
            if not node_id:
                continue

            if node_id not in target_edge_ids:
                root_node_configs.append(node_config)

            all_node_id_config_mapping[node_id] = node_config

        root_node_ids = [node_config.get("id") for node_config in root_node_configs]

        # 获取根节点
        if not root_node_id:
            # 如果没有根节点ID，使用START类型的节点作为根节点
            root_node_id = next(
                (
                    node_config.get("id")
                    for node_config in root_node_configs
                    if node_config.get("data", {}).get("type", "") == NodeType.START.value
                ),
                None,
            )

        if not root_node_id or root_node_id not in root_node_ids:
            raise ValueError(f"Root node id {root_node_id} not found in the graph")

        # 检查是否与前一个节点连接
        cls._check_connected_to_previous_node(route=[root_node_id], edge_mapping=edge_mapping)

        # 从根节点获取所有节点ID
        node_ids = [root_node_id]
        cls._recursively_add_node_ids(node_ids=node_ids, edge_mapping=edge_mapping, node_id=root_node_id)

        node_id_config_mapping = {node_id: all_node_id_config_mapping[node_id] for node_id in node_ids}

        # 初始化并行映射
        parallel_mapping: dict[str, GraphParallel] = {}
        node_parallel_mapping: dict[str, str] = {}
        cls._recursively_add_parallels(
            edge_mapping=edge_mapping,
            reverse_edge_mapping=reverse_edge_mapping,
            start_node_id=root_node_id,
            parallel_mapping=parallel_mapping,
            node_parallel_mapping=node_parallel_mapping,
        )

        # 检查是否超过N层并行
        for parallel in parallel_mapping.values():
            if parallel.parent_parallel_id:
                cls._check_exceed_parallel_limit(
                    parallel_mapping=parallel_mapping, level_limit=3, parent_parallel_id=parallel.parent_parallel_id
                )

        # 初始化答案流生成路由
        answer_stream_generate_routes = AnswerStreamGeneratorRouter.init(
            node_id_config_mapping=node_id_config_mapping, reverse_edge_mapping=reverse_edge_mapping
        )

        # 初始化结束流参数
        end_stream_param = EndStreamGeneratorRouter.init(
            node_id_config_mapping=node_id_config_mapping,
            reverse_edge_mapping=reverse_edge_mapping,
            node_parallel_mapping=node_parallel_mapping,
        )

        # 初始化图对象
        graph = cls(
            root_node_id=root_node_id,
            node_ids=node_ids,
            node_id_config_mapping=node_id_config_mapping,
            edge_mapping=edge_mapping,
            reverse_edge_mapping=reverse_edge_mapping,
            parallel_mapping=parallel_mapping,
            node_parallel_mapping=node_parallel_mapping,
            answer_stream_generate_routes=answer_stream_generate_routes,
            end_stream_param=end_stream_param,
        )

        return graph

    def add_extra_edge(
        self, source_node_id: str, target_node_id: str, run_condition: Optional[RunCondition] = None
    ) -> None:
        """
        向图中添加额外的边。

        该函数的主要用途是向图中添加一条从源节点到目标节点的新边。如果源节点或目标节点不存在于图中，或者目标节点已经与源节点相连，则不会添加新边。

        参数:
        - source_node_id (str): 源节点的ID，表示边的起始节点。
        - target_node_id (str): 目标节点的ID，表示边的结束节点。
        - run_condition (Optional[RunCondition]): 运行条件，表示在什么条件下该边会被激活。默认为None。

        返回值:
        - None: 该函数没有返回值，直接修改图的边映射。
        """
        # 检查源节点和目标节点是否存在于图中
        if source_node_id not in self.node_ids or target_node_id not in self.node_ids:
            # 如果源节点或目标节点不存在，直接返回，不进行任何操作
            return

        # 检查源节点是否已经有出边
        if source_node_id not in self.edge_mapping:
            # 如果源节点没有出边，初始化一个空列表
            self.edge_mapping[source_node_id] = []

        # 检查目标节点是否已经与源节点相连
        if target_node_id in [graph_edge.target_node_id for graph_edge in self.edge_mapping[source_node_id]]:
            # 如果目标节点已经与源节点相连，直接返回，不进行任何操作
            return

        # 创建一个新的图边对象
        graph_edge = GraphEdge(
            source_node_id=source_node_id, target_node_id=target_node_id, run_condition=run_condition
        )

        # 将新创建的图边对象添加到源节点的出边列表中
        self.edge_mapping[source_node_id].append(graph_edge)

    def get_leaf_node_ids(self) -> list[str]:
        """
        获取图中的叶子节点ID。

        该函数的主要用途是遍历图中的所有节点，找出那些没有出边或者只有一条出边且该出边指向根节点的节点，这些节点被称为叶子节点。

        返回值:
        - list[str]: 包含所有叶子节点ID的列表。
        """
        leaf_node_ids = []  # 初始化一个空列表，用于存储叶子节点的ID

        # 遍历图中的所有节点ID
        for node_id in self.node_ids:
            # 检查当前节点是否没有出边，或者只有一条出边且该出边指向根节点
            if node_id not in self.edge_mapping or (
                len(self.edge_mapping[node_id]) == 1
                and self.edge_mapping[node_id][0].target_node_id == self.root_node_id
            ):
                # 如果满足条件，将当前节点ID添加到叶子节点ID列表中
                leaf_node_ids.append(node_id)

        # 返回包含所有叶子节点ID的列表
        return leaf_node_ids

    @classmethod
    def _recursively_add_node_ids(
        cls, node_ids: list[str], edge_mapping: dict[str, list[GraphEdge]], node_id: str
    ) -> None:
        """
        递归地添加节点ID。

        该函数的主要用途是通过递归遍历图中的边，从起始节点开始，逐步添加所有可达节点的ID到node_ids列表中。

        参数:
        - node_ids (list[str]): 存储节点ID的列表。
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。
        - node_id (str): 当前处理的节点ID。

        返回值:
        - None: 该函数没有返回值，直接修改node_ids列表。
        """
        # 遍历当前节点ID对应的边
        for graph_edge in edge_mapping.get(node_id, []):
            # 如果目标节点ID已经在node_ids列表中，跳过
            if graph_edge.target_node_id in node_ids:
                continue

            # 将目标节点ID添加到node_ids列表中
            node_ids.append(graph_edge.target_node_id)
            # 递归调用自身，继续处理目标节点ID
            cls._recursively_add_node_ids(
                node_ids=node_ids, edge_mapping=edge_mapping, node_id=graph_edge.target_node_id
            )

    @classmethod
    def _check_connected_to_previous_node(cls, route: list[str], edge_mapping: dict[str, list[GraphEdge]]) -> None:
        """
        检查是否连接到前一个节点。

        该函数的主要用途是通过递归遍历图中的边，检查当前路径中的节点是否与前一个节点相连。如果发现循环连接，则抛出异常。

        参数:
        - route (list[str]): 当前路径，存储节点ID的列表。
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。

        返回值:
        - None: 该函数没有返回值，如果发现循环连接，则抛出异常。
        """
        # 获取路径中的最后一个节点ID
        last_node_id = route[-1]

        # 遍历最后一个节点ID对应的边
        for graph_edge in edge_mapping.get(last_node_id, []):
            # 如果目标节点ID为空，跳过
            if not graph_edge.target_node_id:
                continue

            # 如果目标节点ID已经在路径中，说明存在循环连接，抛出异常
            if graph_edge.target_node_id in route:
                raise ValueError(
                    f"Node {graph_edge.source_node_id} is connected to the previous node, please check the graph."
                )

            # 创建新的路径，包含当前目标节点ID
            new_route = route.copy()
            new_route.append(graph_edge.target_node_id)
            # 递归调用自身，继续检查新的路径
            cls._check_connected_to_previous_node(
                route=new_route,
                edge_mapping=edge_mapping,
            )

    @classmethod
    def _recursively_add_parallels(
        cls,
        edge_mapping: dict[str, list[GraphEdge]],
        reverse_edge_mapping: dict[str, list[GraphEdge]],
        start_node_id: str,
        parallel_mapping: dict[str, GraphParallel],
        node_parallel_mapping: dict[str, str],
        parent_parallel: Optional[GraphParallel] = None,
    ) -> None:
        """
        递归地添加并行结构。

        该函数的主要用途是通过递归遍历图中的边，从起始节点开始，逐步添加并行结构。它会根据边的运行条件和目标节点ID，构建并行结构并更新并行映射和节点并行映射。

        参数:
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。
        - reverse_edge_mapping (dict[str, list[GraphEdge]]): 图的反向边映射，键是节点ID，值是与该节点相连的边的列表。
        - start_node_id (str): 起始节点的ID，从该节点开始递归添加并行结构。
        - parallel_mapping (dict[str, GraphParallel]): 并行映射字典，键是并行ID，值是GraphParallel对象。
        - node_parallel_mapping (dict[str, str]): 节点并行映射字典，键是节点ID，值是并行ID。
        - parent_parallel (Optional[GraphParallel]): 可选的父并行对象，用于确定当前并行对象。

        返回值:
        - None: 该函数没有返回值，直接修改parallel_mapping和node_parallel_mapping。
        """
        target_node_edges = edge_mapping.get(start_node_id, [])
        parallel = None
        if len(target_node_edges) > 1:
            # 获取当前并行结构中的所有节点ID
            parallel_branch_node_ids = {}
            condition_edge_mappings = {}
            for graph_edge in target_node_edges:
                if graph_edge.run_condition is None:
                    if "default" not in parallel_branch_node_ids:
                        parallel_branch_node_ids["default"] = []

                    parallel_branch_node_ids["default"].append(graph_edge.target_node_id)
                else:
                    condition_hash = graph_edge.run_condition.hash
                    if condition_hash not in condition_edge_mappings:
                        condition_edge_mappings[condition_hash] = []

                    condition_edge_mappings[condition_hash].append(graph_edge)

            for condition_hash, graph_edges in condition_edge_mappings.items():
                if len(graph_edges) > 1:
                    if condition_hash not in parallel_branch_node_ids:
                        parallel_branch_node_ids[condition_hash] = []

                    for graph_edge in graph_edges:
                        parallel_branch_node_ids[condition_hash].append(graph_edge.target_node_id)

            condition_parallels = {}
            for condition_hash, condition_parallel_branch_node_ids in parallel_branch_node_ids.items():
                # 检查节点并行映射中的目标节点ID
                parallel = None
                if condition_parallel_branch_node_ids:
                    parent_parallel_id = parent_parallel.id if parent_parallel else None

                    parallel = GraphParallel(
                        start_from_node_id=start_node_id,
                        parent_parallel_id=parent_parallel.id if parent_parallel else None,
                        parent_parallel_start_node_id=parent_parallel.start_from_node_id if parent_parallel else None,
                    )
                    parallel_mapping[parallel.id] = parallel
                    condition_parallels[condition_hash] = parallel

                    in_branch_node_ids = cls._fetch_all_node_ids_in_parallels(
                        edge_mapping=edge_mapping,
                        reverse_edge_mapping=reverse_edge_mapping,
                        parallel_branch_node_ids=condition_parallel_branch_node_ids,
                    )

                    # 收集所有分支节点ID
                    parallel_node_ids = []
                    for _, node_ids in in_branch_node_ids.items():
                        for node_id in node_ids:
                            in_parent_parallel = True
                            if parent_parallel_id:
                                in_parent_parallel = False
                                for parallel_node_id, parallel_id in node_parallel_mapping.items():
                                    if parallel_id == parent_parallel_id and parallel_node_id == node_id:
                                        in_parent_parallel = True
                                        break

                            if in_parent_parallel:
                                parallel_node_ids.append(node_id)
                                node_parallel_mapping[node_id] = parallel.id

                    outside_parallel_target_node_ids = set()
                    for node_id in parallel_node_ids:
                        if node_id == parallel.start_from_node_id:
                            continue

                        node_edges = edge_mapping.get(node_id)
                        if not node_edges:
                            continue

                        if len(node_edges) > 1:
                            continue

                        target_node_id = node_edges[0].target_node_id
                        if target_node_id in parallel_node_ids:
                            continue

                        if parent_parallel_id:
                            parent_parallel = parallel_mapping.get(parent_parallel_id)
                            if not parent_parallel:
                                continue

                        if (
                            (
                                node_parallel_mapping.get(target_node_id)
                                and node_parallel_mapping.get(target_node_id) == parent_parallel_id
                            )
                            or (
                                parent_parallel
                                and parent_parallel.end_to_node_id
                                and target_node_id == parent_parallel.end_to_node_id
                            )
                            or (not node_parallel_mapping.get(target_node_id) and not parent_parallel)
                        ):
                            outside_parallel_target_node_ids.add(target_node_id)

                    if len(outside_parallel_target_node_ids) == 1:
                        if (
                            parent_parallel
                            and parent_parallel.end_to_node_id
                            and parallel.end_to_node_id == parent_parallel.end_to_node_id
                        ):
                            parallel.end_to_node_id = None
                        else:
                            parallel.end_to_node_id = outside_parallel_target_node_ids.pop()

            if condition_edge_mappings:
                for condition_hash, graph_edges in condition_edge_mappings.items():
                    for graph_edge in graph_edges:
                        current_parallel: GraphParallel | None = cls._get_current_parallel(
                            parallel_mapping=parallel_mapping,
                            graph_edge=graph_edge,
                            parallel=condition_parallels.get(condition_hash),
                            parent_parallel=parent_parallel,
                        )

                        cls._recursively_add_parallels(
                            edge_mapping=edge_mapping,
                            reverse_edge_mapping=reverse_edge_mapping,
                            start_node_id=graph_edge.target_node_id,
                            parallel_mapping=parallel_mapping,
                            node_parallel_mapping=node_parallel_mapping,
                            parent_parallel=current_parallel,
                        )
            else:
                for graph_edge in target_node_edges:
                    current_parallel = cls._get_current_parallel(
                        parallel_mapping=parallel_mapping,
                        graph_edge=graph_edge,
                        parallel=parallel,
                        parent_parallel=parent_parallel,
                    )

                    cls._recursively_add_parallels(
                        edge_mapping=edge_mapping,
                        reverse_edge_mapping=reverse_edge_mapping,
                        start_node_id=graph_edge.target_node_id,
                        parallel_mapping=parallel_mapping,
                        node_parallel_mapping=node_parallel_mapping,
                        parent_parallel=current_parallel,
                    )
        else:
            for graph_edge in target_node_edges:
                current_parallel = cls._get_current_parallel(
                    parallel_mapping=parallel_mapping,
                    graph_edge=graph_edge,
                    parallel=parallel,
                    parent_parallel=parent_parallel,
                )

                cls._recursively_add_parallels(
                    edge_mapping=edge_mapping,
                    reverse_edge_mapping=reverse_edge_mapping,
                    start_node_id=graph_edge.target_node_id,
                    parallel_mapping=parallel_mapping,
                    node_parallel_mapping=node_parallel_mapping,
                    parent_parallel=current_parallel,
                )

    @classmethod
    def _get_current_parallel(
        cls,
        parallel_mapping: dict[str, GraphParallel],
        graph_edge: GraphEdge,
        parallel: Optional[GraphParallel] = None,
        parent_parallel: Optional[GraphParallel] = None,
    ) -> Optional[GraphParallel]:
        """
        获取当前并行对象。

        该函数的主要用途是根据给定的参数确定当前的并行对象。它会优先使用传入的 `parallel` 参数，
        如果没有提供 `parallel`，则会根据 `parent_parallel` 和 `graph_edge` 来确定当前的并行对象。

        参数:
        - parallel_mapping (dict[str, GraphParallel]): 并行映射字典，键是并行ID，值是GraphParallel对象。
        - graph_edge (GraphEdge): 当前的图边对象，包含目标节点的信息。
        - parallel (Optional[GraphParallel]): 可选的并行对象，如果提供则直接使用。
        - parent_parallel (Optional[GraphParallel]): 可选的父并行对象，用于确定当前并行对象。

        返回值:
        - Optional[GraphParallel]: 返回当前的并行对象，如果没有找到则返回 None。
        """
        current_parallel = None  # 初始化当前并行对象为 None

        if parallel:
            # 如果提供了 `parallel` 参数，直接使用该并行对象
            current_parallel = parallel
        elif parent_parallel:
            # 如果没有提供 `parallel` 参数，但提供了 `parent_parallel` 参数
            if not parent_parallel.end_to_node_id or (
                parent_parallel.end_to_node_id and graph_edge.target_node_id != parent_parallel.end_to_node_id
            ):
                # 如果父并行对象没有结束节点ID，或者目标节点ID与父并行对象的结束节点ID不同，则使用父并行对象
                current_parallel = parent_parallel
            else:
                # 否则，尝试获取父并行对象的父并行对象
                parent_parallel_parent_parallel_id = parent_parallel.parent_parallel_id
                if parent_parallel_parent_parallel_id:
                    parent_parallel_parent_parallel = parallel_mapping.get(parent_parallel_parent_parallel_id)
                    if parent_parallel_parent_parallel and (
                        not parent_parallel_parent_parallel.end_to_node_id
                        or (
                            parent_parallel_parent_parallel.end_to_node_id
                            and graph_edge.target_node_id != parent_parallel_parent_parallel.end_to_node_id
                        )
                    ):
                        # 如果父并行对象的父并行对象存在且满足条件，则使用该父并行对象的父并行对象
                        current_parallel = parent_parallel_parent_parallel

        return current_parallel  # 返回当前的并行对象

    @classmethod
    def _check_exceed_parallel_limit(
        cls,
        parallel_mapping: dict[str, GraphParallel],
        level_limit: int,
        parent_parallel_id: str,
        current_level: int = 1,
    ) -> None:
        """
        检查并行层级是否超过限制。

        该函数的主要用途是递归地检查并行结构的层级是否超过指定的限制。如果超过限制，则抛出异常。

        参数:
        - parallel_mapping (dict[str, GraphParallel]): 并行映射字典，键是并行ID，值是GraphParallel对象。
        - level_limit (int): 并行层级的限制，超过该层级将抛出异常。
        - parent_parallel_id (str): 当前父并行的ID，用于递归检查。
        - current_level (int): 当前层级，默认为1。

        返回值:
        - None: 该函数没有返回值，如果超过层级限制，则抛出异常。
        """
        # 获取当前父并行对象
        parent_parallel = parallel_mapping.get(parent_parallel_id)
        if not parent_parallel:
            # 如果父并行对象不存在，直接返回
            return

        # 当前层级加1
        current_level += 1
        if current_level > level_limit:
            # 如果当前层级超过限制，抛出异常
            raise ValueError(f"Exceeds {level_limit} layers of parallel")

        if parent_parallel.parent_parallel_id:
            # 如果父并行有父并行ID，递归调用自身继续检查
            cls._check_exceed_parallel_limit(
                parallel_mapping=parallel_mapping,
                level_limit=level_limit,
                parent_parallel_id=parent_parallel.parent_parallel_id,
                current_level=current_level,
            )

    @classmethod
    def _recursively_add_parallel_node_ids(
        cls,
        branch_node_ids: list[str],
        edge_mapping: dict[str, list[GraphEdge]],
        merge_node_id: str,
        start_node_id: str,
    ) -> None:
        """
        递归地添加并行节点ID。

        该函数的主要用途是遍历图中的边映射，递归地添加所有与起始节点相关的节点ID到分支节点ID列表中，直到遇到合并节点。

        参数:
        - branch_node_ids (list[str]): 分支节点ID的列表，用于存储递归过程中找到的节点ID。
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。
        - merge_node_id (str): 合并节点的ID，用于判断递归的终止条件。
        - start_node_id (str): 起始节点的ID，用于开始递归遍历。

        返回值:
        - None: 该函数没有返回值，直接修改传入的branch_node_ids列表。
        """
        # 遍历与起始节点相连的所有边
        for graph_edge in edge_mapping.get(start_node_id, []):
            # 如果边的目标节点不是合并节点且不在分支节点ID列表中，则添加该节点ID
            if graph_edge.target_node_id != merge_node_id and graph_edge.target_node_id not in branch_node_ids:
                branch_node_ids.append(graph_edge.target_node_id)
                # 递归调用自身，继续添加与目标节点相连的节点ID
                cls._recursively_add_parallel_node_ids(
                    branch_node_ids=branch_node_ids,
                    edge_mapping=edge_mapping,
                    merge_node_id=merge_node_id,
                    start_node_id=graph_edge.target_node_id,
                )

    @classmethod
    def _fetch_all_node_ids_in_parallels(
        cls,
        edge_mapping: dict[str, list[GraphEdge]],
        reverse_edge_mapping: dict[str, list[GraphEdge]],
        parallel_branch_node_ids: list[str],
    ) -> dict[str, list[str]]:
        """
        获取并行分支中的所有节点ID。

        该函数的主要用途是遍历并行分支中的节点，递归地获取每个分支中的所有节点ID，并返回一个字典，其中键是分支节点ID，值是该分支中的所有节点ID列表。

        参数:
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。
        - reverse_edge_mapping (dict[str, list[GraphEdge]]): 图的反向边映射，键是节点ID，值是与该节点相连的边的列表。
        - parallel_branch_node_ids (list[str]): 并行分支节点ID的列表。

        返回值:
        - dict[str, list[str]]: 一个字典，键是分支节点ID，值是该分支中的所有节点ID列表。
        """
        routes_node_ids: dict[str, list[str]] = {}
        for parallel_branch_node_id in parallel_branch_node_ids:
            routes_node_ids[parallel_branch_node_id] = [parallel_branch_node_id]

            # 递归获取路径中的节点ID
            cls._recursively_fetch_routes(
                edge_mapping=edge_mapping,
                start_node_id=parallel_branch_node_id,
                routes_node_ids=routes_node_ids[parallel_branch_node_id],
            )

        # 从路径节点ID中获取叶子节点ID
        leaf_node_ids: dict[str, list[str]] = {}
        merge_branch_node_ids: dict[str, list[str]] = {}
        for branch_node_id, node_ids in routes_node_ids.items():
            for node_id in node_ids:
                if node_id not in edge_mapping or len(edge_mapping[node_id]) == 0:
                    if branch_node_id not in leaf_node_ids:
                        leaf_node_ids[branch_node_id] = []

                    leaf_node_ids[branch_node_id].append(node_id)

                for branch_node_id2, inner_route2 in routes_node_ids.items():
                    if (
                        branch_node_id != branch_node_id2
                        and node_id in inner_route2
                        and len(reverse_edge_mapping.get(node_id, [])) > 1
                        and cls._is_node_in_routes(
                            reverse_edge_mapping=reverse_edge_mapping,
                            start_node_id=node_id,
                            routes_node_ids=routes_node_ids,
                        )
                    ):
                        if node_id not in merge_branch_node_ids:
                            merge_branch_node_ids[node_id] = []

                        if branch_node_id2 not in merge_branch_node_ids[node_id]:
                            merge_branch_node_ids[node_id].append(branch_node_id2)

        # 按分支节点ID长度降序排序merge_branch_node_ids
        merge_branch_node_ids = dict(sorted(merge_branch_node_ids.items(), key=lambda x: len(x[1]), reverse=True))

        duplicate_end_node_ids = {}
        for node_id, branch_node_ids in merge_branch_node_ids.items():
            for node_id2, branch_node_ids2 in merge_branch_node_ids.items():
                if node_id != node_id2 and set(branch_node_ids) == set(branch_node_ids2):
                    if (node_id, node_id2) not in duplicate_end_node_ids and (
                        node_id2,
                        node_id,
                    ) not in duplicate_end_node_ids:
                        duplicate_end_node_ids[(node_id, node_id2)] = branch_node_ids

        for (node_id, node_id2), branch_node_ids in duplicate_end_node_ids.items():
            # 检查哪个节点在后
            if cls._is_node2_after_node1(node1_id=node_id, node2_id=node_id2, edge_mapping=edge_mapping):
                if node_id in merge_branch_node_ids:
                    del merge_branch_node_ids[node_id2]
            elif cls._is_node2_after_node1(node1_id=node_id2, node2_id=node_id, edge_mapping=edge_mapping):
                if node_id2 in merge_branch_node_ids:
                    del merge_branch_node_ids[node_id]

        branches_merge_node_ids: dict[str, str] = {}
        for node_id, branch_node_ids in merge_branch_node_ids.items():
            if len(branch_node_ids) <= 1:
                continue

            for branch_node_id in branch_node_ids:
                if branch_node_id in branches_merge_node_ids:
                    continue

                branches_merge_node_ids[branch_node_id] = node_id

        in_branch_node_ids: dict[str, list[str]] = {}
        for branch_node_id, node_ids in routes_node_ids.items():
            in_branch_node_ids[branch_node_id] = []
            if branch_node_id not in branches_merge_node_ids:
                # 当前分支中的所有节点ID都在此线程中
                in_branch_node_ids[branch_node_id].append(branch_node_id)
                in_branch_node_ids[branch_node_id].extend(node_ids)
            else:
                merge_node_id = branches_merge_node_ids[branch_node_id]
                if merge_node_id != branch_node_id:
                    in_branch_node_ids[branch_node_id].append(branch_node_id)

                # 从branch_node_id和merge_node_id获取所有节点ID
                cls._recursively_add_parallel_node_ids(
                    branch_node_ids=in_branch_node_ids[branch_node_id],
                    edge_mapping=edge_mapping,
                    merge_node_id=merge_node_id,
                    start_node_id=branch_node_id,
                )

        return in_branch_node_ids

    @classmethod
    def _recursively_fetch_routes(
        cls, edge_mapping: dict[str, list[GraphEdge]], start_node_id: str, routes_node_ids: list[str]
    ) -> None:
        """
        递归地获取路径

        该函数通过递归遍历图中的边，从起始节点开始，逐步获取所有可达节点的ID，并将这些节点ID存储在routes_node_ids列表中。

        参数:
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。
        - start_node_id (str): 起始节点的ID，从该节点开始递归获取路径。
        - routes_node_ids (list[str]): 存储路径中所有节点ID的列表。

        返回值:
        - None: 该函数没有返回值，直接修改routes_node_ids列表。
        """
        # 如果起始节点不在边映射中，说明该节点没有后继节点，直接返回
        if start_node_id not in edge_mapping:
            return

        # 遍历与起始节点相连的所有边
        for graph_edge in edge_mapping[start_node_id]:
            # 查找下一个节点的ID
            if graph_edge.target_node_id not in routes_node_ids:
                # 如果下一个节点的ID不在routes_node_ids列表中，将其添加到列表中
                routes_node_ids.append(graph_edge.target_node_id)

                # 递归调用该函数，继续从下一个节点开始获取路径
                cls._recursively_fetch_routes(
                    edge_mapping=edge_mapping, start_node_id=graph_edge.target_node_id, routes_node_ids=routes_node_ids
                )

    @classmethod
    def _is_node_in_routes(
        cls, reverse_edge_mapping: dict[str, list[GraphEdge]], start_node_id: str, routes_node_ids: dict[str, list[str]]
    ) -> bool:
        """
        递归检查节点是否在路径中。

        该函数通过递归遍历图中的反向边映射，检查给定的起始节点是否存在于指定的路径中。

        参数:
        - reverse_edge_mapping (dict[str, list[GraphEdge]]): 图的反向边映射，键是节点ID，值是与该节点相连的边的列表。
        - start_node_id (str): 起始节点的ID，从该节点开始递归检查。
        - routes_node_ids (dict[str, list[str]]): 存储路径中所有节点ID的字典，键是分支节点ID，值是该分支节点下的所有节点ID列表。

        返回值:
        - bool: 如果起始节点存在于指定的路径中，返回True；否则返回False。
        """
        # 如果起始节点不在反向边映射中，说明该节点没有前驱节点，直接返回False
        if start_node_id not in reverse_edge_mapping:
            return False

        # 初始化一个集合，用于存储所有路径中的节点ID
        all_routes_node_ids = set()
        # 初始化一个字典，用于存储并行结构的起始节点ID及其对应的分支节点ID列表
        parallel_start_node_ids: dict[str, list[str]] = {}

        # 遍历routes_node_ids字典中的每个分支节点ID及其对应的节点ID列表
        for branch_node_id, node_ids in routes_node_ids.items():
            # 将当前分支节点下的所有节点ID添加到all_routes_node_ids集合中
            all_routes_node_ids.update(node_ids)

            # 如果当前分支节点在反向边映射中
            if branch_node_id in reverse_edge_mapping:
                # 遍历与当前分支节点相连的所有反向边
                for graph_edge in reverse_edge_mapping[branch_node_id]:
                    # 如果当前反向边的源节点ID不在parallel_start_node_ids字典中，初始化一个空列表
                    if graph_edge.source_node_id not in parallel_start_node_ids:
                        parallel_start_node_ids[graph_edge.source_node_id] = []

                    # 将当前分支节点ID添加到parallel_start_node_ids字典中对应的源节点ID列表中
                    parallel_start_node_ids[graph_edge.source_node_id].append(branch_node_id)

        # 遍历parallel_start_node_ids字典中的每个源节点ID及其对应的分支节点ID列表
        for _, branch_node_ids in parallel_start_node_ids.items():
            # 如果当前分支节点ID列表与routes_node_ids字典的键集合相等，说明起始节点存在于指定的路径中，返回True
            if set(branch_node_ids) == set(routes_node_ids.keys()):
                return True

        # 如果遍历完所有分支节点ID列表都没有找到匹配的路径，返回False
        return False

    @classmethod
    def _is_node2_after_node1(cls, node1_id: str, node2_id: str, edge_mapping: dict[str, list[GraphEdge]]) -> bool:
        """
        检查节点2是否在节点1之后。

        该函数通过递归遍历图中的边，判断节点2是否是节点1的后继节点。

        参数:
        - node1_id (str): 第一个节点的ID。
        - node2_id (str): 第二个节点的ID。
        - edge_mapping (dict[str, list[GraphEdge]]): 图的边映射，键是节点ID，值是与该节点相连的边的列表。

        返回值:
        - bool: 如果节点2是节点1的后继节点，返回True；否则返回False。
        """
        # 如果节点1不在边映射中，说明节点1没有后继节点，直接返回False
        if node1_id not in edge_mapping:
            return False

        # 遍历与节点1相连的所有边
        for graph_edge in edge_mapping[node1_id]:
            # 如果当前边的目标节点是节点2，说明节点2是节点1的后继节点，返回True
            if graph_edge.target_node_id == node2_id:
                return True

            # 递归检查当前边的目标节点是否是节点2的前驱节点
            if cls._is_node2_after_node1(
                node1_id=graph_edge.target_node_id, node2_id=node2_id, edge_mapping=edge_mapping
            ):
                return True

        # 如果遍历完所有边都没有找到节点2，返回False
        return False

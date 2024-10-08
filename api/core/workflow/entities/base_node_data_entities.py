from abc import ABC
from typing import Optional

from pydantic import BaseModel


# 继承自 ABC (Abstract Base Class)的类是一个抽象基类，不能被实例化，只能被继承
# 抽象基类可以定义抽象方法，这些方法必须在子类中实现。
# 通过这种方式，可以确保子类实现了某些必要的方法，从而保证代码的一致性和可维护性

# BaseNodeData 类是一个抽象基类，继承自 ABC 和 BaseModel。它用于定义工作流中节点的基本数据结构。
# 该类包含两个属性：
# - title: 节点的标题，类型为字符串。
# - desc: 节点的描述，类型为可选字符串（默认为 None）。
class BaseNodeData(ABC, BaseModel):

    title: str  # 节点的标题
    desc: Optional[str] = None  # 节点的描述，可选

# BaseIterationNodeData 类继承自 BaseNodeData，用于定义迭代节点的数据结构。
# 该类新增一个属性：
# - start_node_id: 迭代开始节点的 ID，类型为可选字符串（默认为 None）。
class BaseIterationNodeData(BaseNodeData):
    start_node_id: Optional[str] = None  # 迭代开始节点的 ID，可选

# BaseIterationState 类用于定义迭代状态的数据结构。
# 该类包含四个属性：
# - iteration_node_id: 当前迭代节点的 ID，类型为字符串。
# - index: 当前迭代的索引，类型为整数。
# - inputs: 当前迭代的输入数据，类型为字典。
# - metadata: 当前迭代的元数据，类型为 MetaData 类的实例。
class BaseIterationState(BaseModel):
    iteration_node_id: str  # 当前迭代节点的 ID
    index: int  # 当前迭代的索引
    inputs: dict  # 当前迭代的输入数据

    # MetaData 类是一个嵌套类，用于定义迭代状态的元数据。
    # 该类目前没有定义任何属性或方法。
    class MetaData(BaseModel):
        pass

    metadata: MetaData  # 当前迭代的元数据

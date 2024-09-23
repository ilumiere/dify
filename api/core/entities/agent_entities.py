from enum import Enum


class PlanningStrategy(Enum):
    """
    该枚举类定义了不同的规划策略类型。每个策略类型对应一个字符串值，用于标识特定的规划方法。

    属性:
    - ROUTER: 表示使用路由器进行规划的策略。
    - REACT_ROUTER: 表示使用React路由器进行规划的策略。
    - REACT: 表示使用React进行规划的策略。
    - FUNCTION_CALL: 表示使用函数调用进行规划的策略。
    """

    ROUTER = "router"  # 路由器规划策略
    REACT_ROUTER = "react_router"  # React路由器规划策略
    REACT = "react"  # React规划策略
    FUNCTION_CALL = "function_call"  # 函数调用规划策略


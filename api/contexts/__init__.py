from contextvars import ContextVar

from core.workflow.entities.variable_pool import VariablePool

# 这段代码定义了两个上下文变量，用于在多租户环境中管理租户ID和流程变量池。
# 上下文变量（ContextVar）是一种线程安全的变量，可以在不同的上下文中保持状态。

# tenant_id: 这是一个上下文变量，用于存储当前租户的ID。
# 类型为 ContextVar[str]，表示该变量可以存储字符串类型的租户ID。
# 初始值为 "tenant_id"，表示该变量的默认名称。
tenant_id: ContextVar[str] = ContextVar("tenant_id")

# workflow_variable_pool: 这是一个上下文变量，用于存储当前流程的变量池。
# 类型为 ContextVar[VariablePool]，表示该变量可以存储 VariablePool 类型的对象。
# VariablePool 是一个用于管理流程变量的类，通常包含多个变量及其值。
# 初始值为 "workflow_variable_pool"，表示该变量的默认名称。
workflow_variable_pool: ContextVar[VariablePool] = ContextVar("workflow_variable_pool")

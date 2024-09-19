from core.extension.extensible import ExtensionModule, ModuleExtension
from core.external_data_tool.base import ExternalDataTool
from core.moderation.base import Moderation


class Extension:
    """
    该类用于管理和初始化不同模块的扩展。它维护一个字典，用于存储每个模块的扩展实例。
    """

    __module_extensions: dict[str, dict[str, ModuleExtension]] = {}
    """
    私有属性，用于存储每个模块的扩展实例。键是模块的名称，值是一个字典，其中键是扩展的名称，值是扩展实例。
    """

    module_classes = {ExtensionModule.MODERATION: Moderation, ExtensionModule.EXTERNAL_DATA_TOOL: ExternalDataTool}
    """
    静态属性，定义了模块与其对应的类。键是模块的枚举值，值是模块对应的类。
    """

    def init(self):
        """
        初始化所有模块的扩展。遍历 `module_classes` 字典，调用每个模块类的 `scan_extensions` 方法，并将结果存储在 `__module_extensions` 中。
        """
        for module, module_class in self.module_classes.items():
            self.__module_extensions[module.value] = module_class.scan_extensions()

    def module_extensions(self, module: str) -> list[ModuleExtension]:
        """
        获取指定模块的所有扩展实例。

        :param module: 模块的名称，字符串类型。
        :return: 返回一个包含该模块所有扩展实例的列表。
        :raises ValueError: 如果指定的模块不存在，则抛出 ValueError 异常。
        """
        module_extensions = self.__module_extensions.get(module)

        if not module_extensions:
            raise ValueError(f"Extension Module {module} not found")

        return list(module_extensions.values())

    def module_extension(self, module: ExtensionModule, extension_name: str) -> ModuleExtension:
        """
        获取指定模块的特定扩展实例。

        :param module: 模块的枚举值，ExtensionModule 类型。
        :param extension_name: 扩展的名称，字符串类型。
        :return: 返回指定模块的特定扩展实例。
        :raises ValueError: 如果指定的模块或扩展不存在，则抛出 ValueError 异常。
        """
        module_extensions = self.__module_extensions.get(module.value)

        if not module_extensions:
            raise ValueError(f"Extension Module {module} not found")

        module_extension = module_extensions.get(extension_name)

        if not module_extension:
            raise ValueError(f"Extension {extension_name} not found")

        return module_extension

    def extension_class(self, module: ExtensionModule, extension_name: str) -> type:
        """
        获取指定模块的特定扩展的类。

        :param module: 模块的枚举值，ExtensionModule 类型。
        :param extension_name: 扩展的名称，字符串类型。
        :return: 返回指定模块的特定扩展的类。
        :raises ValueError: 如果指定的模块或扩展不存在，则抛出 ValueError 异常。
        """
        module_extension = self.module_extension(module, extension_name)
        return module_extension.extension_class

    def validate_form_schema(self, module: ExtensionModule, extension_name: str, config: dict) -> None:
        """
        验证指定模块的特定扩展的表单模式。

        :param module: 模块的枚举值，ExtensionModule 类型。
        :param extension_name: 扩展的名称，字符串类型。
        :param config: 配置字典，包含需要验证的表单数据。
        :return: 返回 None。
        :raises ValueError: 如果指定的模块或扩展不存在，则抛出 ValueError 异常。
        """
        module_extension = self.module_extension(module, extension_name)
        form_schema = module_extension.form_schema

        # TODO validate form_schema

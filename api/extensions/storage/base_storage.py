"""Abstract interface for file storage implementations."""

from abc import ABC, abstractmethod
from collections.abc import Generator

from flask import Flask


class BaseStorage(ABC):
    """
    文件存储的抽象接口类。

    该类定义了一个抽象接口，用于实现文件存储的各种操作。所有具体的存储实现类都必须继承该类并实现其抽象方法。
    该类的主要用途是提供一个统一的接口，使得不同的存储实现（如本地文件系统、云存储等）可以以一致的方式进行操作。

    属性:
    - app: Flask 应用实例，用于与 Flask 框架集成。
    """

    app = None  # Flask 应用实例，用于与 Flask 框架集成。

    def __init__(self, app: Flask):
        """
        初始化 BaseStorage 类。

        参数:
        - app (Flask): Flask 应用实例，用于与 Flask 框架集成。

        该方法将传入的 Flask 应用实例赋值给类的 app 属性。
        """
        self.app = app

    @abstractmethod
    def save(self, filename, data):
        """
        抽象方法，用于将数据保存到指定文件。

        参数:
        - filename (str): 要保存的文件名。
        - data (bytes): 要保存的数据。

        该方法需要在具体的存储实现类中实现，用于将数据保存到指定的文件中。
        如果未实现该方法，调用时将抛出 NotImplementedError 异常。
        """
        raise NotImplementedError

    @abstractmethod
    def load_once(self, filename: str) -> bytes:
        """
        抽象方法，用于一次性加载指定文件的内容。

        参数:
        - filename (str): 要加载的文件名。

        返回值:
        - bytes: 文件内容的字节数据。

        该方法需要在具体的存储实现类中实现，用于一次性加载指定文件的内容。
        如果未实现该方法，调用时将抛出 NotImplementedError 异常。
        """
        raise NotImplementedError

    @abstractmethod
    def load_stream(self, filename: str) -> Generator:
        """
        抽象方法，用于以流的方式加载指定文件的内容。

        参数:
        - filename (str): 要加载的文件名。

        返回值:
        - Generator: 生成器，用于逐块读取文件内容。

        该方法需要在具体的存储实现类中实现，用于以流的方式加载指定文件的内容。
        如果未实现该方法，调用时将抛出 NotImplementedError 异常。
        """
        raise NotImplementedError

    @abstractmethod
    def download(self, filename, target_filepath):
        """
        抽象方法，用于将指定文件下载到本地文件系统。

        参数:
        - filename (str): 要下载的文件名。
        - target_filepath (str): 下载文件的目标路径。

        该方法需要在具体的存储实现类中实现，用于将指定文件下载到本地文件系统。
        如果未实现该方法，调用时将抛出 NotImplementedError 异常。
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, filename):
        """
        抽象方法，用于检查指定文件是否存在。

        参数:
        - filename (str): 要检查的文件名。

        返回值:
        - bool: 如果文件存在返回 True，否则返回 False。

        该方法需要在具体的存储实现类中实现，用于检查指定文件是否存在。
        如果未实现该方法，调用时将抛出 NotImplementedError 异常。
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, filename):
        """
        抽象方法，用于删除指定文件。

        参数:
        - filename (str): 要删除的文件名。

        该方法需要在具体的存储实现类中实现，用于删除指定文件。
        如果未实现该方法，调用时将抛出 NotImplementedError 异常。
        """
        raise NotImplementedError

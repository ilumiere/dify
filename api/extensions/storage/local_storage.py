import os
import shutil
from collections.abc import Generator
from pathlib import Path

from flask import Flask

from extensions.storage.base_storage import BaseStorage


class LocalStorage(BaseStorage):
    """
    本地存储的实现类。

    该类继承自 BaseStorage，主要用于在本地文件系统中进行文件的存储、读取、下载、检查存在性和删除操作。
    每个方法都提供了详细的注释，解释其功能和实现逻辑。
    """

    def __init__(self, app: Flask):
        """
        初始化 LocalStorage 实例。

        参数:
        app (Flask): Flask 应用实例，用于获取配置信息。

        属性:
        folder (str): 存储文件的本地路径，从 Flask 应用配置中获取。如果路径不是绝对路径，则将其转换为绝对路径。
        """
        super().__init__(app)
        folder = self.app.config.get("STORAGE_LOCAL_PATH")
        if not os.path.isabs(folder):
            folder = os.path.join(app.root_path, folder)
        self.folder = folder

    def save(self, filename, data):
        """
        将数据保存到本地文件系统中。

        参数:
        filename (str): 文件名，包含相对路径。
        data (bytes): 要保存的二进制数据。

        逻辑:
        1. 根据 self.folder 的值，构造完整的文件路径。
        2. 如果文件路径的目录不存在，则创建目录。
        3. 将数据写入指定的文件路径。
        """
        # TODO 
        
        if not self.folder or self.folder.endswith("/"):
            filename = self.folder + filename
        else:
            filename = self.folder + "/" + filename

        # 获取文件路径的目录部分。os.path.dirname 函数返回路径中最后一个斜杠之前的部分，即文件所在的目录。
        folder = os.path.dirname(filename)
        os.makedirs(folder, exist_ok=True)

        Path(os.path.join(os.getcwd(), filename)).write_bytes(data)

    def load_once(self, filename: str) -> bytes:
        """
        一次性读取本地文件的全部内容。

        参数:
        filename (str): 文件名，包含相对路径。

        返回值:
        bytes: 文件的二进制内容。

        逻辑:
        1. 根据 self.folder 的值，构造完整的文件路径。
        2. 检查文件是否存在，如果不存在则抛出 FileNotFoundError 异常。
        3. 读取文件的全部内容并返回。
        """
        if not self.folder or self.folder.endswith("/"):
            filename = self.folder + filename
        else:
            filename = self.folder + "/" + filename

        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")
        # 这里使用 Path 类（来自 pathlib 模块）读取文件内容。Path(filename) 会根据给定的 filename 路径创建一个 Path 对象。
        data = Path(filename).read_bytes()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        以流的方式读取本地文件的内容。

        参数:
        filename (str): 文件名，包含相对路径。

        返回值:
        Generator: 生成器，每次生成 4KB 的文件数据块。

        逻辑:
        1. 根据 self.folder 的值，构造完整的文件路径。
        2. 检查文件是否存在，如果不存在则抛出 FileNotFoundError 异常。
        3. 打开文件并以 4KB 为单位读取数据块，每次生成一个数据块。
        """
        def generate(filename: str = filename) -> Generator:
            if not self.folder or self.folder.endswith("/"):
                filename = self.folder + filename
            else:
                filename = self.folder + "/" + filename

            if not os.path.exists(filename):
                raise FileNotFoundError("File not found")

            with open(filename, "rb") as f:
                while chunk := f.read(4096):  # 每次读取 4KB 的数据块
                    yield chunk

        return generate()

    def download(self, filename, target_filepath):
        """
        将本地文件下载到指定路径。

        参数:
        filename (str): 文件名，包含相对路径。
        target_filepath (str): 目标文件路径，包含文件名。

        逻辑:
        1. 根据 self.folder 的值，构造完整的文件路径。
        2. 检查文件是否存在，如果不存在则抛出 FileNotFoundError 异常。
        3. 使用 shutil.copyfile 将文件复制到目标路径。
        """
        if not self.folder or self.folder.endswith("/"):
            filename = self.folder + filename
        else:
            filename = self.folder + "/" + filename

        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        shutil.copyfile(filename, target_filepath)

    def exists(self, filename):
        """
        检查本地文件是否存在。

        参数:
        filename (str): 文件名，包含相对路径。

        返回值:
        bool: 如果文件存在返回 True，否则返回 False。

        逻辑:
        1. 根据 self.folder 的值，构造完整的文件路径。
        2. 使用 os.path.exists 检查文件是否存在。
        """
        if not self.folder or self.folder.endswith("/"):
            filename = self.folder + filename
        else:
            filename = self.folder + "/" + filename

        return os.path.exists(filename)

    def delete(self, filename):
        """
        删除本地文件。

        参数:
        filename (str): 文件名，包含相对路径。

        逻辑:
        1. 根据 self.folder 的值，构造完整的文件路径。
        2. 检查文件是否存在，如果存在则使用 os.remove 删除文件。
        """
        if not self.folder or self.folder.endswith("/"):
            filename = self.folder + filename
        else:
            filename = self.folder + "/" + filename
        if os.path.exists(filename):
            os.remove(filename)

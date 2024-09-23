from collections.abc import Generator
from typing import Union

from flask import Flask

from extensions.storage.aliyun_storage import AliyunStorage
from extensions.storage.azure_storage import AzureStorage
from extensions.storage.google_storage import GoogleStorage
from extensions.storage.huawei_storage import HuaweiStorage
from extensions.storage.local_storage import LocalStorage
from extensions.storage.oci_storage import OCIStorage
from extensions.storage.s3_storage import S3Storage
from extensions.storage.tencent_storage import TencentStorage
from extensions.storage.volcengine_storage import VolcengineStorage


class Storage:
    """
    存储类，用于根据配置选择不同的存储服务并提供统一的接口进行文件操作。

    属性:
        storage_runner: 存储服务的实例，根据配置初始化为不同的存储服务。
    """

    def __init__(self):
        """
        初始化存储类，设置 storage_runner 为 None。
        """
        self.storage_runner = None

    def init_app(self, app: Flask):
        """
        根据 Flask 应用的配置初始化存储服务。

        参数:
            app (Flask): Flask 应用实例，用于获取配置信息。

        逻辑:
            1. 从 Flask 应用配置中获取 STORAGE_TYPE。
            2. 根据 STORAGE_TYPE 的值初始化相应的存储服务实例。
            3. 如果 STORAGE_TYPE 未匹配任何已知类型，则默认使用本地存储。
        """
        storage_type = app.config.get("STORAGE_TYPE")
        if storage_type == "s3":
            self.storage_runner = S3Storage(app=app)
        elif storage_type == "azure-blob":
            self.storage_runner = AzureStorage(app=app)
        elif storage_type == "aliyun-oss":
            self.storage_runner = AliyunStorage(app=app)
        elif storage_type == "google-storage":
            self.storage_runner = GoogleStorage(app=app)
        elif storage_type == "tencent-cos":
            self.storage_runner = TencentStorage(app=app)
        elif storage_type == "oci-storage":
            self.storage_runner = OCIStorage(app=app)
        elif storage_type == "huawei-obs":
            self.storage_runner = HuaweiStorage(app=app)
        elif storage_type == "volcengine-tos":
            self.storage_runner = VolcengineStorage(app=app)
        else:
            self.storage_runner = LocalStorage(app=app)

    def save(self, filename, data):
        """
        保存数据到指定文件。

        参数:
            filename (str): 文件名。
            data: 要保存的数据。

        逻辑:
            调用当前存储服务的 save 方法保存数据。
        """
        self.storage_runner.save(filename, data)

    def load(self, filename: str, stream: bool = False) -> Union[bytes, Generator]:
        """
        加载指定文件的数据。

        参数:
            filename (str): 文件名。
            stream (bool): 是否以流的方式加载数据，默认为 False。

        返回值:
            如果 stream 为 False，返回文件内容的字节数据；
            如果 stream 为 True，返回生成器，用于流式读取文件内容。

        逻辑:
            根据 stream 参数决定调用 load_once 还是 load_stream 方法。
        """
        if stream:
            return self.load_stream(filename)
        else:
            return self.load_once(filename)

    def load_once(self, filename: str) -> bytes:
        """
        一次性加载指定文件的全部数据。

        参数:
            filename (str): 文件名。

        返回值:
            文件内容的字节数据。

        逻辑:
            调用当前存储服务的 load_once 方法加载数据。
        """
        return self.storage_runner.load_once(filename)

    def load_stream(self, filename: str) -> Generator:
        """
        以流的方式加载指定文件的数据。

        参数:
            filename (str): 文件名。

        返回值:
            生成器，用于流式读取文件内容。

        逻辑:
            调用当前存储服务的 load_stream 方法加载数据。
        """
        return self.storage_runner.load_stream(filename)

    def download(self, filename, target_filepath):
        """
        下载指定文件到本地路径。

        参数:
            filename (str): 文件名。
            target_filepath (str): 目标文件路径。

        逻辑:
            调用当前存储服务的 download 方法下载文件。
        """
        self.storage_runner.download(filename, target_filepath)

    def exists(self, filename):
        """
        检查指定文件是否存在。

        参数:
            filename (str): 文件名。

        返回值:
            布尔值，表示文件是否存在。

        逻辑:
            调用当前存储服务的 exists 方法检查文件是否存在。
        """
        return self.storage_runner.exists(filename)

    def delete(self, filename):
        """
        删除指定文件。

        参数:
            filename (str): 文件名。

        返回值:
            布尔值，表示文件是否成功删除。

        逻辑:
            调用当前存储服务的 delete 方法删除文件。
        """
        return self.storage_runner.delete(filename)


storage = Storage()


def init_app(app: Flask):
    """
    初始化 Flask 应用的存储服务。

    参数:
        app (Flask): Flask 应用实例。

    逻辑:
        调用 Storage 类的 init_app 方法初始化存储服务。
    """
    storage.init_app(app)

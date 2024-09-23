from collections.abc import Generator

import tos
from flask import Flask

from extensions.storage.base_storage import BaseStorage


class VolcengineStorage(BaseStorage):
    """
    实现火山引擎 TOS 存储的类。

    该类继承自 BaseStorage，主要用于与火山引擎 TOS 存储服务进行交互。它提供了文件的保存、加载、下载、检查存在性和删除等功能。

    属性:
    - app: Flask 应用实例，用于获取配置信息。
    - bucket_name: 存储桶名称，从 Flask 应用配置中获取。
    - client: tos.TosClientV2 实例，用于与火山引擎 TOS 服务进行交互。
    """

    def __init__(self, app: Flask):
        """
        初始化 VolcengineStorage 类。

        参数:
        - app: Flask 应用实例，用于获取配置信息。

        初始化过程中，会从 Flask 应用配置中获取存储桶名称、访问密钥 ID、秘密访问密钥、服务端点和区域名称，
        并使用这些信息初始化 tos.TosClientV2 实例。
        """
        super().__init__(app)  # 调用父类 BaseStorage 的初始化方法
        app_config = self.app.config  # 获取 Flask 应用程序的配置
        self.bucket_name = app_config.get("VOLCENGINE_TOS_BUCKET_NAME")  # 从配置中获取存储桶名称
        self.client = tos.TosClientV2(
            ak=app_config.get("VOLCENGINE_TOS_ACCESS_KEY"),  # 从配置中获取访问密钥 ID
            sk=app_config.get("VOLCENGINE_TOS_SECRET_KEY"),  # 从配置中获取秘密访问密钥
            endpoint=app_config.get("VOLCENGINE_TOS_ENDPOINT"),  # 从配置中获取服务端点
            region=app_config.get("VOLCENGINE_TOS_REGION"),  # 从配置中获取区域名称
        )

    def save(self, filename, data):
        """
        将数据保存到火山引擎 TOS 存储中。

        参数:
        - filename: 文件名，用于标识存储在 TOS 中的对象。
        - data: 要保存的数据，可以是字符串或字节流。

        该方法使用 tos.TosClientV2 的 put_object 方法将数据上传到指定的存储桶中。
        """
        self.client.put_object(bucket=self.bucket_name, key=filename, content=data)

    def load_once(self, filename: str) -> bytes:
        """
        从火山引擎 TOS 存储中一次性加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        bytes: 文件的二进制数据。

        该方法使用 tos.TosClientV2 的 get_object 方法获取对象，并读取其内容。
        """
        data = self.client.get_object(bucket=self.bucket_name, key=filename).read()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从火山引擎 TOS 存储中以流的方式加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        Generator: 生成器，每次生成 4096 字节的数据块。

        该方法使用 tos.TosClientV2 的 get_object 方法获取对象，并通过生成器逐块读取数据。
        """
        def generate(filename: str = filename) -> Generator:
            response = self.client.get_object(bucket=self.bucket_name, key=filename)
            while chunk := response.read(4096):
                yield chunk

        return generate()

    def download(self, filename, target_filepath):
        """
        从火山引擎 TOS 存储中下载文件到本地。

        参数:
        - filename: 文件名，标识要下载的对象。
        - target_filepath: 目标文件路径，指定下载文件的保存位置。

        该方法使用 tos.TosClientV2 的 get_object_to_file 方法将对象下载到指定路径。
        """
        self.client.get_object_to_file(bucket=self.bucket_name, key=filename, file_path=target_filepath)

    def exists(self, filename):
        """
        检查火山引擎 TOS 存储中是否存在指定文件。

        参数:
        - filename: 文件名，标识要检查的对象。

        返回值:
        bool: 如果文件存在返回 True，否则返回 False。

        该方法使用 tos.TosClientV2 的 head_object 方法检查对象是否存在，并根据响应状态码判断。
        """
        res = self.client.head_object(bucket=self.bucket_name, key=filename)
        if res.status_code != 200:
            return False
        return True

    def delete(self, filename):
        """
        从火山引擎 TOS 存储中删除指定文件。

        参数:
        - filename: 文件名，标识要删除的对象。

        该方法使用 tos.TosClientV2 的 delete_object 方法删除指定对象。
        """
        self.client.delete_object(bucket=self.bucket_name, key=filename)

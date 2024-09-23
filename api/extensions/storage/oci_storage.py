from collections.abc import Generator
from contextlib import closing

import boto3
from botocore.exceptions import ClientError
from flask import Flask

from extensions.storage.base_storage import BaseStorage


class OCIStorage(BaseStorage):
    """
    OCIStorage 类实现了与 Oracle Cloud Infrastructure (OCI) 存储服务的交互。
    该类继承自 BaseStorage，提供了文件的保存、加载、下载、检查存在性和删除等功能。

    属性:
    - app: Flask 应用实例，用于获取配置信息。
    - bucket_name: 存储桶名称，从 Flask 应用配置中获取。
    - client: boto3 客户端实例，用于与 OCI 存储服务进行交互。
    """

    def __init__(self, app: Flask):
        """
        初始化 OCIStorage 类。

        参数:
        - app: Flask 应用实例，用于获取配置信息。

        初始化过程中，会从 Flask 应用配置中获取存储桶名称、访问密钥 ID、秘密访问密钥、服务端点和区域名称，
        并使用这些信息初始化 boto3 客户端实例。
        """
        super().__init__(app)  # 调用父类 BaseStorage 的初始化方法
        app_config = self.app.config  # 获取 Flask 应用程序的配置
        self.bucket_name = app_config.get("OCI_BUCKET_NAME")  # 从配置中获取存储桶名称
        self.client = boto3.client(
            "s3",
            aws_secret_access_key=app_config.get("OCI_SECRET_KEY"),  # 从配置中获取秘密访问密钥
            aws_access_key_id=app_config.get("OCI_ACCESS_KEY"),  # 从配置中获取访问密钥 ID
            endpoint_url=app_config.get("OCI_ENDPOINT"),  # 从配置中获取服务端点
            region_name=app_config.get("OCI_REGION"),  # 从配置中获取区域名称
        )

    def save(self, filename, data):
        """
        将数据保存到 OCI 存储中。

        参数:
        - filename: 文件名，用于标识存储在 OCI 中的对象。
        - data: 要保存的数据，可以是字符串或字节流。

        该方法使用 boto3 客户端的 put_object 方法将数据上传到指定的存储桶中。
        """
        self.client.put_object(Bucket=self.bucket_name, Key=filename, Body=data)

    def load_once(self, filename: str) -> bytes:
        """
        从 OCI 存储中一次性加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        bytes: 文件的二进制数据。

        逻辑:
        1. 使用上下文管理器关闭客户端连接。
        2. 尝试获取对象数据。
        3. 如果文件不存在，抛出 FileNotFoundError 异常。
        4. 否则，返回文件的二进制数据。
        """
        try:
            with closing(self.client) as client:
                data = client.get_object(Bucket=self.bucket_name, Key=filename)["Body"].read()
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError("File not found")
            else:
                raise
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从 OCI 存储中以流的方式加载文件数据。

        参数:
        - filename: 文件名，用于在存储桶中标识文件。

        返回值:
        Generator: 生成器，每次生成文件的一部分数据。

        逻辑:
        1. 定义一个生成器函数 generate，用于逐块读取文件数据。
        2. 使用上下文管理器关闭客户端连接。
        3. 尝试获取对象数据。
        4. 如果文件不存在，抛出 FileNotFoundError 异常。
        5. 否则，逐块读取数据并生成。
        """
        def generate(filename: str = filename) -> Generator:
            try:
                with closing(self.client) as client:
                    response = client.get_object(Bucket=self.bucket_name, Key=filename)
                    yield from response["Body"].iter_chunks()
            except ClientError as ex:
                if ex.response["Error"]["Code"] == "NoSuchKey":
                    raise FileNotFoundError("File not found")
                else:
                    raise

        return generate()

    def download(self, filename, target_filepath):
        """
        从 OCI 存储中下载文件到本地。

        参数:
        - filename: 文件名，标识要下载的对象。
        - target_filepath: 目标文件路径，指定下载文件的本地存储位置。

        逻辑:
        1. 使用上下文管理器关闭客户端连接。
        2. 调用 download_file 方法将文件下载到指定路径。
        """
        with closing(self.client) as client:
            client.download_file(self.bucket_name, filename, target_filepath)

    def exists(self, filename):
        """
        检查 OCI 存储中是否存在指定文件。

        参数:
        - filename: 文件名，标识要检查的对象。

        返回值:
        bool: 如果文件存在返回 True，否则返回 False。

        逻辑:
        1. 使用上下文管理器关闭客户端连接。
        2. 尝试获取对象的元数据。
        3. 如果成功，返回 True。
        4. 如果失败，返回 False。
        """
        with closing(self.client) as client:
            try:
                client.head_object(Bucket=self.bucket_name, Key=filename)
                return True
            except:
                return False

    def delete(self, filename):
        """
        从 OCI 存储中删除指定文件。

        参数:
        - filename: 文件名，标识要删除的对象。

        逻辑:
        1. 调用 delete_object 方法删除指定文件。
        """
        self.client.delete_object(Bucket=self.bucket_name, Key=filename)

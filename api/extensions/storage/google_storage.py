import base64
import io
import json
from collections.abc import Generator
from contextlib import closing

from flask import Flask
from google.cloud import storage as google_cloud_storage

from extensions.storage.base_storage import BaseStorage

class GoogleStorage(BaseStorage):
    """
    实现 Google 存储的类。

    该类继承自 BaseStorage，主要用于与 Google Cloud Storage 进行交互。
    提供了文件的保存、加载、下载、检查存在性和删除等功能。
    """

    def __init__(self, app: Flask):
        """
        初始化 GoogleStorage 类。

        该方法的主要用途是设置 GoogleStorage 类的初始状态，包括从 Flask 配置中获取存储桶名称和 Google Cloud Storage 客户端实例。

        参数:
        app (Flask): Flask 应用程序实例，用于获取配置信息。

        属性:
        self.bucket_name (str): 存储桶名称，从 Flask 配置中获取。
        self.client (google_cloud_storage.Client): Google Cloud Storage 客户端实例，用于与 Google Cloud Storage 进行交互。
        """
        super().__init__(app)  # 调用父类 BaseStorage 的初始化方法
        app_config = self.app.config  # 获取 Flask 应用程序的配置
        self.bucket_name = app_config.get("GOOGLE_STORAGE_BUCKET_NAME")  # 从配置中获取存储桶名称
        service_account_json_str = app_config.get("GOOGLE_STORAGE_SERVICE_ACCOUNT_JSON_BASE64")  # 从配置中获取服务账户 JSON 字符串（Base64 编码）
        
        # 如果 service_account_json_str 为空，使用应用默认凭据
        if service_account_json_str:
            service_account_json = base64.b64decode(service_account_json_str).decode("utf-8")  # 解码 Base64 编码的服务账户 JSON 字符串
            # 将字符串转换为对象
            service_account_obj = json.loads(service_account_json)  # 将 JSON 字符串解析为 Python 对象
            self.client = google_cloud_storage.Client.from_service_account_info(service_account_obj)  # 使用服务账户信息创建 Google Cloud Storage 客户端实例
        else:
            self.client = google_cloud_storage.Client()  # 使用应用默认凭据创建 Google Cloud Storage 客户端实例

    def save(self, filename, data):
        """
        将数据保存到 Google Cloud Storage 中。

        该函数的主要用途是将指定的数据保存到 Google Cloud Storage 中的指定文件名下。

        参数:
        filename (str): 文件名，用于在存储桶中标识文件。该参数是一个字符串，表示要保存的文件的名称。
        data (bytes): 要保存的数据。该参数是一个字节对象，表示要上传到 Google Cloud Storage 的数据。

        逻辑:
        1. 获取存储桶实例。通过调用 `self.client.get_bucket(self.bucket_name)` 方法，获取与当前实例关联的存储桶实例。
        2. 创建一个 Blob 实例，表示存储桶中的文件。通过调用 `bucket.blob(filename)` 方法，创建一个表示存储桶中指定文件的 Blob 实例。
        3. 使用 io.BytesIO 将数据包装为流。通过 `io.BytesIO(data)` 将字节数据包装为一个流对象，以便后续上传操作。
        4. 将数据流上传到 Google Cloud Storage。通过调用 `blob.upload_from_file(stream)` 方法，将数据流上传到 Google Cloud Storage 中。

        返回值:
        该函数没有显式的返回值。上传操作成功后，数据将被保存到指定的文件名下。
        """
        bucket = self.client.get_bucket(self.bucket_name)  # 获取存储桶实例
        blob = bucket.blob(filename)  # 创建 Blob 实例
        with io.BytesIO(data) as stream:  # 将数据包装为流
            blob.upload_from_file(stream)  # 上传数据流

    def load_once(self, filename: str) -> bytes:
        """
        从 Google Cloud Storage 中一次性加载文件数据。

        参数:
        filename (str): 文件名，用于在存储桶中标识文件。

        返回值:
        bytes: 文件的二进制数据。

        逻辑:
        1. 获取存储桶实例。
        2. 获取 Blob 实例，表示存储桶中的文件。
        3. 下载文件的二进制数据并返回。
        """
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.get_blob(filename)
        data = blob.download_as_bytes()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从 Google Cloud Storage 中以流的方式加载文件数据。

        参数:
        filename (str): 文件名，用于在存储桶中标识文件。

        返回值:
        Generator: 生成器，每次生成文件的一部分数据。

        逻辑:
        1. 定义一个生成器函数 generate，用于逐块读取文件数据。
        2. 获取存储桶实例。
        3. 获取 Blob 实例，表示存储桶中的文件。
        4. 打开 Blob 流，逐块读取数据并生成。
        """
        def generate(filename: str = filename) -> Generator:
            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.get_blob(filename)
            with closing(blob.open(mode="rb")) as blob_stream:
                while chunk := blob_stream.read(4096):
                    yield chunk

        return generate()

    def download(self, filename, target_filepath):
        """
        将文件从 Google Cloud Storage 下载到本地文件系统。

        参数:
        filename (str): 文件名，用于在存储桶中标识文件。
        target_filepath (str): 目标文件路径，用于保存下载的文件。

        逻辑:
        1. 获取存储桶实例。
        2. 获取 Blob 实例，表示存储桶中的文件。
        3. 将文件下载到指定的本地路径。
        """
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.get_blob(filename)
        blob.download_to_filename(target_filepath)

    def exists(self, filename):
        """
        检查文件是否存在于 Google Cloud Storage 中。

        参数:
        filename (str): 文件名，用于在存储桶中标识文件。

        返回值:
        bool: 如果文件存在则返回 True，否则返回 False。

        逻辑:
        1. 获取存储桶实例。
        2. 创建一个 Blob 实例，表示存储桶中的文件。
        3. 检查文件是否存在并返回结果。
        """
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(filename)
        return blob.exists()

    def delete(self, filename):
        """
        从 Google Cloud Storage 中删除文件。

        参数:
        filename (str): 文件名，用于在存储桶中标识文件。

        逻辑:
        1. 获取存储桶实例。
        2. 删除指定的文件。
        """
        bucket = self.client.get_bucket(self.bucket_name)
        bucket.delete_blob(filename)


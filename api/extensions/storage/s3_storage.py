from collections.abc import Generator
from contextlib import closing

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from flask import Flask

from extensions.storage.base_storage import BaseStorage


class S3Storage(BaseStorage):
    """
    实现 S3 存储的类。

    该类继承自 BaseStorage，主要用于与 AWS S3 存储服务进行交互。它提供了文件的保存、加载、下载、检查存在性和删除等功能。
    """

    def __init__(self, app: Flask):
        """
        初始化 S3Storage 类。

        参数:
        app (Flask): Flask 应用程序实例，用于获取配置信息。

        属性:
        bucket_name (str): S3 存储桶的名称，从 Flask 配置中获取。
        client (boto3.client): S3 客户端，用于与 S3 服务进行交互。
        """
        super().__init__(app)
        app_config = self.app.config
        self.bucket_name = app_config.get("S3_BUCKET_NAME")
        
        # 根据配置决定是否使用 AWS 托管的 IAM 角色
        if app_config.get("S3_USE_AWS_MANAGED_IAM"):
            session = boto3.Session()
            self.client = session.client("s3")
        else:
            # 使用提供的访问密钥和配置创建 S3 客户端
            self.client = boto3.client(
                "s3",
                aws_secret_access_key=app_config.get("S3_SECRET_KEY"),
                aws_access_key_id=app_config.get("S3_ACCESS_KEY"),
                endpoint_url=app_config.get("S3_ENDPOINT"),
                region_name=app_config.get("S3_REGION"),
                config=Config(s3={"addressing_style": app_config.get("S3_ADDRESS_STYLE")}),
            )
        
        # 尝试检查存储桶是否存在，如果不存在则创建
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            # 如果存储桶不存在，创建它
            if e.response["Error"]["Code"] == "404":
                self.client.create_bucket(Bucket=self.bucket_name)
            # 如果存储桶不可访问，可能是存在的但不可访问，跳过
            elif e.response["Error"]["Code"] == "403":
                pass
            else:
                # 其他错误，抛出异常
                raise

    def save(self, filename, data):
        """
        将数据保存到 S3 存储桶中。

        参数:
        filename (str): 文件名，用于在 S3 中标识对象。
        data (bytes): 要保存的数据。
        """
        self.client.put_object(Bucket=self.bucket_name, Key=filename, Body=data)

    def load_once(self, filename: str) -> bytes:
        """
        从 S3 存储桶中一次性加载文件数据。

        参数:
        filename (str): 文件名，用于在 S3 中标识对象。

        返回:
        bytes: 文件的数据。

        异常:
        FileNotFoundError: 如果文件不存在。
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
        从 S3 存储桶中流式加载文件数据。

        参数:
        filename (str): 文件名，用于在 S3 中标识对象。

        返回:
        Generator: 生成器，逐块生成文件数据。

        异常:
        FileNotFoundError: 如果文件不存在。
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
        从 S3 存储桶中下载文件到本地文件系统。

        参数:
        filename (str): 文件名，用于在 S3 中标识对象。
        target_filepath (str): 目标文件路径，用于保存下载的文件。
        """
        with closing(self.client) as client:
            client.download_file(self.bucket_name, filename, target_filepath)

    def exists(self, filename):
        """
        检查 S3 存储桶中是否存在指定文件。

        参数:
        filename (str): 文件名，用于在 S3 中标识对象。

        返回:
        bool: 如果文件存在则返回 True，否则返回 False。
        """
        with closing(self.client) as client:
            try:
                client.head_object(Bucket=self.bucket_name, Key=filename)
                return True
            except:
                return False

    def delete(self, filename):
        """
        从 S3 存储桶中删除指定文件。

        参数:
        filename (str): 文件名，用于在 S3 中标识对象。
        """
        self.client.delete_object(Bucket=self.bucket_name, Key=filename)

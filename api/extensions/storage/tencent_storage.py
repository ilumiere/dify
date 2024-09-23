from collections.abc import Generator

from flask import Flask
from qcloud_cos import CosConfig, CosS3Client

from extensions.storage.base_storage import BaseStorage


class TencentStorage(BaseStorage):
    """
    腾讯云对象存储（COS）的实现类。

    该类继承自BaseStorage，提供了与腾讯云COS存储服务交互的功能。
    主要用途是管理存储在腾讯云COS中的对象，包括上传、下载、删除等操作。

    属性:
    - app: Flask应用实例，用于获取配置信息。
    - bucket_name: 存储桶名称，从Flask应用配置中获取。
    - client: CosS3Client实例，用于与腾讯云COS服务进行交互。
    """

    def __init__(self, app: Flask):
        """
        初始化TencentStorage类。

        参数:
        - app: Flask应用实例，用于获取配置信息。

        初始化过程中，会从Flask应用配置中获取存储桶名称、区域、访问密钥ID、秘密访问密钥和服务器地址，
        并使用这些信息初始化CosS3Client实例。
        """
        super().__init__(app)  # 调用父类BaseStorage的初始化方法
        app_config = self.app.config  # 获取Flask应用程序的配置
        self.bucket_name = app_config.get("TENCENT_COS_BUCKET_NAME")  # 从配置中获取存储桶名称
        config = CosConfig(
            Region=app_config.get("TENCENT_COS_REGION"),  # 从配置中获取区域
            SecretId=app_config.get("TENCENT_COS_SECRET_ID"),  # 从配置中获取访问密钥ID
            SecretKey=app_config.get("TENCENT_COS_SECRET_KEY"),  # 从配置中获取秘密访问密钥
            Scheme=app_config.get("TENCENT_COS_SCHEME"),  # 从配置中获取协议（如http或https）
        )
        self.client = CosS3Client(config)  # 初始化CosS3Client实例

    def save(self, filename, data):
        """
        将数据保存到腾讯云COS存储中。

        参数:
        - filename: 文件名，用于标识存储在COS中的对象。
        - data: 要保存的数据，可以是字符串或字节流。

        该方法使用CosS3Client的put_object方法将数据上传到指定的存储桶中。
        """
        self.client.put_object(Bucket=self.bucket_name, Body=data, Key=filename)

    def load_once(self, filename: str) -> bytes:
        """
        从腾讯云COS存储中一次性加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        bytes: 文件的二进制数据。

        逻辑:
        1. 使用CosS3Client的get_object方法获取对象。
        2. 从响应中获取原始数据流并读取数据。
        """
        data = self.client.get_object(Bucket=self.bucket_name, Key=filename)["Body"].get_raw_stream().read()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从腾讯云COS存储中以流的方式加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        Generator: 生成器，每次生成文件的一部分数据。

        逻辑:
        1. 定义一个生成器函数generate，用于逐块读取文件数据。
        2. 使用CosS3Client的get_object方法获取对象。
        3. 逐块读取数据并生成。
        """
        def generate(filename: str = filename) -> Generator:
            response = self.client.get_object(Bucket=self.bucket_name, Key=filename)
            yield from response["Body"].get_stream(chunk_size=4096)

        return generate()

    def download(self, filename, target_filepath):
        """
        从腾讯云COS存储中下载文件到本地。

        参数:
        - filename: 文件名，标识要下载的对象。
        - target_filepath: 目标文件路径，指定下载文件的本地存储位置。

        逻辑:
        1. 使用CosS3Client的get_object方法获取对象。
        2. 将获取到的数据流写入到目标文件路径。
        """
        response = self.client.get_object(Bucket=self.bucket_name, Key=filename)
        response["Body"].get_stream_to_file(target_filepath)

    def exists(self, filename):
        """
        检查腾讯云COS存储中是否存在指定文件。

        参数:
        - filename: 文件名，标识要检查的对象。

        返回值:
        bool: 如果文件存在返回True，否则返回False。

        逻辑:
        使用CosS3Client的object_exists方法检查对象是否存在。
        """
        return self.client.object_exists(Bucket=self.bucket_name, Key=filename)

    def delete(self, filename):
        """
        从腾讯云COS存储中删除指定文件。

        参数:
        - filename: 文件名，标识要删除的对象。

        逻辑:
        使用CosS3Client的delete_object方法删除对象。
        """
        self.client.delete_object(Bucket=self.bucket_name, Key=filename)

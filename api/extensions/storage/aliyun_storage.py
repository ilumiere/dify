from collections.abc import Generator
from contextlib import closing

import oss2 as aliyun_s3
from flask import Flask

from extensions.storage.base_storage import BaseStorage


class AliyunStorage(BaseStorage):
    """
    阿里云存储的实现类。

    该类继承自 `BaseStorage`，用于与阿里云 OSS（对象存储服务）进行交互。它提供了文件的保存、加载、下载、检查存在性、删除等功能。
    """

    def __init__(self, app: Flask):
        """
        初始化阿里云存储对象。

        该方法用于初始化 `AliyunStorage` 类，设置与阿里云 OSS 交互所需的配置和客户端对象。

        参数:
        - app (Flask): Flask 应用实例，用于获取配置信息。

        属性:
        - bucket_name (str): 存储桶名称，从配置中获取。
        - folder (str): 存储路径，从配置中获取。
        - client (aliyun_s3.Bucket): 阿里云 OSS 客户端对象，用于与 OSS 进行交互。
        """
        super().__init__(app)  # 调用父类 `BaseStorage` 的初始化方法，传递 Flask 应用实例。

        app_config = self.app.config  # 获取 Flask 应用的配置信息。
        self.bucket_name = app_config.get("ALIYUN_OSS_BUCKET_NAME")  # 从配置中获取存储桶名称。
        self.folder = app.config.get("ALIYUN_OSS_PATH")  # 从配置中获取存储路径。

        # 根据配置选择认证方法，默认为 `aliyun_s3.Auth`。
        oss_auth_method = aliyun_s3.Auth
        region = None
        if app_config.get("ALIYUN_OSS_AUTH_VERSION") == "v4":
            oss_auth_method = aliyun_s3.AuthV4  # 如果认证版本为 v4，则使用 `aliyun_s3.AuthV4`。
            region = app_config.get("ALIYUN_OSS_REGION")  # 获取区域信息。

        # 使用选择的认证方法和配置中的访问密钥、秘密密钥创建认证对象。
        oss_auth = oss_auth_method(app_config.get("ALIYUN_OSS_ACCESS_KEY"), app_config.get("ALIYUN_OSS_SECRET_KEY"))

        # 创建阿里云 OSS 客户端对象，用于与 OSS 进行交互。
        self.client = aliyun_s3.Bucket(
            oss_auth,  # 认证对象
            app_config.get("ALIYUN_OSS_ENDPOINT"),  # OSS 终端节点
            self.bucket_name,  # 存储桶名称
            connect_timeout=30,  # 连接超时时间，设置为 30 秒
            region=region,  # 区域信息，如果认证版本为 v4 则使用配置中的区域信息
        )

    def save(self, filename, data):
        """
        将数据保存到阿里云 OSS。

        参数:
        - filename (str): 文件名。
        - data: 要保存的数据。

        该方法将数据保存到指定的文件名中，文件名会根据 `folder` 属性进行包装。
        """
        self.client.put_object(self.__wrapper_folder_filename(filename), data)

    def load_once(self, filename: str) -> bytes:
        """
        从阿里云 OSS 加载数据，一次性读取所有数据。

        参数:
        - filename (str): 文件名。

        返回值:
        - bytes: 文件内容的字节数据。

        该方法从指定的文件名中读取数据，并返回字节数据。
        """
        with closing(self.client.get_object(self.__wrapper_folder_filename(filename))) as obj:
            data = obj.read()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从阿里云 OSS 加载数据，以流的方式读取数据。

        参数:
        - filename (str): 文件名。

        返回值:
        - Generator: 生成器，每次生成 4096 字节的数据块。

        该方法以流的方式读取数据，每次生成 4096 字节的数据块。
        with closing:
        closing 是 contextlib 模块中的一个上下文管理器，它包装了一个对象，并在 with 块结束时调用该对象的 close 方法。
        在这个例子中，self.client.get_object 返回的对象有一个 close 方法，
        使用 with closing 可以确保在读取完数据后，对象的 close 方法会被调用，从而释放资源。
        """
        def generate(filename: str = filename) -> Generator:
            with closing(self.client.get_object(self.__wrapper_folder_filename(filename))) as obj:
                while chunk := obj.read(4096):
                    yield chunk

        return generate()

    def download(self, filename, target_filepath):
        """
        从阿里云 OSS 下载文件到本地。

        参数:
        - filename (str): 文件名。
        - target_filepath (str): 目标文件路径。

        该方法将指定的文件下载到本地文件系统中。
        """
        self.client.get_object_to_file(self.__wrapper_folder_filename(filename), target_filepath)

    def exists(self, filename):
        """
        检查文件是否存在于阿里云 OSS。

        参数:
        - filename (str): 文件名。

        返回值:
        - bool: 如果文件存在返回 True，否则返回 False。

        该方法检查指定的文件是否存在于 OSS 中。
        """
        return self.client.object_exists(self.__wrapper_folder_filename(filename))

    def delete(self, filename):
        """
        从阿里云 OSS 删除文件。

        参数:
        - filename (str): 文件名。

        该方法删除指定的文件。
        """
        self.client.delete_object(self.__wrapper_folder_filename(filename))

    def __wrapper_folder_filename(self, filename) -> str:
        """
        包装文件名，添加存储路径前缀。

        参数:
        - filename (str): 文件名。

        返回值:
        - str: 包装后的文件名。

        该方法根据 `folder` 属性包装文件名，确保文件名包含存储路径前缀。
        """
        if self.folder:
            if self.folder.endswith("/"):
                filename = self.folder + filename
            else:
                filename = self.folder + "/" + filename
        return filename

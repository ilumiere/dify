from collections.abc import Generator

from flask import Flask
from obs import ObsClient

from extensions.storage.base_storage import BaseStorage


class HuaweiStorage(BaseStorage):
    """
    华为OBS存储的实现类。

    该类继承自BaseStorage，提供了与华为OBS存储服务交互的功能。
    主要用途是管理存储在华为OBS中的对象，包括上传、下载、删除等操作。

    属性:
    - app: Flask应用实例，用于获取配置信息。
    - bucket_name: 存储桶名称，从Flask应用配置中获取。
    - client: ObsClient实例，用于与华为OBS服务进行交互。
    """

    def __init__(self, app: Flask):
        """
        初始化HuaweiStorage类。

        参数:
        - app: Flask应用实例，用于获取配置信息。

        初始化过程中，会从Flask应用配置中获取存储桶名称、访问密钥ID、秘密访问密钥和服务器地址，
        并使用这些信息初始化ObsClient实例。
        """
        super().__init__(app)
        app_config = self.app.config
        self.bucket_name = app_config.get("HUAWEI_OBS_BUCKET_NAME")
        self.client = ObsClient(
            access_key_id=app_config.get("HUAWEI_OBS_ACCESS_KEY"),
            secret_access_key=app_config.get("HUAWEI_OBS_SECRET_KEY"),
            server=app_config.get("HUAWEI_OBS_SERVER"),
        )

    def save(self, filename, data):
        """
        将数据保存到华为OBS存储中。

        参数:
        - filename: 文件名，用于标识存储在OBS中的对象。
        - data: 要保存的数据，可以是字符串或字节流。

        该方法使用ObsClient的putObject方法将数据上传到指定的存储桶中。
        """
        self.client.putObject(bucketName=self.bucket_name, objectKey=filename, content=data)

    def load_once(self, filename: str) -> bytes:
        """
        从华为OBS存储中一次性加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        - bytes: 加载的数据，以字节形式返回。

        该方法使用ObsClient的getObject方法从指定的存储桶中获取对象，并返回其内容。
        """
        data = self.client.getObject(bucketName=self.bucket_name, objectKey=filename)["body"].response.read()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从华为OBS存储中以流的方式加载数据。

        参数:
        - filename: 文件名，标识要加载的对象。

        返回值:
        - Generator: 生成器，每次生成4096字节的数据。

        该方法使用ObsClient的getObject方法从指定的存储桶中获取对象，并通过生成器逐块返回数据。
        """
        def generate(filename: str = filename) -> Generator:
            response = self.client.getObject(bucketName=self.bucket_name, objectKey=filename)["body"].response
            yield from response.read(4096)

        return generate()

    def download(self, filename, target_filepath):
        """
        从华为OBS存储中下载文件到本地。

        参数:
        - filename: 文件名，标识要下载的对象。
        - target_filepath: 目标文件路径，指定下载文件的本地存储位置。

        该方法使用ObsClient的getObject方法从指定的存储桶中获取对象，并将其下载到本地指定路径。
        """
        self.client.getObject(bucketName=self.bucket_name, objectKey=filename, downloadPath=target_filepath)

    def exists(self, filename):
        """
        检查华为OBS存储中是否存在指定对象。

        参数:
        - filename: 文件名，标识要检查的对象。

        返回值:
        - bool: 如果对象存在返回True，否则返回False。

        该方法通过调用_get_meta方法获取对象的元数据，如果元数据存在则返回True，否则返回False。
        """
        res = self._get_meta(filename)
        if res is None:
            return False
        return True

    def delete(self, filename):
        """
        从华为OBS存储中删除指定对象。

        参数:
        - filename: 文件名，标识要删除的对象。

        该方法使用ObsClient的deleteObject方法从指定的存储桶中删除对象。
        """
        self.client.deleteObject(bucketName=self.bucket_name, objectKey=filename)

    def _get_meta(self, filename):
        """
        获取华为OBS存储中指定对象的元数据。

        参数:
        - filename: 文件名，标识要获取元数据的对象。

        返回值:
        - dict: 对象的元数据，如果对象不存在返回None。

        该方法使用ObsClient的getObjectMetadata方法获取对象的元数据，如果请求成功（状态码小于300），
        则返回元数据，否则返回None。
        """
        res = self.client.getObjectMetadata(bucketName=self.bucket_name, objectKey=filename)
        if res.status < 300:
            return res
        else:
            return None

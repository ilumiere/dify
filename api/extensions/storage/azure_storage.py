from collections.abc import Generator
from datetime import datetime, timedelta, timezone

from azure.storage.blob import AccountSasPermissions, BlobServiceClient, ResourceTypes, generate_account_sas
from flask import Flask

from extensions.ext_redis import redis_client
from extensions.storage.base_storage import BaseStorage


class AzureStorage(BaseStorage):
    """
    实现 Azure 存储的类。

    该类继承自 BaseStorage，主要用于与 Azure Blob 存储进行交互。它提供了保存、加载、下载、检查存在性、删除等操作。
    """

    def __init__(self, app: Flask):
        """
        初始化 AzureStorage 类。

        参数:
        - app (Flask): Flask 应用程序实例，用于获取配置信息。

        属性:
        - bucket_name (str): Azure Blob 存储的容器名称，从配置中获取。
        - account_url (str): Azure Blob 存储的账户 URL，从配置中获取。
        - account_name (str): Azure Blob 存储的账户名称，从配置中获取。
        - account_key (str): Azure Blob 存储的账户密钥，从配置中获取。
        """
        super().__init__(app)
        app_config = self.app.config
        self.bucket_name = app_config.get("AZURE_BLOB_CONTAINER_NAME")
        self.account_url = app_config.get("AZURE_BLOB_ACCOUNT_URL")
        self.account_name = app_config.get("AZURE_BLOB_ACCOUNT_NAME")
        self.account_key = app_config.get("AZURE_BLOB_ACCOUNT_KEY")

    def save(self, filename, data):
        """
        将数据保存到 Azure Blob 存储中。

        参数:
        - filename (str): 要保存的文件名。
        - data: 要保存的数据。

        逻辑:
        1. 获取同步客户端。
        2. 获取容器客户端。
        3. 将数据上传到指定的文件名。
        """
        client = self._sync_client()
        blob_container = client.get_container_client(container=self.bucket_name)
        blob_container.upload_blob(filename, data)

    def load_once(self, filename: str) -> bytes:
        """
        从 Azure Blob 存储中一次性加载数据。

        参数:
        - filename (str): 要加载的文件名。

        返回值:
        - bytes: 加载的数据。

        逻辑:
        1. 获取同步客户端。
        2. 获取容器客户端。
        3. 获取 Blob 客户端。
        4. 下载 Blob 数据并读取所有内容。
        """
        client = self._sync_client()
        blob = client.get_container_client(container=self.bucket_name)
        blob = blob.get_blob_client(blob=filename)
        data = blob.download_blob().readall()
        return data

    def load_stream(self, filename: str) -> Generator:
        """
        从 Azure Blob 存储中以流的方式加载数据。

        参数:
        - filename (str): 要加载的文件名。

        返回值:
        - Generator: 生成器，用于逐块读取数据。

        逻辑:
        1. 获取同步客户端。
        2. 定义生成器函数，用于逐块读取 Blob 数据。
        3. 返回生成器。
        """
        client = self._sync_client()

        def generate(filename: str = filename) -> Generator:
            blob = client.get_blob_client(container=self.bucket_name, blob=filename)
            blob_data = blob.download_blob()
            yield from blob_data.chunks()

        return generate(filename)

    def download(self, filename, target_filepath):
        """
        从 Azure Blob 存储中下载文件到本地。

        参数:
        - filename (str): 要下载的文件名。
        - target_filepath (str): 本地目标文件路径。

        逻辑:
        1. 获取同步客户端。
        2. 获取 Blob 客户端。
        3. 打开本地文件并下载 Blob 数据到文件中。
        """
        client = self._sync_client()
        blob = client.get_blob_client(container=self.bucket_name, blob=filename)
        with open(target_filepath, "wb") as my_blob:
            blob_data = blob.download_blob()
            blob_data.readinto(my_blob)

    def exists(self, filename):
        """
        检查 Azure Blob 存储中是否存在指定文件。

        参数:
        - filename (str): 要检查的文件名。

        返回值:
        - bool: 如果文件存在则返回 True，否则返回 False。

        逻辑:
        1. 获取同步客户端。
        2. 获取 Blob 客户端。
        3. 检查 Blob 是否存在。
        """
        client = self._sync_client()
        blob = client.get_blob_client(container=self.bucket_name, blob=filename)
        return blob.exists()

    def delete(self, filename):
        """
        从 Azure Blob 存储中删除指定文件。

        参数:
        - filename (str): 要删除的文件名。

        逻辑:
        1. 获取同步客户端。
        2. 获取容器客户端。
        3. 删除指定的 Blob。
        """
        client = self._sync_client()
        blob_container = client.get_container_client(container=self.bucket_name)
        blob_container.delete_blob(filename)

    def _sync_client(self):
        """
        获取 Azure Blob 存储的同步客户端。

        该函数的主要用途是获取 Azure Blob 存储的同步客户端实例。它首先尝试从 Redis 缓存中获取 SAS 令牌，如果缓存中没有，则生成新的 SAS 令牌并存储到缓存中。最后，使用 SAS 令牌创建并返回 BlobServiceClient 实例。

        逻辑:
        1. 生成缓存键。
        2. 尝试从 Redis 缓存中获取 SAS 令牌。
        3. 如果缓存中没有 SAS 令牌，则生成新的 SAS 令牌并存储到缓存中。
        4. 返回 BlobServiceClient 实例。

        返回值:
        - BlobServiceClient: Azure Blob 存储的客户端实例。
        """
        # 生成缓存键，用于在 Redis 缓存中存储和检索 SAS 令牌
        cache_key = "azure_blob_sas_token_{}_{}".format(self.account_name, self.account_key)
        
        # 尝试从 Redis 缓存中获取 SAS 令牌
        cache_result = redis_client.get(cache_key)
        
        # 如果缓存中存在 SAS 令牌，则解码并使用
        if cache_result is not None:
            sas_token = cache_result.decode("utf-8")
        else:
            # 如果缓存中没有 SAS 令牌，则生成新的 SAS 令牌
            sas_token = generate_account_sas(
                account_name=self.account_name,  # Azure 存储账户名称
                account_key=self.account_key,    # Azure 存储账户密钥
                resource_types=ResourceTypes(service=True, container=True, object=True),  # 资源类型，允许服务、容器和对象操作
                permission=AccountSasPermissions(read=True, write=True, delete=True, list=True, add=True, create=True),  # 权限，允许读、写、删除、列出、添加和创建操作
                expiry=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),  # SAS 令牌的过期时间，当前时间加上1小时
            )
            # 将新生成的 SAS 令牌存储到 Redis 缓存中，并设置过期时间为3000秒
            redis_client.set(cache_key, sas_token, ex=3000)
        
        # 使用 SAS 令牌创建并返回 BlobServiceClient 实例
        return BlobServiceClient(account_url=self.account_url, credential=sas_token)

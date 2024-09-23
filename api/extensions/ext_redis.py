import redis
from redis.connection import Connection, SSLConnection
from redis.sentinel import Sentinel

class RedisClientWrapper(redis.Redis):
    """
    这是一个 Redis 客户端的包装类，用于解决在 Sentinel 返回新的 Redis 实例时无法更新全局 `redis_client` 变量的问题。

    该类允许延迟初始化 Redis 客户端，并在必要时使用新实例重新初始化客户端。这在 Redis 实例可能动态变化的场景中特别有用，例如在 Sentinel 管理的 Redis 设置中发生故障转移时。

    属性:
        _client (redis.Redis): 实际的 Redis 客户端实例。在通过 `initialize` 方法初始化之前，它保持为 None。

    方法:
        initialize(client): 如果 Redis 客户端尚未初始化，则初始化它。
        __getattr__(item): 将属性访问委托给 Redis 客户端，如果客户端未初始化，则引发错误。
    """

    def __init__(self):
        """
        初始化 RedisClientWrapper 实例。

        属性:
            _client (redis.Redis): 初始化为 None，表示 Redis 客户端尚未初始化。
        """
        self._client = None

    def initialize(self, client):
        """
        初始化 Redis 客户端。

        参数:
            client (redis.Redis): 要初始化的 Redis 客户端实例。

        逻辑:
            如果 `_client` 属性为 None，则将其设置为传入的 `client` 实例。
        """
        if self._client is None:
            self._client = client

    def __getattr__(self, item):
        """
        将属性访问委托给 Redis 客户端。

        参数:
            item (str): 要访问的属性名称。

        逻辑:
            如果 `_client` 属性为 None，则抛出 RuntimeError，提示需要先调用 `init_app` 方法。
            否则，返回 `_client` 实例的指定属性。

        返回值:
            返回 `_client` 实例的指定属性。

        异常:
            RuntimeError: 如果 Redis 客户端未初始化。
        """
        if self._client is None:
            raise RuntimeError("Redis client is not initialized. Call init_app first.")
        return getattr(self._client, item)


redis_client = RedisClientWrapper()


def init_app(app):
    """
    初始化应用程序的 Redis 客户端。

    该函数的主要用途是根据 Flask 应用程序的配置初始化 Redis 客户端，并将其添加到 Flask 应用程序的扩展中。

    参数:
        app (Flask app): Flask 应用程序实例，用于获取配置信息。

    逻辑:
        1. 获取全局 `redis_client` 实例。
        2. 根据配置确定连接类（Connection 或 SSLConnection）。
        3. 构建 Redis 连接参数。
        4. 如果使用 Sentinel，则配置 Sentinel 并获取主节点，初始化 `redis_client`。
        5. 否则，直接配置 Redis 连接池并初始化 `redis_client`。
        6. 将 `redis_client` 添加到 Flask 应用程序的扩展中。

    返回值:
        无返回值。
    """
    global redis_client  # 获取全局 `redis_client` 实例
    connection_class = Connection  # 默认使用普通连接类
    if app.config.get("REDIS_USE_SSL"):  # 如果配置中启用了 SSL
        connection_class = SSLConnection  # 使用 SSL 连接类

    redis_params = {
        "username": app.config.get("REDIS_USERNAME"),  # Redis 用户名
        "password": app.config.get("REDIS_PASSWORD"),  # Redis 密码
        "db": app.config.get("REDIS_DB"),  # 数据库编号
        "encoding": "utf-8",  # 编码方式
        "encoding_errors": "strict",  # 编码错误处理方式
        "decode_responses": False,  # 不自动解码响应
    }

    if app.config.get("REDIS_USE_SENTINEL"):  # 如果配置中启用了 Sentinel
        sentinel_hosts = [
            (node.split(":")[0], int(node.split(":")[1])) for node in app.config.get("REDIS_SENTINELS").split(",")
        ]  # 解析 Sentinel 主机列表
        sentinel = Sentinel(
            sentinel_hosts,
            sentinel_kwargs={
                "socket_timeout": app.config.get("REDIS_SENTINEL_SOCKET_TIMEOUT", 0.1),  # Sentinel 连接超时时间
                "username": app.config.get("REDIS_SENTINEL_USERNAME"),  # Sentinel 用户名
                "password": app.config.get("REDIS_SENTINEL_PASSWORD"),  # Sentinel 密码
            },
        )  # 初始化 Sentinel 实例
        master = sentinel.master_for(app.config.get("REDIS_SENTINEL_SERVICE_NAME"), **redis_params)  # 获取主节点
        redis_client.initialize(master)  # 初始化 `redis_client`
    else:  # 如果未启用 Sentinel
        redis_params.update(
            {
                "host": app.config.get("REDIS_HOST"),  # Redis 主机
                "port": app.config.get("REDIS_PORT"),  # Redis 端口
                "connection_class": connection_class,  # 连接类
            }
        )
        pool = redis.ConnectionPool(**redis_params)  # 创建连接池
        redis_client.initialize(redis.Redis(connection_pool=pool))  # 初始化 `redis_client`

    app.extensions["redis"] = redis_client  # 将 `redis_client` 添加到 Flask 应用程序的扩展中

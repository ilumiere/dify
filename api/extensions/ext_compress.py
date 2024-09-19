from flask import Flask

# Compress 是 Flask-Compress 扩展的一个类，用于在 Flask 应用中启用 Gzip 压缩。通过使用 Compress，可以减少传输的数据量，从而提高应用的性能。
# 具体作用
# 1. 启用 Gzip 压缩：Compress 会自动对指定的 MIME 类型进行 Gzip 压缩，从而减少传输的数据量。
# 2. 配置 MIME 类型：你可以通过 app.config["COMPRESS_MIMETYPES"] 配置需要压缩的 MIME 类型。

def init_app(app: Flask):
    if app.config.get("API_COMPRESSION_ENABLED"):
        from flask_compress import Compress

        # 自动对 application/json、image/svg+xml 和 text/html 类型的响应进行 Gzip 压缩
        app.config["COMPRESS_MIMETYPES"] = [
            "application/json",
            "image/svg+xml",
            "text/html",
        ]

        compress = Compress()
        compress.init_app(app)

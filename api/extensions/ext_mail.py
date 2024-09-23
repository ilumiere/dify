import logging
from typing import Optional

import resend
from flask import Flask


class Mail:
    """
    邮件类，用于初始化和发送邮件。支持两种邮件发送方式：Resend API 和 SMTP。
    """

    def __init__(self):
        """
        初始化 Mail 类。

        属性:
        - _client: 邮件客户端对象，初始为 None。
        - _default_send_from: 默认发件人地址，初始为 None。
        """
        self._client = None
        self._default_send_from = None

    def is_inited(self) -> bool:
        """
        检查邮件客户端是否已初始化。

        返回值:
        - bool: 如果 _client 不为 None，则返回 True，否则返回 False。
        """
        return self._client is not None

    def init_app(self, app: Flask):
        """
        根据 Flask 应用的配置初始化邮件客户端。

        参数:
        - app: Flask 应用对象，包含邮件配置信息。

        逻辑:
        - 检查 MAIL_TYPE 配置是否存在。
        - 如果存在，根据 MAIL_TYPE 的值初始化相应的邮件客户端。
        - 如果 MAIL_TYPE 为 "resend"，则使用 Resend API 初始化客户端。
        - 如果 MAIL_TYPE 为 "smtp"，则使用 SMTP 初始化客户端。
        - 如果 MAIL_TYPE 未设置或不支持，记录警告信息。
        """
        if app.config.get("MAIL_TYPE"):
            if app.config.get("MAIL_DEFAULT_SEND_FROM"):
                self._default_send_from = app.config.get("MAIL_DEFAULT_SEND_FROM")

            if app.config.get("MAIL_TYPE") == "resend":
                api_key = app.config.get("RESEND_API_KEY")
                if not api_key:
                    raise ValueError("RESEND_API_KEY is not set")

                api_url = app.config.get("RESEND_API_URL")
                if api_url:
                    resend.api_url = api_url

                resend.api_key = api_key
                self._client = resend.Emails
            elif app.config.get("MAIL_TYPE") == "smtp":
                from libs.smtp import SMTPClient

                if not app.config.get("SMTP_SERVER") or not app.config.get("SMTP_PORT"):
                    raise ValueError("SMTP_SERVER and SMTP_PORT are required for smtp mail type")
                if not app.config.get("SMTP_USE_TLS") and app.config.get("SMTP_OPPORTUNISTIC_TLS"):
                    raise ValueError("SMTP_OPPORTUNISTIC_TLS is not supported without enabling SMTP_USE_TLS")
                self._client = SMTPClient(
                    server=app.config.get("SMTP_SERVER"),
                    port=app.config.get("SMTP_PORT"),
                    username=app.config.get("SMTP_USERNAME"),
                    password=app.config.get("SMTP_PASSWORD"),
                    _from=app.config.get("MAIL_DEFAULT_SEND_FROM"),
                    use_tls=app.config.get("SMTP_USE_TLS"),
                    opportunistic_tls=app.config.get("SMTP_OPPORTUNISTIC_TLS"),
                )
            else:
                raise ValueError("Unsupported mail type {}".format(app.config.get("MAIL_TYPE")))
        else:
            logging.warning("MAIL_TYPE is not set")

    def send(self, to: str, subject: str, html: str, from_: Optional[str] = None):
        """
        发送邮件。

        参数:
        - to: 收件人地址，字符串类型。
        - subject: 邮件主题，字符串类型。
        - html: 邮件内容，HTML 格式，字符串类型。
        - from_: 发件人地址，可选参数，字符串类型。

        逻辑:
        - 检查邮件客户端是否已初始化。
        - 如果 from_ 未设置且存在默认发件人地址，则使用默认发件人地址。
        - 检查所有必需参数是否已设置。
        - 调用邮件客户端的 send 方法发送邮件。

        异常处理:
        - 如果邮件客户端未初始化，抛出 ValueError。
        - 如果任何必需参数未设置，抛出 ValueError。
        """
        if not self._client:
            raise ValueError("Mail client is not initialized")

        if not from_ and self._default_send_from:
            from_ = self._default_send_from

        if not from_:
            raise ValueError("mail from is not set")

        if not to:
            raise ValueError("mail to is not set")

        if not subject:
            raise ValueError("mail subject is not set")

        if not html:
            raise ValueError("mail html is not set")

        self._client.send(
            {
                "from": from_,
                "to": to,
                "subject": subject,
                "html": html,
            }
        )


def init_app(app: Flask):
    """
    初始化 Flask 应用的邮件配置。

    参数:
    - app: Flask 应用对象。

    逻辑:
    - 调用 Mail 类的 init_app 方法初始化邮件客户端。
    """
    mail.init_app(app)


mail = Mail()

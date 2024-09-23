import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTPClient:
    """
    SMTPClient 类用于通过 SMTP 协议发送电子邮件。
    该类封装了与 SMTP 服务器的连接、认证和邮件发送功能。
    """

    def __init__(
        self, server: str, port: int, username: str, password: str, _from: str, use_tls=False, opportunistic_tls=False
    ):
        """
        初始化 SMTPClient 实例。

        参数:
        server (str): SMTP 服务器地址。
        port (int): SMTP 服务器端口。
        username (str): SMTP 服务器认证用户名。
        password (str): SMTP 服务器认证密码。
        _from (str): 发件人邮箱地址。
        use_tls (bool): 是否使用 TLS 加密连接。默认为 False。
        opportunistic_tls (bool): 是否使用机会性 TLS。仅在 use_tls 为 True 时有效。默认为 False。
        """
        self.server = server
        self.port = port
        self._from = _from
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.opportunistic_tls = opportunistic_tls

    def send(self, mail: dict):
        """
        发送电子邮件。

        参数:
        mail (dict): 包含邮件信息的字典，必须包含以下键：
            - "subject": 邮件主题。
            - "to": 收件人邮箱地址。
            - "html": 邮件正文内容，HTML 格式。

        返回值:
        无返回值。如果发送失败，将抛出异常。
        """
        smtp = None
        try:
            # 根据 use_tls 和 opportunistic_tls 的值选择合适的 SMTP 连接方式
            if self.use_tls:
                if self.opportunistic_tls:
                    smtp = smtplib.SMTP(self.server, self.port, timeout=10)
                    smtp.starttls()
                else:
                    smtp = smtplib.SMTP_SSL(self.server, self.port, timeout=10)
            else:
                smtp = smtplib.SMTP(self.server, self.port, timeout=10)

            # 如果提供了用户名和密码，进行 SMTP 认证
            if self.username and self.password:
                smtp.login(self.username, self.password)

            # 创建邮件消息对象
            msg = MIMEMultipart()
            msg["Subject"] = mail["subject"]
            msg["From"] = self._from
            msg["To"] = mail["to"]
            msg.attach(MIMEText(mail["html"], "html"))

            # 发送邮件
            smtp.sendmail(self._from, mail["to"], msg.as_string())
        except smtplib.SMTPException as e:
            # 捕获并记录 SMTP 错误
            logging.error(f"SMTP error occurred: {str(e)}")
            raise
        except TimeoutError as e:
            # 捕获并记录超时错误
            logging.error(f"Timeout occurred while sending email: {str(e)}")
            raise
        except Exception as e:
            # 捕获并记录其他意外错误
            logging.error(f"Unexpected error occurred while sending email: {str(e)}")
            raise
        finally:
            # 确保 SMTP 连接在最后关闭
            if smtp:
                smtp.quit()

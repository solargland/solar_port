import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from typing import Optional

logger = logging.getLogger("GlobalNewsCrawler")

class EmailNotifier:
    """邮件通知发送器，支持 HTML 正文与 Markdown 纯文本发送"""

    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            # 兼容搜索 report/mail_config.json 与当前目录下的 mail_config.json
            candidate_paths = [
                os.path.join(os.getcwd(), "report", "mail_config.json"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "report", "mail_config.json"),
                os.path.join(os.getcwd(), "mail_config.json"),
            ]
            for p in candidate_paths:
                if os.path.exists(p):
                    config_path = p
                    break

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        # 1. 优先读取环境变量 (适配 GitHub Actions Secrets 与云端安全部署)
        if os.environ.get("SENDER_EMAIL") and os.environ.get("AUTH_CODE"):
            return {
                "smtp_server": os.environ.get("SMTP_SERVER", "smtp.qq.com"),
                "smtp_port": int(os.environ.get("SMTP_PORT", 465)),
                "use_ssl": os.environ.get("USE_SSL", "true").lower() in ("true", "1", "yes"),
                "sender_email": os.environ.get("SENDER_EMAIL"),
                "auth_code": os.environ.get("AUTH_CODE"),
                "receiver_email": os.environ.get("RECEIVER_EMAIL") or os.environ.get("SENDER_EMAIL")
            }

        # 2. 从本地配置文件读取
        if not self.config_path or not os.path.exists(self.config_path):
            logger.warning("未找到邮件配置文件 mail_config.json 或相关环境变量，邮件推送功能暂不可用。")
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取邮件配置失败: {e}")
            return {}

    def send_report(self, subject: str, html_content: str, text_content: str = "") -> bool:
        """发送每日热点新闻报告邮件"""
        if not self.config:
            logger.warning("未配置有效的邮件账户，跳过邮件发送。")
            return False

        smtp_server = self.config.get("smtp_server", "smtp.qq.com")
        smtp_port = self.config.get("smtp_port", 465)
        use_ssl = self.config.get("use_ssl", True)
        sender = self.config.get("sender_email")
        auth_code = self.config.get("auth_code")
        receiver = self.config.get("receiver_email")

        if not sender or not auth_code or not receiver or "授权码" in auth_code:
            logger.warning("邮件配置缺少必要信息或授权码未填写。")
            return False

        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((str(Header("Global Daily News Bot", "utf-8")), sender))
        msg["To"] = formataddr((str(Header("订阅者", "utf-8")), receiver))
        msg["Subject"] = Header(subject, "utf-8")

        if text_content:
            part_text = MIMEText(text_content, "plain", "utf-8")
            msg.attach(part_text)

        if html_content:
            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_html)

        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
                server.starttls()

            server.login(sender, auth_code)
            server.sendmail(sender, [receiver], msg.as_string())
            server.quit()
            logger.info(f"每日热点新闻邮件已成功投递至: {receiver}")
            return True
        except Exception as e:
            logger.error(f"邮件投递异常: {e}")
            return False

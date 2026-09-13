import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

# 确保在 Windows 控制台下输出不会因为编码报错
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CURRENT_DIR, "mail_config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[-] 提示: 未找到邮件配置文件 {CONFIG_FILE}。")
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] 读取配置文件失败: {e}")
        return None

def send_email(subject: str, content: str, is_html: bool = False, receiver: str = None) -> bool:
    config = load_config()
    if not config:
        return False

    smtp_server = config.get("smtp_server", "smtp.qq.com")
    smtp_port = config.get("smtp_port", 465)
    use_ssl = config.get("use_ssl", True)
    sender = config.get("sender_email")
    auth_code = config.get("auth_code")
    to_addr = receiver or config.get("receiver_email")

    if not sender or not auth_code or not to_addr or "授权码" in auth_code:
        print("[-] 错误: 请先在 mail_config.json 中填入有效的 16 位 QQ 邮箱 SMTP 授权码。")
        return False

    msg = MIMEMultipart()
    # RFC 5322 规范：显示名称可进行 UTF-8 编码，但邮件地址必须保持明文标准格式
    msg['From'] = formataddr((str(Header("GitHub Daily Explorer", 'utf-8')), sender))
    msg['To'] = formataddr((str(Header("订阅者", 'utf-8')), to_addr))
    msg['Subject'] = Header(subject, 'utf-8')

    body = MIMEText(content, 'html' if is_html else 'plain', 'utf-8')
    msg.attach(body)

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
            server.starttls()

        server.login(sender, auth_code)
        server.sendmail(sender, [to_addr], msg.as_string())
        server.quit()
        print(f"[+] 邮件提醒已成功发送至: {to_addr}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[-] 认证失败: QQ 邮箱授权码错误，请确保填入的是在 QQ 邮箱网页版设置中生成的 16 位独立授权码，而非邮箱登录密码。")
        return False
    except Exception as e:
        print(f"[-] 邮件发送失败: {e}")
        return False

def send_daily_report(report_path: str = None):
    """自动将最新的报告内容发送至目标邮箱"""
    if not report_path:
        report_files = [f for f in os.listdir(CURRENT_DIR) if f.endswith(".md")]
        if not report_files:
            print("[-] 未找到可发送的报告文件。")
            return False
        report_files.sort(reverse=True)
        report_path = os.path.join(CURRENT_DIR, report_files[0])

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    filename = os.path.basename(report_path)
    subject = f"【GitHub 开源与逆向日报】{filename.replace('.md', '')}"
    return send_email(subject, content, is_html=False)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "send_report":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        send_daily_report(path)
    elif len(sys.argv) > 2:
        sub = sys.argv[1]
        body_text = sys.argv[2]
        send_email(sub, body_text)
    else:
        print("用法说明:")
        print("  1. 测试发送自定义邮件: python mail_notifier.py <邮件主题> <邮件正文>")
        print("  2. 发送今日最新精选报告: python mail_notifier.py send_report")
        cfg = load_config()
        if cfg:
            print(f"\n当前配置目标邮箱: {cfg.get('receiver_email')}")
            if "授权码" in cfg.get("auth_code", ""):
                print("状态: 授权码尚未填写。")
            else:
                print("状态: 授权码已配置。")

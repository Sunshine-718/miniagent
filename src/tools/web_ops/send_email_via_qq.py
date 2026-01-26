import smtplib
from src import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


def send_email_via_qq(to_email: str, subject: str, body: str) -> str:
    """
    通过QQ邮箱的SMTP服务器发送电子邮件。
    参数:
        to_email: 字符串，收件人邮箱地址
        subject: 字符串，邮件主题
        body: 字符串，邮件正文（纯文本）
    返回:
        成功或错误信息字符串
    用法:
        send_email_via_qq(to_email=<收件人>, subject=<主题>, body=<正文>)
    """

    # 从配置中读取邮箱信息
    sender_email = config.QQ_EMAIL
    auth_code = config.QQ_EMAIL_AUTH_CODE

    if not sender_email or not auth_code:
        return "错误：QQ邮箱配置未设置。请编辑 .env 文件并设置 QQ_EMAIL 和 QQ_EMAIL_AUTH_CODE。"

    try:
        # 设置邮件内容
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # QQ邮箱SMTP服务器设置
        smtp_server = 'smtp.qq.com'
        smtp_port = 465  # SSL端口

        # 建立SSL连接
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, auth_code)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        return f'邮件发送成功！从 {sender_email} 发送到 {to_email}，主题：{subject}'
    except Exception as e:
        return f'邮件发送失败：{str(e)}'

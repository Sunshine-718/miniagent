import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
import mimetypes


def send_email_via_qq(to_email: str, subject: str, body: str, attachments=None) -> str:
    """
    通过QQ邮箱的SMTP服务器发送电子邮件，支持附件。
    参数:
        to_email: 字符串，收件人邮箱地址
        subject: 字符串，邮件主题
        body: 字符串，邮件正文（纯文本）
        attachments: 字符串或列表，附件文件路径（可选）。可以是单个文件路径字符串，或多个文件路径的列表。
    返回:
        成功或错误信息字符串
    用法:
        send_email_via_qq(to_email=<收件人>, subject=<主题>, body=<正文>)
        send_email_via_qq(to_email=<收件人>, subject=<主题>, body=<正文>, attachments=<文件路径>)
        send_email_via_qq(to_email=<收件人>, subject=<主题>, body=<正文>, attachments=[<文件1>, <文件2>])
    """

    # 从配置中读取邮箱信息
    sender_email = os.getenv('QQ_EMAIL')
    auth_code = os.getenv('QQ_EMAIL_AUTH_CODE')

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

        # 处理附件
        if attachments:
            # 如果 attachments 是字符串，转换为列表
            if isinstance(attachments, str):
                attachments = [attachments]
            
            for attachment_path in attachments:
                if not os.path.exists(attachment_path):
                    return f"错误：附件文件不存在 - {attachment_path}"
                
                # 获取文件名
                filename = os.path.basename(attachment_path)
                
                # 读取文件内容
                with open(attachment_path, 'rb') as f:
                    file_content = f.read()
                
                # 猜测文件类型
                mime_type, _ = mimetypes.guess_type(attachment_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                # 创建附件
                main_type, sub_type = mime_type.split('/', 1)
                attachment = MIMEApplication(file_content, _subtype=sub_type)
                
                # 设置附件头信息
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                attachment.add_header('Content-Type', mime_type)
                
                msg.attach(attachment)

        # QQ邮箱SMTP服务器设置
        smtp_server = 'smtp.qq.com'
        smtp_port = 465  # SSL端口

        # 建立SSL连接
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, auth_code)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        # 构建成功消息
        success_msg = f'邮件发送成功！从 {sender_email} 发送到 {to_email}，主题：{subject}'
        if attachments:
            attachment_names = [os.path.basename(path) for path in (attachments if isinstance(attachments, list) else [attachments])]
            success_msg += f'，附件：{", ".join(attachment_names)}'
        
        return success_msg
    except Exception as e:
        return f'邮件发送失败：{str(e)}'

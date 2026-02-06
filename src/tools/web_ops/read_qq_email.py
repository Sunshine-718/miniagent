

import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime


def read_qq_email(count: int = 1) -> str:
    '''QQ 邮箱收件箱读取工具（IMAP + imaplib/email 专用版）

    使用 Python 原生 imaplib + email 库安全连接 QQ 邮箱，获取最新邮件摘要。
    注意：
    - 本工具不存储、不记录任何凭证；
    - 建议首次运行时仅 fetch 1 封邮件测试连接。

    参数:
        count (int, optional): 获取邮件数量，默认为 1（最新一封）

    返回:
        str: 成功时返回邮件摘要（主题、发件人、时间、正文前100字）；失败时返回错误信息。
    '''
    # 强制从 .env 加载（专用于你的邮箱）
    email_user = os.getenv('QQ_EMAIL')
    email_pass = os.getenv('QQ_EMAIL_AUTH_CODE')
    
    # 校验必要参数
    if not email_user or not email_pass:
        return "[ERROR] 缺少必要凭证：请确保 workspace/.env 中已正确配置 QQ_EMAIL 和 QQ_EMAIL_AUTH_CODE。"
    
    try:
        # 1. 连接到 IMAP 服务器
        mail = imaplib.IMAP4_SSL('imap.qq.com')
        mail.login(email_user, email_pass)
        
        # 2. 选择收件箱
        mail.select('INBOX')
        
        # 3. 搜索邮件（获取所有邮件 ID）
        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()
        
        if not mail_ids:
            return "收件箱为空。"
        
        # 取最新 count 封
        mail_ids = mail_ids[-count:]
        
        # 4. 拉取并解析邮件
        summary = [f"已获取最新 {len(mail_ids)} 封邮件："]
        for i, mail_id in enumerate(mail_ids, 1):
            res, msg_data = mail.fetch(mail_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 解码主题
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    subject = str(subject)[:50]
                    
                    # 解码发件人
                    from_, encoding = decode_header(msg.get('From'))[0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding if encoding else 'utf-8')
                    from_ = str(from_)[:40]
                    
                    # 获取时间
                    date = msg.get('Date', '(无日期)')
                    date_str = str(date)[:16]
                    
                    # 获取正文
                    body = "(正文为空)"
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8')
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode('utf-8')
                        except:
                            pass
                    preview = str(body)[:100].replace('\n', ' ').replace('\r', ' ').strip()
                    if not preview:
                        preview = '(正文为空)'
                    
                    summary.append(f"{i}. 【{subject}】\n   发件人：{from_}\n   时间：{date_str}\n   预览：{preview}...")
                    break  # 只处理第一段数据
        
        mail.logout()
        return '\n\n'.join(summary)
    
    except Exception as e:
        err_msg = str(e).lower()
        if 'login' in err_msg or 'auth' in err_msg or 'password' in err_msg:
            return "[ERROR] 登录失败：请检查 .env 中的 QQ_EMAIL 和 QQ_EMAIL_AUTH_CODE 是否正确，并确认已开启 IMAP 服务。"
        else:
            return f"[ERROR] 未知错误：{str(e)}"

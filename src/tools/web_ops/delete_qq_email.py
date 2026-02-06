import imaplib
import os
import sys

def delete_emails_by_keyword(keyword: str, search_field: str = 'SUBJECT') -> dict:
    """
    根据关键词删除 QQ 邮箱中的邮件（已修复中文编码问题）。
    
    Args:
        keyword (str): 搜索关键词（支持中文）。
        search_field (str): 'SUBJECT' (标题) 或 'FROM' (发件人)。

    Returns:
        dict: 包含 status, deleted_count, message 的字典。
    """
    
    # 1. 基础参数校验
    if not keyword:
        return {"status": "error", "deleted_count": 0, "message": "关键词不能为空"}
    
    valid_fields = ['SUBJECT', 'FROM']
    search_field = search_field.upper()
    if search_field not in valid_fields:
        return {"status": "error", "deleted_count": 0, "message": f"不支持的搜索字段: {search_field}"}

    # 2. 从环境变量获取凭证
    email_user = os.getenv('QQ_EMAIL')
    email_pass = os.getenv('QQ_EMAIL_AUTH_CODE')

    if not email_user or not email_pass:
        return {
            "status": "error", 
            "deleted_count": 0, 
            "message": "环境变量 'QQ_EMAIL' 或 'QQ_EMAIL_AUTH_CODE' 未设置，请检查配置。"
        }

    imap_server = 'imap.qq.com'
    mail = None

    try:
        # 3. 连接 IMAP 服务器
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select('INBOX')

        # 4. 构建搜索指令 (核心修复部分)
        # IMAP 协议要求格式: (SUBJECT "内容")
        criteria_str = f'({search_field} "{keyword}")'
        
        # 【关键修正】: 将字符串手动编码为 utf-8 bytes，防止 Python 使用默认的 ascii 编码导致报错
        status, messages = mail.search("UTF-8", criteria_str.encode('utf-8'))

        if status != 'OK':
            return {"status": "error", "deleted_count": 0, "message": "搜索指令被服务器拒绝"}

        # 解析邮件 ID 列表
        mail_ids = messages[0].split()
        count = len(mail_ids)

        if count == 0:
            return {
                "status": "success", 
                "deleted_count": 0, 
                "message": f"未找到 {search_field} 包含 '{keyword}' 的邮件。"
            }

        # 5. 遍历并标记删除
        print(f"-> 正在标记 {count} 封邮件为删除状态...")
        for mail_id in mail_ids:
            mail.store(mail_id, '+FLAGS', '\\Deleted')
        
        # 6. 彻底移除 (Expunge)
        mail.expunge()
        
        return {
            "status": "success", 
            "deleted_count": count, 
            "message": f"成功删除 {count} 封相关邮件。"
        }

    except imaplib.IMAP4.error as e:
        return {
            "status": "error", 
            "deleted_count": 0, 
            "message": f"IMAP 协议错误 (可能是授权码失效): {e}"
        }
    except Exception as e:
        return {
            "status": "error", 
            "deleted_count": 0, 
            "message": f"未知系统错误: {str(e)}"
        }
    finally:
        # 7. 资源清理
        if mail:
            try:
                mail.logout()
            except:
                pass
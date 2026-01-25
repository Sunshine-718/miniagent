import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

# Jina AI API 配置
JINA_API_TOKEN = os.getenv('JINA_API_TOKEN')

# QQ邮箱SMTP配置
QQ_EMAIL = os.getenv('QQ_EMAIL')
QQ_EMAIL_AUTH_CODE = os.getenv('QQ_EMAIL_AUTH_CODE')

# 配置验证函数
def validate_config():
    """验证必要的配置是否已设置"""
    missing_configs = []
    
    if not DEEPSEEK_API_KEY:
        missing_configs.append('DEEPSEEK_API_KEY')
    
    if not JINA_API_TOKEN:
        missing_configs.append('JINA_API_TOKEN')
    
    if not QQ_EMAIL:
        missing_configs.append('QQ_EMAIL')
    
    if not QQ_EMAIL_AUTH_CODE:
        missing_configs.append('QQ_EMAIL_AUTH_CODE')
    
    if missing_configs:
        print(f"警告: 以下配置未设置: {', '.join(missing_configs)}")
        print(f"请编辑 .env 文件并设置这些配置项")
        return False
    
    print("所有配置已正确设置")
    return True


if __name__ == "__main__":
    # 当直接运行此脚本时，验证配置
    print("=== 配置验证 ===")
    print(f"DEEPSEEK_API_KEY: {'已设置' if DEEPSEEK_API_KEY else '未设置'}")
    print(f"DEEPSEEK_BASE_URL: {DEEPSEEK_BASE_URL}")
    print(f"JINA_API_TOKEN: {'已设置' if JINA_API_TOKEN else '未设置'}")
    print(f"QQ_EMAIL: {'已设置' if QQ_EMAIL else '未设置'}")
    print(f"QQ_EMAIL_AUTH_CODE: {'已设置' if QQ_EMAIL_AUTH_CODE else '未设置'}")
    print()
    validate_config()
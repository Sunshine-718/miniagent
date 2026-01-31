import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv(override=True)

@dataclass
class Config:
    API_KEY: str = os.getenv('DEEPSEEK_API_KEY')
    JINA_TOKEN: str = os.getenv('JINA_API_TOKEN')
    QQ_EMAIL: str = os.getenv('QQ_EMAIL')
    QQ_AUTH: str = os.getenv('QQ_EMAIL_AUTH_CODE')

    TOKEN_LIMIT: int = 1000000
    RETAIN_RECENT: int = 50
    
settings = Config()
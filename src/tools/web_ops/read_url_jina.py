import requests
import os

def read_url_jina(url: str) -> str:
    """
    使用 r.jina.ai 读取URL并获取其内容（优先使用scrape_web_page）
    参数:
        url: 字符串，网址
    返回:
        网页信息或错误信息
    用法:
        read_url_jina(url=<网址>)

    """
    url = f"https://r.jina.ai/{url}"
    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_API_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    return response.text

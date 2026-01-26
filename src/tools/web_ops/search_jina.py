import requests
from src import config


def search_jina(keyword):
    """
    使用 s.jina.ai 搜索网络并获取SERP（优先使用scrape_web_page）
    参数:
        keyword: 字符串关键字
    返回:
        状态码，内容
    用法:
        search_jina(url=<网址>)
    """
    url = f"https://s.jina.ai/?q={keyword}"
    headers = {
        "Authorization": f"Bearer {config.JINA_API_TOKEN}",
        "X-Respond-With": "no-content"
    }
    response = requests.get(url, headers=headers)
    return response.status_code, response.content

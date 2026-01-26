import requests
import html2text
from bs4 import BeautifulSoup

def scrape_web_page(url: str) -> str:
    """
    爬取网页并将其转换为精简的 Markdown 格式，节省 Token。（优先选择这个因为jina的API有限额）
    参数:
        url: 字符串，网址
    返回:
        网页内容或报错信息
    用法:
        scrape_web_page(url=<网址>)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 1. 使用 BeautifulSoup 初步清洗
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除完全无用的标签
        for script in soup(["script", "style", "header", "footer", "nav", "svg", "noscript"]):
            script.extract()

        # 2. 使用 html2text 转换为 Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False  # 保留链接，有时候 Agent 需要继续点击
        h.ignore_images = True  # 忽略图片，节省大量干扰
        h.body_width = 0       # 不自动换行

        markdown_content = h.handle(str(soup))

        # 3. 再次去重空行（压缩 Token）
        lines = [line.strip() for line in markdown_content.splitlines() if line.strip()]
        clean_content = '\n'.join(lines)

        # 4. 长度熔断（防止仍然过长）
        max_len = 5000
        if len(clean_content) > max_len:
            return clean_content[:max_len] + f"\n\n...(网页过长，已截断。剩余 {len(clean_content) - max_len} 字符)"

        return clean_content

    except Exception as e:
        return f"Error scraping {url}: {str(e)}"
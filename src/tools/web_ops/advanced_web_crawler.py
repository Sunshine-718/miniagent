import requests
import json
import csv
from typing import Dict, List, Any, Optional, Union
from bs4 import BeautifulSoup
import time
import re
import html2text

class AdvancedWebCrawler:
    """
    高级网页爬虫工具，支持多种解析方式和数据提取功能
    """
    
    def __init__(self, timeout: int = 10, retry_times: int = 3, delay: float = 1.0):
        """
        初始化爬虫
        
        Args:
            timeout: 请求超时时间（秒）
            retry_times: 重试次数
            delay: 请求延迟（秒），避免被封
        """
        self.timeout = timeout
        self.retry_times = retry_times
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        })
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """设置自定义请求头"""
        self.session.headers.update(headers)
    
    def set_proxy(self, proxy: Dict[str, str]) -> None:
        """设置代理"""
        self.session.proxies.update(proxy)
    
    def fetch_page(self, url: str, method: str = 'GET', data: Optional[Dict] = None, 
                   params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            method: HTTP方法（GET/POST）
            data: POST数据
            params: URL参数
            
        Returns:
            Response对象或None
        """
        for attempt in range(self.retry_times):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, data=data, params=params, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                time.sleep(self.delay)  # 礼貌延迟
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    return None
        
        return None
    
    def parse_html(self, html_content: str, parser: str = 'html.parser') -> BeautifulSoup:
        """解析HTML内容为BeautifulSoup对象"""
        return BeautifulSoup(html_content, parser)
    
    def extract_by_css(self, soup: BeautifulSoup, selector: str, 
                       attr: Optional[str] = None, multiple: bool = True) -> Union[List[str], str, None]:
        """
        使用CSS选择器提取元素
        
        Args:
            soup: BeautifulSoup对象
            selector: CSS选择器
            attr: 要提取的属性（如'href', 'src', 'text'等），None表示提取文本
            multiple: 是否提取多个元素
            
        Returns:
            提取的结果
        """
        try:
            elements = soup.select(selector)
            
            if not elements:
                return None if not multiple else []
            
            if multiple:
                if attr:
                    return [element.get(attr, '') for element in elements if element.get(attr)]
                else:
                    return [element.get_text(strip=True) for element in elements]
            else:
                element = elements[0]
                if attr:
                    return element.get(attr, '')
                else:
                    return element.get_text(strip=True)
                
        except Exception as e:
            print(f"Error extracting by CSS selector '{selector}': {e}")
            return None if not multiple else []
    
    def extract_json(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """尝试从响应中提取JSON数据"""
        try:
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type:
                return response.json()
            
            # 尝试从HTML中提取JSON-LD
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script', type='application/ld+json')
            if script_tags:
                for script in script_tags:
                    try:
                        return json.loads(script.string)
                    except:
                        continue
            
            # 尝试从JavaScript变量中提取JSON
            json_patterns = [
                r'JSON\.parse\(\s*["\'](.+?)["\']\s*\)',
                r'=\s*({.+?})\s*;',
                r'var\s+\w+\s*=\s*({.+?})\s*;'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response.text, re.DOTALL)
                for match in matches:
                    try:
                        # 清理JSON字符串
                        json_str = match.replace('\\"', '"').replace("\\'", "'")
                        return json.loads(json_str)
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"Error extracting JSON: {e}")
            return None
    
    def save_to_json(self, data: Any, filename: str) -> bool:
        """保存数据为JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """保存数据为CSV文件"""
        try:
            if not data:
                return False
            
            # 获取所有字段名
            fieldnames = set()
            for item in data:
                if isinstance(item, dict):
                    fieldnames.update(item.keys())
            
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                writer.writeheader()
                
                for item in data:
                    if isinstance(item, dict):
                        writer.writerow(item)
            
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False

def advanced_web_crawler(
    url: str,
    action: str = 'fetch',
    selector: Optional[str] = None,
    attr: Optional[str] = None,
    output_format: str = 'text',
    output_file: Optional[str] = None,
    custom_headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
    retry_times: int = 3,
    delay: float = 1.0,
    raw_html: bool = False
) -> str:
    """
    高级网页爬虫工具
    
    参数:
        url: 目标URL
        action: 操作类型，可选值：
              'fetch' - 获取网页内容
              'extract' - 提取特定元素
              'extract_json' - 提取JSON数据
        selector: CSS选择器（当action为'extract'时使用）
        attr: 要提取的属性（如'href', 'src', 'text'等）
        output_format: 输出格式，可选'text', 'json', 'csv'
        output_file: 输出文件路径（如果提供则保存到文件）
        custom_headers: 自定义请求头
        timeout: 请求超时时间（秒），默认10秒
        retry_times: 重试次数，默认3次
        delay: 请求延迟（秒），避免被封，默认1秒
        raw_html: 是否返回原始HTML（默认False，返回精简Markdown）
        
    返回:
        爬取结果或状态信息
    
    示例:
        >>> advanced_web_crawler("https://example.com", "fetch")  # 默认返回精简Markdown
        >>> advanced_web_crawler("https://example.com", "fetch", raw_html=True)  # 返回原始HTML
        >>> advanced_web_crawler("https://example.com", "extract", selector="h1", attr="text")
        >>> advanced_web_crawler("https://api.example.com/data.json", "extract_json")
    """
    try:
        crawler = AdvancedWebCrawler(timeout=timeout, retry_times=retry_times, delay=delay)
        
        # 设置自定义请求头
        if custom_headers:
            crawler.set_headers(custom_headers)
        
        if action == 'fetch':
            response = crawler.fetch_page(url)
            if not response:
                return f"Failed to fetch URL: {url}"
            
            # 尝试提取JSON
            json_data = crawler.extract_json(response)
            if json_data and output_format == 'json':
                result = json.dumps(json_data, ensure_ascii=False, indent=2)
            else:
                if raw_html:
                    # 返回原始HTML内容（有长度限制）
                    result = response.text[:5000] + "..." if len(response.text) > 5000 else response.text
                else:
                    # 转换为精简Markdown格式，节省Token
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 移除完全无用的标签
                    for script in soup(["script", "style", "header", "footer", "nav", "svg", "noscript"]):
                        script.extract()
                    
                    # 使用 html2text 转换为 Markdown
                    h = html2text.HTML2Text()
                    h.ignore_links = False  # 保留链接，有时候 Agent 需要继续点击
                    h.ignore_images = True  # 忽略图片，节省大量干扰
                    h.body_width = 0       # 不自动换行

                    markdown_content = h.handle(str(soup))

                    # 再次去重空行（压缩 Token）
                    lines = [line.strip() for line in markdown_content.splitlines() if line.strip()]
                    clean_content = '\n'.join(lines)

                    # 长度熔断（防止仍然过长）
                    max_len = 5000
                    if len(clean_content) > max_len:
                        result = clean_content[:max_len] + f"\n\n...(网页过长，已截断。剩余 {len(clean_content) - max_len} 字符)"
                    else:
                        result = clean_content
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                return f"Content saved to {output_file}"
            
            return result
            
        elif action == 'extract':
            response = crawler.fetch_page(url)
            if not response:
                return f"Failed to fetch URL: {url}"
            
            soup = crawler.parse_html(response.text)
            
            if not selector:
                return "Error: selector must be provided for extraction"
            
            results = crawler.extract_by_css(soup, selector, attr, multiple=True)
            
            if not results:
                return "No elements found with the given selector"
            
            # 格式化输出
            if output_format == 'json':
                result = json.dumps(results, ensure_ascii=False, indent=2)
            elif output_format == 'csv':
                # 将结果转换为字典列表
                data = [{'index': i, 'value': value} for i, value in enumerate(results)]
                if output_file:
                    crawler.save_to_csv(data, output_file)
                    return f"Data saved to {output_file}"
                result = "\n".join([f"{i+1}. {value}" for i, value in enumerate(results)])
            else:
                result = "\n".join([f"{i+1}. {value}" for i, value in enumerate(results)])
            
            if output_file and output_format != 'csv':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                return f"Data saved to {output_file}"
            
            return result
            
        elif action == 'extract_json':
            response = crawler.fetch_page(url)
            if not response:
                return f"Failed to fetch URL: {url}"
            
            json_data = crawler.extract_json(response)
            if not json_data:
                return "No JSON data found in the response"
            
            result = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                return f"JSON data saved to {output_file}"
            
            return result
            
        else:
            return f"Unknown action: {action}. Supported actions: fetch, extract, extract_json"
            
    except Exception as e:
        return f"Error in advanced_web_crawler: {str(e)}"
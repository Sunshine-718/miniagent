import os
import subprocess
import math
import datetime
import requests
import json
import html2text
from bs4 import BeautifulSoup
import contextlib
import sys
import io
import inspect
import difflib
import config  # 导入配置模块


def check_file_diff(file_path: str, new_content: str):
    """
    检查如果将 new_content 写入 file_path，会产生什么差异。
    用于在实际覆盖文件前进行预览和检查。
    
    参数:
        file_path: 现有文件路径
        new_content: 准备写入的新内容
    返回:
        Diff 差异字符串
    """
    if not os.path.exists(file_path):
        return f"New File: {file_path} (Entire content is new)"
    
    # 读取旧内容
    with open(file_path, 'r', encoding='utf-8') as f:
        old_content = f.read()
        
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f'{file_path} (Current)',
        tofile=f'{file_path} (New)',
        lineterm=''
    )
    
    diff_text = ''.join(diff)
    if not diff_text:
        return "No changes detected."
    return diff_text


def get_source_code(name: str):
    """
    传入函数名字符串可以获得tools.py的函数的源代码，方便快速查看，节省token数量
    参数:
        name: 字符串，函数名
    返回:
        函数实现的源代码或报错信息
    用法:
        get_source_code(name=<工具函数名>)
    """
    current_module = sys.modules[__name__]
    all_functions = inspect.getmembers(current_module, inspect.isfunction)
    for n, func in all_functions:
        try:
            if name == n and func.__module__ == __name__:
                return inspect.getsource(func)
        except Exception as e:
            return f'Error: {e}'
    else:
        return f'Error: 没有找到函数 "{name}"'


def python_repl(code: str):
    """
    调用Python解释器运行Python代码，并且返回结果到标准输出
    变量在多次调用之间持续保持
    参数:
        code: 字符串，代码
    返回:
        代码运行结果或报错信息
    用法:
        python_repl(code=<你的代码>)
    """
    io_buffer = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(io_buffer), contextlib.redirect_stderr(io_buffer):
            exec(code, globals())
        output = io_buffer.getvalue()
        if not output.strip():
            return "Execution successful, but no output produced. (Hint: Use print() to see results)"
        return output
    except Exception as e:
        return f"Runtime Error: {e}"


def edit_file_by_replace(file_path: str, old_text: str, new_text: str):
    """
    通过查找并替换特定的文本块来修改文件（精准修改，节省Token）。
    
    参数:
        file_path: 文件路径
        old_text: 原文中需要被替换的**准确**代码块或文本（必须与文件内容完全一致，包括空格和缩进）。
        new_text: 想要替换成的新内容。
    
    返回:
        操作结果信息。
    """
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在。"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. 检查 old_text 是否存在
        if old_text not in content:
            # 尝试做一个简单的容错：去除两端空白再试（可选）
            if old_text.strip() in content:
                 return "错误：找到相似内容，但空白字符（空格/缩进）不匹配。请精确复制原文。"
            return "错误：在文件中未找到指定的 old_text。请确保通过 read_file 确认了最新的文件内容，并精确复制要修改的代码块。"

        # 2. 检查唯一性 (防止误伤)
        if content.count(old_text) > 1:
            return f"错误：指定的 old_text 在文件中出现了 {content.count(old_text)} 次，系统无法确定替换哪一处。请提供更长的 old_text 以确保唯一性。"

        # 3. 执行替换
        new_content = content.replace(old_text, new_text, 1) # 只替换一次

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return "修改成功！"

    except Exception as e:
        return f"系统错误：{str(e)}"


def edit_file_by_line(file_path: str, line_number: int, new_line_content: str = None, mode: str = "replace"):
    """
    基于行号修改文件。
    
    参数:
        file_path: 文件路径
        line_number: 目标行号（从 1 开始）。
        new_line_content: 新的一行内容（如果 mode 为 'delete' 则忽略此参数）。
        mode: 操作模式 - 'replace' (替换该行), 'insert' (在该行前插入), 'delete' (删除该行)。
    """
    if not os.path.exists(file_path):
        return f"错误：文件不存在。"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 转换为索引 (0-based)
        idx = line_number - 1
        
        if idx < 0 or idx >= len(lines) + (1 if mode == 'insert' else 0):
             return f"错误：行号 {line_number} 超出范围 (当前文件共 {len(lines)} 行)。"

        # 处理换行符：确保输入的内容末尾有换行
        if new_line_content and not new_line_content.endswith('\n'):
            new_line_content += '\n'

        if mode == 'replace':
            lines[idx] = new_line_content
        elif mode == 'insert':
            lines.insert(idx, new_line_content)
        elif mode == 'delete':
            del lines[idx]
        else:
            return "错误：未知模式，仅支持 replace, insert, delete。"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        return f"操作成功：Line {line_number} 已执行 {mode}。"

    except Exception as e:
        return f"错误：{str(e)}"


def list_dir(path: str):
    """
    获取给定路径下的文件名
    参数:
        path: 字符串，路径
    返回:
        给定路径下的文件名
    用法:
        list_dir(path=<路径>)
    """
    return ', '.join(os.listdir(path))


def make_dir(dir_name: str):
    """
    调用 os.makedirs 创建目录
    参数:
        dir_name: 字符串，目录名
    返回:
        无
    用法:
        make_dir(dir_name=<目录名>)
    """
    os.makedirs(dir_name, exist_ok=True)
    return f'文件夹：{dir_name} 已创建成功'


def create_file(file_name: str, content: str) -> None:
    """
    创建文件
    参数:
        file_name: 字符串，文件名
        content: 字符串，文件内容
    返回:
        无
    用法:
        create_file(file_name=<文件名>, content=<文件内容>)
    """
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)
    return f'文件：{file_name} 已创建成功'


def read_file(file_name: str) -> str:
    """
    读取文件内容
    参数:
        file_name: 字符串，文件名
    返回:
        文件内容
    用法:
        read_file(file_name=<文件名>)
    """
    with open(file_name, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
    return ''.join(lines)


def delete_dir(dir_name: str):
    """
    删除目录
    参数:
        dir_name: 字符串，目录名
    返回:
        无
    用法:
        delete_dir(dir=<目录名>)
    """
    # input(f'尝试删除路径：{dir_name}, 输入Enter以确认')
    os.removedirs(dir_name)
    return f'文件夹：{dir_name} 已成功删除'


def delete_file(file_name: str):
    """
    删除文件
    参数:
        file_name: 字符串，文件名
    返回:
        无
    用法:
        delete_file(file_name=<文件名>)
    """
    # input(f'尝试删除文件：{file_name}, 输入Enter以确认')
    os.remove(file_name)
    return f'文件：{file_name} 已成功删除'


def run_terminal_command(command: str):
    """
    在终端中运行命令 (支持实时输出反馈)
    参数:
        command: 字符串，命令
    返回:
        命令的所有输出内容
    用法:
        run_terminal_command(command=<命令>)
    """
    try:
        print(f"Executing: {command}")  # 提示当前执行的命令

        # 使用 Popen 实现流式输出
        # stderr=subprocess.STDOUT 表示将错误输出合并到标准输出中
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',  # 显式指定编码，防止中文乱码
            errors='replace'   # 遇到无法解码的字符时不报错，用占位符替代
        )

        output_lines = []

        # 实时逐行读取输出
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            if line:
                # 1. 实时打印给人类看 (去除末尾换行符以免双重换行)
                print(line.strip())
                # 2. 收集起来给 Agent 看
                output_lines.append(line)

        # 等待进程完全结束
        process.wait()

        full_output = "".join(output_lines).strip()

        if process.returncode == 0:
            if not full_output:
                return "命令执行成功（无输出）。"
            return full_output
        else:
            # 即使失败了，Agent 也能看到之前的报错详情
            return f"错误（退出码 {process.returncode}）：\n{full_output}"

    except Exception as e:
        return f"系统错误：{str(e)}"


def list_files(path: str = '.') -> list:
    """
    列出指定目录中的文件
    参数:
        path: 字符串，目录路径（默认为当前目录 '.'）
    返回:
        文件和目录列表
    用法:
        list_files(path=<目录路径>)
    """
    return os.listdir(path)


def append_to_file(file_name: str, content: str, line_number: int = None):
    """
    在文件的特定行或末尾追加内容。
    参数:
        file_name: 字符串，文件名
        content: 字符串，要追加的内容
        line_number: 整数，可选的行号（从1开始）。如果为None或未提供，则追加到末尾。
    返回:
        无
    用法:
        append_to_file(file_name=<文件名>, content=<内容>, line_number=<行号>)
    """
    # 如果文件不存在，创建它
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            pass  # 创建空文件

    if line_number is None:
        # 追加到文件末尾
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(content)
    else:
        # 插入到特定行（从1开始）
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 转换为0索引
        idx = line_number - 1
        # 如果行号超出末尾，则追加到末尾
        if idx > len(lines):
            lines.append(content)
        else:
            # 确保索引非负
            idx = max(0, idx)
            lines.insert(idx, content)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    return f'函数运行成功'


def get_current_time() -> str:
    """
    获取当前日期和时间
    参数:
        无
    返回:
        当前日期和时间字符串
    用法:
        get_current_time()
    """
    return str(datetime.datetime.now())


def calculator(expression: str):
    """
    计算数学表达式，支持基本科学计算功能。
    支持：+, -, *, /, **, sqrt, sin, cos, tan, log, log10, exp, pi, e 等。
    参数:
        expression: 字符串，要计算的数学表达式
    返回:
        结果（浮点数）或错误字符串
    用法:
        calculator(expression=<数学表达式>)
    """
    # 为 eval 定义安全环境
    safe_dict = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pi': math.pi,
        'e': math.e,
        'radians': math.radians,
        'degrees': math.degrees,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': math.factorial,
        'pow': math.pow,
    }

    # 添加基本算术运算
    safe_dict.update({
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        '**': lambda x, y: x ** y,
    })

    try:
        # 仅使用 safe_dict 进行 eval
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return str(result)
    except Exception as e:
        return f"错误：{str(e)}"


def get_weather_with_temp(location: str = "") -> str:
    """
    获取指定位置的天气预报，包含气温信息。
    参数:
        location: 字符串，位置（例如 "Guangzhou" 或 "" 表示自动定位）
    返回:
        天气预报字符串，包含气温和降雨概率。
    用法:
        get_weather_with_temp(location=<位置>)
    """
    try:
        base_url = "https://wttr.in/"
        if location:
            url = f"{base_url}{location}?format=j1"
        else:
            url = f"{base_url}?format=j1"

        response = requests.get(url, headers={"User-Agent": "curl"})
        response.raise_for_status()
        data = response.json()

        tomorrow_forecast = data["weather"][1]
        date = tomorrow_forecast["date"]
        hourly_forecast = tomorrow_forecast["hourly"][0]
        weather_desc = hourly_forecast["weatherDesc"][0]["value"]
        chanceofrain = hourly_forecast["chanceofrain"]
        tempC = hourly_forecast["tempC"]
        tempF = hourly_forecast["tempF"]

        result = f"明天（{date}）的天气预报：\n"
        result += f"天气状况：{weather_desc}\n"
        result += f"气温：{tempC}°C ({tempF}°F)\n"
        result += f"降雨概率：{chanceofrain}%\n"
        if int(chanceofrain) > 50:
            result += "明天很可能会下雨，建议带伞。"
        else:
            result += "明天不太可能下雨，但天气多变，请关注最新预报。"
        return result
    except Exception as e:
        return f"获取天气信息时出错：{str(e)}"


def get_os_info() -> str:
    """
    获取当前操作系统的信息。
    参数:
        无
    返回:
        操作系统信息字符串
    用法:
        get_os_info()
    """
    import platform
    os_name = platform.system()  # e.g., 'Windows', 'Linux', 'Darwin'
    os_version = platform.version()
    os_arch = platform.machine()
    os_release = platform.release()

    info = f"操作系统: {os_name}\n"
    info += f"版本: {os_version}\n"
    info += f"发行版: {os_release}\n"
    info += f"架构: {os_arch}"
    return info


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
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.utils import formatdate
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
        "Authorization": f"Bearer {config.JINA_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    return response.text


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


def check_deepseek_balance():
    """
    查询deepseek API账户余额
    参数:
        无
    返回:
        账户余额
    用法:
        check_deepseek_balance()
    """
    url = "https://api.deepseek.com/user/balance"
    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {config.DEEPSEEK_API_KEY}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def upload_to_github(commit_message: str = "Update code files") -> str:
    """
    使用 run_terminal_command 执行三行 Git 命令上传到 GitHub。
    参数:
        commit_message: 字符串，提交信息
    返回:
        操作结果字符串
    用法:
        upload_to_github(commit_message=<提交信息>)
    """
    results = []

    # 1. 添加所有更改
    result1 = run_terminal_command("git add .")
    results.append(f"添加文件结果: {result1}")

    # 2. 提交更改
    result2 = run_terminal_command(f'git commit -m "{commit_message}"')
    results.append(f"提交结果: {result2}")

    # 3. 推送到远程仓库
    result3 = run_terminal_command("git push")
    results.append(f"推送结果: {result3}")

    return "\n".join(results)


def regex_search_in_file(file_path: str, pattern: str, flags: int = 0) -> str:
    """
    使用正则表达式在文件中搜索匹配的内容。
    
    参数:
        file_path: 字符串，文件路径
        pattern: 字符串，正则表达式模式
        flags: 整数，可选的正则表达式标志（如 re.IGNORECASE, re.MULTILINE 等）
    返回:
        匹配结果字符串（每行一个匹配）或错误信息
    用法:
        regex_search_in_file(file_path=<文件路径>, pattern=<正则表达式>, flags=<标志>)
    """
    import re
    
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在。"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(pattern, content, flags)
        
        if not matches:
            return "未找到匹配项。"
        
        result_lines = []
        for i, match in enumerate(matches, 1):
            if isinstance(match, tuple):
                # 如果有多个捕获组，显示所有组
                match_str = ', '.join(str(g) for g in match if g is not None)
                result_lines.append(f"匹配 {i}: [{match_str}]")
            else:
                result_lines.append(f"匹配 {i}: {match}")
        
        # 添加统计信息
        result_lines.append(f"\n总计找到 {len(matches)} 个匹配项。")
        return '\n'.join(result_lines)
        
    except re.error as e:
        return f"正则表达式错误：{str(e)}"
    except Exception as e:
        return f"读取文件时出错：{str(e)}"


def count_file_lines(file_path: str) -> str:
    """
    统计文件的行数信息。
    
    参数:
        file_path: 字符串，文件路径
    
    返回:
        包含总行数、非空行数和空行数的统计信息字符串
    
    用法:
        count_file_lines(file_path=<文件路径>)
    """
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在。"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        non_empty_lines = 0
        empty_lines = 0
        
        for line in lines:
            if line.strip() == '':
                empty_lines += 1
            else:
                non_empty_lines += 1
        
        # 计算百分比
        if total_lines > 0:
            non_empty_percent = (non_empty_lines / total_lines) * 100
            empty_percent = (empty_lines / total_lines) * 100
        else:
            non_empty_percent = 0.0
            empty_percent = 0.0
        
        result = f"文件: {file_path}\n"
        result += f"总行数: {total_lines}\n"
        result += f"非空行数: {non_empty_lines} ({non_empty_percent:.1f}%)\n"
        result += f"空行数: {empty_lines} ({empty_percent:.1f}%)\n"
        
        # 添加一些分析建议
        if empty_percent > 30:
            result += "提示：文件中有较多空行，建议适当清理以提升可读性。"
        elif non_empty_percent == 100:
            result += "提示：文件中没有空行，代码紧凑。"
        else:
            result += "提示：空行比例适中，代码结构良好。"
        
        return result
        
    except Exception as e:
        return f"读取文件时出错：{str(e)}"
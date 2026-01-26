import os
import re

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
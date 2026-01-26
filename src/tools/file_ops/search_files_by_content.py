import os
import re

def search_files_by_content(directory: str, search_text: str, recursive: bool = True, case_sensitive: bool = False):
    """
    在目录中搜索包含特定文本的文件
    
    参数:
        directory: 要搜索的目录路径
        search_text: 要搜索的文本内容
        recursive: 是否递归搜索子目录，默认为True
        case_sensitive: 是否区分大小写，默认为False
        
    返回:
        包含匹配文件的路径列表
    """
    
    if not os.path.exists(directory):
        return f"错误：目录 {directory} 不存在"
    
    if not os.path.isdir(directory):
        return f"错误：{directory} 不是目录"
    
    matched_files = []
    
    # 设置搜索标志
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(search_text, flags)
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if pattern.search(content):
                    matched_files.append(file_path)
            except (UnicodeDecodeError, PermissionError, OSError):
                # 跳过二进制文件或无权限文件
                continue
        
        # 如果不递归，只处理当前目录
        if not recursive:
            break
    
    if not matched_files:
        return f"在 {directory} 中未找到包含 '{search_text}' 的文件"
    
    return f"找到 {len(matched_files)} 个匹配文件:\n" + "\n".join(matched_files)
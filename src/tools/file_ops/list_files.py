import os

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
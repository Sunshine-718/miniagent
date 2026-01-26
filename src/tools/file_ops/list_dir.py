import os


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

import os

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
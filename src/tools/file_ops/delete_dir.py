import os


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

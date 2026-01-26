import os


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

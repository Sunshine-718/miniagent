import os

def rename_file(old_name: str, new_name: str):
    """
    重命名文件
    参数:
        old_name: 字符串，原文件名
        new_name: 字符串，新文件名
    返回:
        成功或错误信息字符串
    用法:
        rename_file(old_name=<原文件名>, new_name=<新文件名>)
    """
    try:
        os.rename(old_name, new_name)
        return f'文件已从 "{old_name}" 重命名为 "{new_name}"'
    except FileNotFoundError:
        return f'错误：文件 "{old_name}" 不存在'
    except FileExistsError:
        return f'错误：文件 "{new_name}" 已存在'
    except Exception as e:
        return f'重命名失败：{str(e)}'
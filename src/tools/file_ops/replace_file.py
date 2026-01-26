import os

def replace_file(src: str, dst: str):
    """
    使用 os.replace 替换文件（原子操作）
    参数:
        src: 字符串，源文件路径
        dst: 字符串，目标文件路径
    返回:
        成功或错误信息字符串
    用法:
        replace_file(src=<源文件>, dst=<目标文件>)
    """
    try:
        os.replace(src, dst)
        return f'文件已从 "{src}" 替换到 "{dst}"'
    except FileNotFoundError:
        return f'错误：源文件 "{src}" 不存在'
    except Exception as e:
        return f'替换失败：{str(e)}'
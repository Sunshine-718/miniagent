import os
import shutil

def move_file(src: str, dst: str):
    """
    移动文件或文件夹
    参数:
        src: 字符串，源路径
        dst: 字符串，目标路径
    返回:
        成功或错误信息字符串
    用法:
        move_file(src=<源路径>, dst=<目标路径>)
    """
    try:
        # 如果目标是目录，则移动文件到该目录
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        
        shutil.move(src, dst)
        return f'已从 "{src}" 移动到 "{dst}"'
    except FileNotFoundError:
        return f'错误：源路径 "{src}" 不存在'
    except Exception as e:
        return f'移动失败：{str(e)}'
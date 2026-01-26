import os
import shutil

def copy(src: str, dst: str) -> str:
    """
    复制文件或目录
    参数:
        src: 字符串，源路径（文件或目录）
        dst: 字符串，目标路径
    返回:
        成功或错误信息字符串
    用法:
        copy(src=<源路径>, dst=<目标路径>)
    """
    try:
        # 检查源路径是否存在
        if not os.path.exists(src):
            return f'错误：源路径 "{src}" 不存在'
        
        # 如果是文件，复制文件
        if os.path.isfile(src):
            # 如果目标是目录，则复制文件到该目录
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            # 使用 shutil.copy2 复制文件并保留元数据
            shutil.copy2(src, dst)
            return f'已从 "{src}" 复制文件到 "{dst}"'
        
        # 如果是目录，复制目录
        elif os.path.isdir(src):
            # 使用 shutil.copytree 复制目录
            shutil.copytree(src, dst)
            return f'已从 "{src}" 复制目录到 "{dst}"'
        
        else:
            return f'错误：源路径 "{src}" 不是文件也不是目录'
            
    except FileExistsError:
        return f'错误：目标路径 "{dst}" 已存在（对于目录复制）'
    except Exception as e:
        return f'复制失败：{str(e)}'
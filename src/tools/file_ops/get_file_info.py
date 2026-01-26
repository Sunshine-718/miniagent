import os
import stat
import time
from typing import Dict, Any

def get_file_info(file_path: str) -> str:
    """
    获取文件的详细信息，包括大小、时间戳、权限等。
    
    参数:
        file_path: 字符串，文件路径
        
    返回:
        格式化的文件信息字符串，包含：
        - 文件类型
        - 文件大小（字节、KB、MB）
        - 权限
        - 修改时间、创建时间、访问时间
        - inode、设备、硬链接数等元数据
        
    用法:
        get_file_info(file_path=<文件路径>)
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误: 文件 '{file_path}' 不存在"
        
        # 获取文件状态
        file_stat = os.stat(file_path)
        
        # 文件大小（字节）
        size_bytes = file_stat.st_size
        
        # 格式化文件大小
        def format_size(size: int) -> str:
            if size < 1024:
                return f"{size} 字节"
            elif size < 1024 * 1024:
                return f"{size/1024:.2f} KB ({size} 字节)"
            elif size < 1024 * 1024 * 1024:
                return f"{size/(1024*1024):.2f} MB ({size} 字节)"
            else:
                return f"{size/(1024*1024*1024):.2f} GB ({size} 字节)"
        
        # 时间戳转换
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_ctime))
        atime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_atime))
        
        # 文件权限
        mode = file_stat.st_mode
        permissions = stat.filemode(mode)
        
        # 文件类型判断
        if stat.S_ISDIR(mode):
            file_type = "目录"
        elif stat.S_ISREG(mode):
            file_type = "普通文件"
        elif stat.S_ISLNK(mode):
            file_type = "符号链接"
        elif stat.S_ISCHR(mode):
            file_type = "字符设备"
        elif stat.S_ISBLK(mode):
            file_type = "块设备"
        elif stat.S_ISFIFO(mode):
            file_type = "FIFO/管道"
        elif stat.S_ISSOCK(mode):
            file_type = "套接字"
        else:
            file_type = "未知类型"
        
        # 构建信息字符串
        info_lines = [
            f"文件信息: {os.path.abspath(file_path)}",
            f"类型: {file_type}",
            f"大小: {format_size(size_bytes)}",
            f"权限: {permissions}",
            f"修改时间: {mtime}",
            f"创建时间: {ctime}",
            f"访问时间: {atime}",
            f"inode 号: {file_stat.st_ino}",
            f"设备号: {file_stat.st_dev}",
            f"硬链接数: {file_stat.st_nlink}",
            f"用户ID: {file_stat.st_uid}",
            f"组ID: {file_stat.st_gid}",
        ]
        
        return '\n'.join(info_lines)
        
    except PermissionError:
        return f"错误: 没有权限访问文件 '{file_path}'"
    except Exception as e:
        return f"错误: 获取文件信息时发生异常 - {str(e)}"

# 测试代码
if __name__ == "__main__":
    # 测试当前文件
    print(get_file_info(__file__))
    print("\n" + "="*50 + "\n")
    
    # 测试一个不存在的文件
    print(get_file_info("nonexistent_file.txt"))

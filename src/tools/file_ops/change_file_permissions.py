import os
import stat
import platform

def change_file_permissions(file_path: str, permissions: str = None, mode: int = None):
    """
    修改文件或目录的权限
    
    参数:
        file_path: 文件或目录路径
        permissions: 权限字符串，如'755'、'644'等（八进制表示）
        mode: 权限模式整数，如0o755、0o644等
        
    注意：permissions和mode参数二选一，如果都提供，优先使用permissions
        
    返回:
        操作结果信息
    """
    
    if not os.path.exists(file_path):
        return f"错误：路径 {file_path} 不存在"
    
    # 检查操作系统
    system = platform.system()
    if system == 'Windows':
        return "注意：Windows系统对文件权限的支持有限。此工具主要适用于Linux/Unix系统。\n" \
               "在Windows上，文件权限通常由文件系统ACL控制，而不是简单的Unix权限位。"
    
    # 确定要设置的权限模式
    target_mode = None
    
    if permissions:
        try:
            # 将字符串转换为八进制整数
            target_mode = int(permissions, 8)
        except ValueError:
            return f"错误：无效的权限字符串 '{permissions}'，请使用八进制格式如'755'、'644'"
    elif mode is not None:
        target_mode = mode
    else:
        return "错误：必须提供permissions或mode参数"
    
    # 检查权限值是否有效
    if not (0 <= target_mode <= 0o777):
        return f"错误：权限值 {oct(target_mode)} 超出有效范围（0-777）"
    
    try:
        # 获取当前权限
        current_mode = os.stat(file_path).st_mode
        current_permissions = stat.S_IMODE(current_mode)
        
        # 修改权限
        os.chmod(file_path, target_mode)
        
        # 获取修改后的权限
        new_mode = os.stat(file_path).st_mode
        new_permissions = stat.S_IMODE(new_mode)
        
        # 构建结果信息
        result = [
            f"文件：{file_path}",
            f"原权限：{oct(current_permissions)} ({current_permissions:03o})",
            f"新权限：{oct(new_permissions)} ({new_permissions:03o})",
        ]
        
        # 添加权限解释
        if file_path.endswith('.py') or file_path.endswith('.sh'):
            # 对于脚本文件，检查是否设置了执行权限
            is_executable = bool(new_permissions & 0o111)
            result.append(f"可执行：{'是' if is_executable else '否'}")
        
        return "\n".join(result)
        
    except PermissionError:
        return f"错误：没有权限修改 {file_path} 的权限"
    except Exception as e:
        return f"错误：修改权限失败 - {str(e)}"
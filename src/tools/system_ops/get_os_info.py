import platform


def get_os_info() -> str:
    """
    获取当前操作系统的信息。
    参数:
        无
    返回:
        操作系统信息字符串
    用法:
        get_os_info()
    """

    os_name = platform.system()  # e.g., 'Windows', 'Linux', 'Darwin'
    os_version = platform.version()
    os_arch = platform.machine()
    os_release = platform.release()

    info = f"操作系统: {os_name}\n"
    info += f"版本: {os_version}\n"
    info += f"发行版: {os_release}\n"
    info += f"架构: {os_arch}"
    return info

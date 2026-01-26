from datetime import datetime


def get_current_time() -> str:
    """
    获取当前日期和时间
    参数:
        无
    返回:
        当前日期和时间字符串
    用法:
        get_current_time()
    """
    return str(datetime.now())

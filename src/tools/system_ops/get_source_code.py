import sys
import inspect


def get_source_code(name: str):
    """
    传入函数名字符串可以获得tools.py的函数的源代码，方便快速查看，节省token数量
    参数:
        name: 字符串，函数名
    返回:
        函数实现的源代码或报错信息
    用法:
        get_source_code(name=<工具函数名>)
    """
    # 延迟导入，避免循环引用
    import src.tools as tool_pkg
    
    # 在 tool_pkg (即 __init__.py 汇总后的命名空间) 里查找
    # 因为 __init__.py 已经把所有子模块的函数都挂载到自己身上了
    if hasattr(tool_pkg, name):
        func = getattr(tool_pkg, name)
        if inspect.isfunction(func):
            return inspect.getsource(func)
            
    return f'Error: 没有找到函数 "{name}"'

import math


def calculator(expression: str):
    """
    计算数学表达式，支持基本科学计算功能。
    支持：+, -, *, /, **, sqrt, sin, cos, tan, log, log10, exp, pi, e 等。
    参数:
        expression: 字符串，要计算的数学表达式
    返回:
        结果（浮点数）或错误字符串
    用法:
        calculator(expression=<数学表达式>)
    """
    # 为 eval 定义安全环境
    safe_dict = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pi': math.pi,
        'e': math.e,
        'radians': math.radians,
        'degrees': math.degrees,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': math.factorial,
        'pow': math.pow,
    }

    # 添加基本算术运算
    safe_dict.update({
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        '**': lambda x, y: x ** y,
    })

    try:
        # 仅使用 safe_dict 进行 eval
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return str(result)
    except Exception as e:
        return f"错误：{str(e)}"

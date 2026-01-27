import sympy
from sympy import symbols, integrate, diff, limit, simplify, solve, Eq, sin, cos, tan, exp, log, pi, oo

def sympy_tool(operation: str, expression: str, variable: str = 'x', lower: str = None, upper: str = None):
    """
    使用 SymPy 进行符号计算。
    
    参数:
        operation: 操作类型，可选 'integrate', 'diff', 'limit', 'simplify', 'solve', 'matrix'
        expression: 数学表达式字符串，如 'x**2 + sin(x)' 或矩阵字符串 'Matrix([[1, 2], [3, 4]])'
        variable: 变量符号，默认为 'x'；当 operation='matrix' 时，指定矩阵操作类型：
                 'det' - 行列式，'inv' - 逆矩阵，'eigenvalues' - 特征值，
                 'eigenvectors' - 特征向量，'rank' - 秩，'trace' - 迹，
                 'transpose' - 转置，'rref' - 行最简形
        lower: 积分下限或极限趋向的点（字符串形式，如 '0' 或 'oo' 表示无穷）
        upper: 积分上限（仅积分需要）
    
    返回:
        计算结果字符串或错误信息
    """
    try:
        if operation == 'matrix':
            # 线性代数操作
            from sympy import Matrix
            # 解析矩阵表达式
            matrix = sympy.sympify(expression)
            if not isinstance(matrix, Matrix):
                return "错误：表达式必须是一个有效的 SymPy 矩阵。"
            
            if variable == 'det':
                result = matrix.det()
            elif variable == 'inv':
                result = matrix.inv()
            elif variable == 'eigenvalues':
                result = matrix.eigenvals()
            elif variable == 'eigenvectors':
                result = matrix.eigenvects()
            elif variable == 'rank':
                result = matrix.rank()
            elif variable == 'trace':
                result = matrix.trace()
            elif variable == 'transpose':
                result = matrix.T
            elif variable == 'rref':
                result = matrix.rref()
            else:
                return f"错误：不支持的矩阵操作 '{variable}'。支持的操作: det, inv, eigenvalues, eigenvectors, rank, trace, transpose, rref"
            return str(result)
        
        # 原有操作
        # 定义符号
        x = symbols(variable)
        # 解析表达式
        expr = sympy.sympify(expression)
        
        if operation == 'simplify':
            result = simplify(expr)
            return str(result)
        
        elif operation == 'diff':
            result = diff(expr, x)
            return str(result)
        
        elif operation == 'integrate':
            if lower is not None and upper is not None:
                # 定积分
                lower_expr = sympy.sympify(lower)
                upper_expr = sympy.sympify(upper)
                result = integrate(expr, (x, lower_expr, upper_expr))
            else:
                # 不定积分
                result = integrate(expr, x)
            return str(result)
        
        elif operation == 'limit':
            if lower is None:
                return "错误：极限需要指定趋向点（lower 参数）"
            point = sympy.sympify(lower)
            result = limit(expr, x, point)
            return str(result)
        
        elif operation == 'solve':
            # 解方程，表达式应为等式，如 'x**2 - 1 = 0'
            if '=' in expression:
                lhs, rhs = expression.split('=', 1)
                eq = Eq(sympy.sympify(lhs), sympy.sympify(rhs))
            else:
                eq = Eq(expr, 0)
            solutions = solve(eq, x)
            return str(solutions)
        
        else:
            return f"错误：不支持的操作 '{operation}'。支持的操作: simplify, diff, integrate, limit, solve, matrix"
    
    except Exception as e:
        return f"错误：{str(e)}"

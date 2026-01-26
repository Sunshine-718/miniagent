import io
import contextlib


def python_repl(code: str):
    """
    调用Python解释器运行Python代码，并且返回结果到标准输出
    变量在多次调用之间持续保持
    参数:
        code: 字符串，代码
    返回:
        代码运行结果或报错信息
    用法:
        python_repl(code=<你的代码>)
    """
    io_buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(io_buffer), contextlib.redirect_stderr(io_buffer):
            exec(code, globals())
        output = io_buffer.getvalue()
        if not output.strip():
            return "Execution successful, but no output produced. (Hint: Use print() to see results)"
        return output
    except Exception as e:
        return f"Runtime Error: {e}"

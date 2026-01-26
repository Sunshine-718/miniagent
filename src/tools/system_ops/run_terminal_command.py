import subprocess


def run_terminal_command(command: str):
    """
    在终端中运行命令 (支持实时输出反馈)
    参数:
        command: 字符串，命令
    返回:
        命令的所有输出内容
    用法:
        run_terminal_command(command=<命令>)
    """
    try:
        print(f"Executing: {command}")  # 提示当前执行的命令

        # 使用 Popen 实现流式输出
        # stderr=subprocess.STDOUT 表示将错误输出合并到标准输出中
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',  # 显式指定编码，防止中文乱码
            errors='replace'   # 遇到无法解码的字符时不报错，用占位符替代
        )

        output_lines = []

        # 实时逐行读取输出
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            if line:
                # 1. 实时打印给人类看 (去除末尾换行符以免双重换行)
                print(line.strip())
                # 2. 收集起来给 Agent 看
                output_lines.append(line)

        # 等待进程完全结束
        process.wait()

        full_output = "".join(output_lines).strip()

        if process.returncode == 0:
            if not full_output:
                return "命令执行成功（无输出）。"
            return full_output
        else:
            # 即使失败了，Agent 也能看到之前的报错详情
            return f"错误（退出码 {process.returncode}）：\n{full_output}"

    except Exception as e:
        return f"系统错误：{str(e)}"

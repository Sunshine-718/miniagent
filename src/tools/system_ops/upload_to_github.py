from .run_terminal_command import run_terminal_command


def upload_to_github(commit_message: str = "Update code files") -> str:
    """
    使用 run_terminal_command 执行三行 Git 命令上传到 GitHub。
    参数:
        commit_message: 字符串，提交信息
    返回:
        操作结果字符串
    用法:
        upload_to_github(commit_message=<提交信息>)
    """
    results = []

    # 1. 添加所有更改
    result1 = run_terminal_command("git add .")
    results.append(f"添加文件结果: {result1}")

    # 2. 提交更改
    result2 = run_terminal_command(f'git commit -m "{commit_message}"')
    results.append(f"提交结果: {result2}")

    # 3. 推送到远程仓库
    result3 = run_terminal_command("git push")
    results.append(f"推送结果: {result3}")

    return "\n".join(results)

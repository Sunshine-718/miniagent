import os
import difflib


def check_file_diff(file_path: str, new_content: str):
    """
    检查如果将 new_content 写入 file_path，会产生什么差异。
    用于在实际覆盖文件前进行预览和检查。

    参数:
        file_path: 现有文件路径
        new_content: 准备写入的新内容
    返回:
        Diff 差异字符串
    """
    if not os.path.exists(file_path):
        return f"New File: {file_path} (Entire content is new)"

    # 读取旧内容
    with open(file_path, 'r', encoding='utf-8') as f:
        old_content = f.read()

    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f'{file_path} (Current)',
        tofile=f'{file_path} (New)',
        lineterm=''
    )

    diff_text = ''.join(diff)
    if not diff_text:
        return "No changes detected."
    return diff_text

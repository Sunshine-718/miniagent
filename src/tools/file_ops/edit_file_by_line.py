import os


def edit_file_by_line(file_path: str, line_number: int, new_line_content: str = None, mode: str = "replace"):
    """
    基于行号修改文件。

    参数:
        file_path: 文件路径
        line_number: 目标行号（从 1 开始）。
        new_line_content: 新的一行内容（如果 mode 为 'delete' 则忽略此参数）。
        mode: 操作模式 - 'replace' (替换该行), 'insert' (在该行前插入), 'delete' (删除该行)。
    """
    if not os.path.exists(file_path):
        return f"错误：文件不存在。"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 转换为索引 (0-based)
        idx = line_number - 1

        if idx < 0 or idx >= len(lines) + (1 if mode == 'insert' else 0):
            return f"错误：行号 {line_number} 超出范围 (当前文件共 {len(lines)} 行)。"

        # 处理换行符：确保输入的内容末尾有换行
        if new_line_content and not new_line_content.endswith('\n'):
            new_line_content += '\n'

        if mode == 'replace':
            lines[idx] = new_line_content
        elif mode == 'insert':
            lines.insert(idx, new_line_content)
        elif mode == 'delete':
            del lines[idx]
        else:
            return "错误：未知模式，仅支持 replace, insert, delete。"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return f"操作成功：Line {line_number} 已执行 {mode}。"

    except Exception as e:
        return f"错误：{str(e)}"

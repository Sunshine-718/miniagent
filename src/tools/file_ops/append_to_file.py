import os

def append_to_file(file_name: str, content: str, line_number: int = None):
    """
    在文件的特定行或末尾追加内容。
    参数:
        file_name: 字符串，文件名
        content: 字符串，要追加的内容
        line_number: 整数，可选的行号（从1开始）。如果为None或未提供，则追加到末尾。
    返回:
        无
    用法:
        append_to_file(file_name=<文件名>, content=<内容>, line_number=<行号>)
    """
    # 如果文件不存在，创建它
    if not os.path.exists(file_name):
        with open(file_name, 'w', encoding='utf-8') as f:
            pass  # 创建空文件

    if line_number is None:
        # 追加到文件末尾
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(content)
    else:
        # 插入到特定行（从1开始）
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 转换为0索引
        idx = line_number - 1
        # 如果行号超出末尾，则追加到末尾
        if idx > len(lines):
            lines.append(content)
        else:
            # 确保索引非负
            idx = max(0, idx)
            lines.insert(idx, content)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    return f'函数运行成功'

import os


def count_file_lines(file_path: str) -> str:
    """
    统计文件的行数信息。

    参数:
        file_path: 字符串，文件路径

    返回:
        包含总行数、非空行数和空行数的统计信息字符串

    用法:
        count_file_lines(file_path=<文件路径>)
    """
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在。"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)
        non_empty_lines = 0
        empty_lines = 0

        for line in lines:
            if line.strip() == '':
                empty_lines += 1
            else:
                non_empty_lines += 1

        # 计算百分比
        if total_lines > 0:
            non_empty_percent = (non_empty_lines / total_lines) * 100
            empty_percent = (empty_lines / total_lines) * 100
        else:
            non_empty_percent = 0.0
            empty_percent = 0.0

        result = f"文件: {file_path}\n"
        result += f"总行数: {total_lines}\n"
        result += f"非空行数: {non_empty_lines} ({non_empty_percent:.1f}%)\n"
        result += f"空行数: {empty_lines} ({empty_percent:.1f}%)\n"

        # 添加一些分析建议
        if empty_percent > 30:
            result += "提示：文件中有较多空行，建议适当清理以提升可读性。"
        elif non_empty_percent == 100:
            result += "提示：文件中没有空行，代码紧凑。"
        else:
            result += "提示：空行比例适中，代码结构良好。"

        return result

    except Exception as e:
        return f"读取文件时出错：{str(e)}"

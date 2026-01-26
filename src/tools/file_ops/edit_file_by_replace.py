import os


def edit_file_by_replace(file_path: str, old_text: str, new_text: str):
    """
    通过查找并替换特定的文本块来修改文件（精准修改，节省Token）。

    参数:
        file_path: 文件路径
        old_text: 原文中需要被替换的**准确**代码块或文本（必须与文件内容完全一致，包括空格和缩进）。
        new_text: 想要替换成的新内容。

    返回:
        操作结果信息。
    """
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在。"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. 检查 old_text 是否存在
        if old_text not in content:
            # 尝试做一个简单的容错：去除两端空白再试（可选）
            if old_text.strip() in content:
                return "错误：找到相似内容，但空白字符（空格/缩进）不匹配。请精确复制原文。"
            return "错误：在文件中未找到指定的 old_text。请确保通过 read_file 确认了最新的文件内容，并精确复制要修改的代码块。"

        # 2. 检查唯一性 (防止误伤)
        if content.count(old_text) > 1:
            return f"错误：指定的 old_text 在文件中出现了 {content.count(old_text)} 次，系统无法确定替换哪一处。请提供更长的 old_text 以确保唯一性。"

        # 3. 执行替换
        new_content = content.replace(old_text, new_text, 1)  # 只替换一次

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return "修改成功！"

    except Exception as e:
        return f"系统错误：{str(e)}"

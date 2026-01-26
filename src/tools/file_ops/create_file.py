def create_file(file_name: str, content: str) -> None:
    """
    创建文件
    参数:
        file_name: 字符串，文件名
        content: 字符串，文件内容
    返回:
        无
    用法:
        create_file(file_name=<文件名>, content=<文件内容>)
    """
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)
    return f'文件：{file_name} 已创建成功'
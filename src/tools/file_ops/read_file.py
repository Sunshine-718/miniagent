def read_file(file_name: str) -> str:
    """
    读取文件内容
    参数:
        file_name: 字符串，文件名
    返回:
        文件内容
    用法:
        read_file(file_name=<文件名>)
    """
    with open(file_name, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
    return ''.join(lines)
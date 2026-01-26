import os
import difflib

def read_file_with_encoding(file_path: str) -> str:
    """尝试多种编码读取文件"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            continue
    
    # 如果所有编码都失败，尝试二进制读取
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            # 尝试解码为字符串，忽略错误
            return content.decode('utf-8', errors='ignore')
    except Exception as e:
        raise IOError(f"无法读取文件 '{file_path}'，所有编码尝试都失败: {str(e)}")


def compare_files(file1: str, file2: str) -> str:
    """
    比较两个文件的内容差异
    
    参数:
        file1: 字符串，第一个文件路径
        file2: 字符串，第二个文件路径
    
    返回:
        差异字符串（如果文件相同则返回"两个文件内容相同"）
    
    用法:
        compare_files(file1=<文件1路径>, file2=<文件2路径>)
    """
    # 检查文件是否存在
    if not os.path.exists(file1):
        return f"错误：文件 '{file1}' 不存在"
    if not os.path.exists(file2):
        return f"错误：文件 '{file2}' 不存在"
    
    try:
        # 读取文件内容（使用多种编码尝试）
        content1 = read_file_with_encoding(file1)
        content2 = read_file_with_encoding(file2)
    except Exception as e:
        return f"读取文件失败：{str(e)}"
    
    # 分割行
    lines1 = content1.splitlines(keepends=True)
    lines2 = content2.splitlines(keepends=True)
    
    # 生成差异
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=file1,
        tofile=file2,
        lineterm=''
    )
    
    diff_text = ''.join(diff)
    if not diff_text:
        return "两个文件内容相同"
    
    return diff_text
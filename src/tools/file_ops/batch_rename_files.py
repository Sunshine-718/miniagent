import os
import re

def batch_rename_files(directory: str, pattern: str, replacement: str, preview: bool = True):
    """
    批量重命名文件
    
    参数:
        directory: 目录路径
        pattern: 要匹配的正则表达式模式
        replacement: 替换的字符串
        preview: 预览模式（只显示将要重命名的文件，不实际执行），默认为True
        
    返回:
        重命名结果信息
    """
    
    if not os.path.exists(directory):
        return f"错误：目录 {directory} 不存在"
    
    if not os.path.isdir(directory):
        return f"错误：{directory} 不是目录"
    
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"错误：无效的正则表达式模式 '{pattern}': {str(e)}"
    
    renamed_files = []
    skipped_files = []
    
    # 获取目录中的所有文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # 只处理文件，跳过目录
        if not os.path.isfile(file_path):
            continue
        
        # 应用正则表达式替换
        new_filename = regex.sub(replacement, filename)
        
        # 如果文件名没有变化，跳过
        if new_filename == filename:
            skipped_files.append(filename)
            continue
        
        new_file_path = os.path.join(directory, new_filename)
        
        # 检查新文件名是否已存在
        if os.path.exists(new_file_path):
            skipped_files.append(f"{filename} -> {new_filename} (目标文件已存在)")
            continue
        
        renamed_files.append({
            'old': filename,
            'new': new_filename,
            'old_path': file_path,
            'new_path': new_file_path
        })
    
    # 构建结果信息
    result = []
    
    if renamed_files:
        result.append(f"找到 {len(renamed_files)} 个文件需要重命名：")
        for item in renamed_files:
            result.append(f"  {item['old']} -> {item['new']}")
        
        # 如果不是预览模式，实际执行重命名
        if not preview:
            success_count = 0
            for item in renamed_files:
                try:
                    os.rename(item['old_path'], item['new_path'])
                    success_count += 1
                except Exception as e:
                    result.append(f"  重命名失败 {item['old']}: {str(e)}")
            
            result.append(f"\n成功重命名 {success_count} 个文件")
        else:
            result.append("\n这是预览模式，要实际执行重命名，请设置 preview=False")
    else:
        result.append("没有找到需要重命名的文件")
    
    if skipped_files:
        result.append(f"\n跳过了 {len(skipped_files)} 个文件：")
        for filename in skipped_files[:10]:  # 只显示前10个
            result.append(f"  {filename}")
        if len(skipped_files) > 10:
            result.append(f"  ... 还有 {len(skipped_files) - 10} 个")
    
    return "\n".join(result)
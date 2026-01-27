import os
import re
import json
from collections import Counter

def analyze_python_code_letter_frequency(project_root='.'):
    """分析Python项目中的字母频率"""
    
    # 1. 查找所有Python文件
    python_files = []
    for dirpath, dirnames, filenames in os.walk(project_root):
        if '__pycache__' in dirpath or '.git' in dirpath:
            continue
        for filename in filenames:
            if filename.endswith('.py'):
                python_files.append(os.path.join(dirpath, filename))
    
    # 2. 统计字母频率
    letter_counter = Counter()
    total_letters = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                letters = re.findall(r'[a-zA-Z]', content)
                letter_counter.update(letters)
                total_letters += len(letters)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # 3. 准备结果
    case_sensitive = dict(letter_counter)
    case_insensitive = Counter()
    
    for letter, count in letter_counter.items():
        case_insensitive[letter.lower()] += count
    
    result = {
        'total_files': len(python_files),
        'total_letters': total_letters,
        'letter_frequency_case_sensitive': case_sensitive,
        'letter_frequency_case_insensitive': dict(case_insensitive)
    }
    
    return result

if __name__ == '__main__':
    # 使用示例
    stats = analyze_python_code_letter_frequency()
    print(f"分析完成！共分析 {stats['total_files']} 个文件，{stats['total_letters']} 个字母")
    
    # 保存结果
    with open('letter_frequency_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print("结果已保存到 letter_frequency_stats.json")

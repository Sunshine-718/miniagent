import os
import json
from datetime import datetime
from typing import Optional, List
from ._utils import load_index, save_index, extract_keywords, categorize_memory, CATEGORIES_DIR


def save_memory(key: str, value: str, keywords: Optional[List[str]] = None) -> str:
    """
    保存记忆到分类目录并更新索引
    参数:
        key: 字符串，记忆关键词
        value: 字符串，记忆内容
        keywords: 可选的关键词列表，如果为None则自动从内容中提取
    """
    index = load_index()
    if index is None:
        return "错误：索引文件损坏，无法读取。"

    # 1. 确定分类和路径
    category = categorize_memory(key, value)
    timestamp = datetime.now().isoformat()
    
    # 2. 确定关键词：如果提供了自定义关键词则使用，否则自动提取
    if keywords is not None:
        # 确保key总是包含在关键词中，并去重
        keywords = list(set([key.lower()] + keywords))
    else:
        keywords = [key.lower()] + extract_keywords(value)

    memory_filename = f"{key}.json"
    memory_path = os.path.join(CATEGORIES_DIR, category, memory_filename)

    # 2. 写入记忆文件
    os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    memory_data = {
        'value': value,
        'timestamp': timestamp,
        'keywords': keywords
    }
    with open(memory_path, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)

    # 3. 处理分类变更 (如果key已存在但分类变了)
    if key in index['memories']:
        old_category = index['memories'][key]['category']
        if old_category != category:
            # 清理旧分类计数
            index['categories'][old_category]['count'] -= 1
            if key in index['categories'][old_category]['memory_keys']:
                index['categories'][old_category]['memory_keys'].remove(key)
            # 删除旧文件
            old_path = os.path.join(CATEGORIES_DIR, old_category, f"{key}.json")
            if os.path.exists(old_path) and old_path != memory_path:
                os.remove(old_path)
            # 清理旧关键词索引
            old_keywords = index['memories'][key].get('keywords', [])
            for k in old_keywords:
                if k in index['keyword_index'] and key in index['keyword_index'][k]:
                    index['keyword_index'][k].remove(key)
                    if not index['keyword_index'][k]:
                        del index['keyword_index'][k]
    else:
        index['total_memories'] += 1

    # 4. 更新分类统计
    if key not in index['categories'][category]['memory_keys']:
        index['categories'][category]['count'] += 1
        index['categories'][category]['memory_keys'].append(key)

    # 5. 更新主索引记录
    index['memories'][key] = {
        "key": key,
        "category": category,
        "file_path": memory_path,
        "timestamp": timestamp,
        "keywords": keywords
    }

    # 6. 更新反向关键词索引
    for k in keywords:
        if k not in index['keyword_index']:
            index['keyword_index'][k] = []
        if key not in index['keyword_index'][k]:
            index['keyword_index'][k].append(key)

    save_index(index)
    return f"记忆 '{key}' 已保存到分类 '{category}'"

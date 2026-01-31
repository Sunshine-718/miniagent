import json
from ._utils import load_index


def _read_memory_file(file_path: str) -> tuple:
    """安全读取记忆文件，返回 (value, timestamp, category) 或 (None, None, None)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 从文件路径反推 category（兼容现有结构）
        import os
        category = os.path.basename(os.path.dirname(file_path))
        return (
            data.get('value', ''),
            data.get('timestamp', '未知'),
            category
        )
    except Exception:
        return None, None, None


def search_memory(keyword: str, fuzzy: bool = True) -> str:
    """
    通过索引搜索记忆
    参数:
        keyword: 字符串，搜索关键词
        fuzzy: 布尔值，是否使用模糊搜索（默认True）
    """
    index = load_index()
    if index is None:
        return "错误：索引文件损坏或不存在"

    keyword_lower = keyword.lower()
    results = []
    seen_keys = set()

    # 1. 精确匹配 (Key匹配 或 关键词索引匹配)
    candidates = set()
    if keyword_lower in index['memories']:
        candidates.add((keyword_lower, 100))  # Key 完全匹配
    
    if keyword_lower in index['keyword_index']:
        for k in index['keyword_index'][keyword_lower]:
            candidates.add((k, 90))  # 关键词索引匹配

    # 2. 模糊搜索 (如果不满足精确匹配)
    if fuzzy:
        # 遍历所有 Key
        for k in index['memories']:
            if keyword_lower in k.lower():
                candidates.add((k, 70))
        # 遍历关键词索引的部分匹配
        for kw in index['keyword_index']:
            if keyword_lower in kw:
                for k in index['keyword_index'][kw]:
                    candidates.add((k, 50))

    # 3. 统一读取内容
    for key, score in candidates:
        if key in seen_keys:
            continue
        seen_keys.add(key)
        
        info = index['memories'].get(key)
        if not info:
            continue
            
        content, ts, cat = _read_memory_file(info['file_path'])
        if content is not None:
            results.append({
                "key": key,
                "value": content,
                "timestamp": ts,
                "category": cat,
                "score": score
            })

    # 4. 格式化输出
    results.sort(key=lambda x: x['score'], reverse=True)
    if not results:
        return "未找到相关记忆"

    output = f"找到 {len(results)} 条相关记忆：\n"
    for i, res in enumerate(results[:5], 1):
        preview = res['value'][:100].replace('\n', ' ')
        if len(res['value']) > 100:
            preview += "..."
        output += f"{i}. [{res['key']}] (分类: {res['category']}, 时间: {res['timestamp']})\n"
        output += f"   内容: {preview}\n"

    return output

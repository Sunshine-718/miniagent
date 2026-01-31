from ._utils import load_index


def _get_category_summary(category: str, info: dict, index: dict) -> str:
    """生成单个分类的摘要字符串"""
    count = info['count']
    if count == 0:
        return ""
    
    lines = [f"\n📂 {category} ({count}):"]
    # 只列出最新的 5 个
    recent_keys = info['memory_keys'][-5:]
    for key in recent_keys:
        ts = index['memories'].get(key, {}).get('timestamp', '')[:10]
        lines.append(f"  - {key} ({ts})")
    if count > 5:
        lines.append(f"  ... 以及其他 {count - 5} 条")
    return "\n".join(lines)


def get_all_memories() -> str:
    """
    从索引获取所有记忆概览
    """
    index = load_index()
    if index is None:
        return "错误：索引文件损坏或不存在"

    if index['total_memories'] == 0:
        return "暂无记忆"

    output = f"🧠 记忆库概览 (共 {index['total_memories']} 条):\n"

    for category, info in index['categories'].items():
        section = _get_category_summary(category, info, index)
        if section:
            output += section

    return output

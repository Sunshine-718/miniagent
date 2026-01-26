from ._utils import load_index


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
        count = info['count']
        if count > 0:
            output += f"\n📂 {category} ({count}):\n"
            # 只列出最新的 5 个
            recent_keys = info['memory_keys'][-5:]
            for key in recent_keys:
                ts = index['memories'][key].get('timestamp', '')[:10]  # 只显示日期
                output += f"  - {key} ({ts})\n"
            if count > 5:
                output += f"  ... 以及其他 {count - 5} 条\n"

    return output

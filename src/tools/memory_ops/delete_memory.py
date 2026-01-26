import os
from ._utils import load_index, save_index


def delete_memory(key: str) -> str:
    """
    删除记忆并更新索引
    参数:
        key: 字符串，要删除的记忆关键词
    """
    index = load_index()
    if index is None:
        return "错误：索引文件损坏或不存在"

    if key not in index['memories']:
        return f"错误：未找到记忆 '{key}'"

    memory_info = index['memories'][key]
    category = memory_info['category']

    # 1. 删除物理文件
    if os.path.exists(memory_info['file_path']):
        try:
            os.remove(memory_info['file_path'])
        except OSError as e:
            return f"错误：删除文件失败 {str(e)}"

    # 2. 更新分类索引
    if key in index['categories'][category]['memory_keys']:
        index['categories'][category]['memory_keys'].remove(key)
        index['categories'][category]['count'] = max(0, index['categories'][category]['count'] - 1)

    # 3. 更新关键词索引
    keywords = memory_info.get('keywords', [])
    for k in keywords:
        if k in index['keyword_index'] and key in index['keyword_index'][k]:
            index['keyword_index'][k].remove(key)
            if not index['keyword_index'][k]:
                del index['keyword_index'][k]

    # 4. 删除主索引
    del index['memories'][key]
    index['total_memories'] = max(0, index['total_memories'] - 1)

    save_index(index)
    return f"记忆 '{key}' 已成功从分类 '{category}' 中删除"

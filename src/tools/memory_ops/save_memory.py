import os
import json
from datetime import datetime
from typing import List

CATEGORIES_DIR = "memory/"

def categorize_memory(key: str, value: str) -> str:
    """
    【已内联】智能分类记忆
    规则：
      - key 以 "user_" 开头 → "user_preferences"
      - key 以 "api_" 或 "token" 开头 → "api_keys"
      - key 为 "test_*" 或包含 "test" → "test"
      - 其他 → "general"
    """
    key_lower = key.lower()
    if key_lower.startswith("user_"):
        return "user_preferences"
    elif key_lower.startswith(("api_", "token")) or "api" in key_lower:
        return "api_keys"
    elif key_lower.startswith("test_") or "test" in key_lower:
        return "test"
    else:
        return "general"

def _ensure_category_dir(category: str):
    """确保分类目录存在"""
    os.makedirs(os.path.join(CATEGORIES_DIR, category), exist_ok=True)

def _write_memory_file(memory_path: str, value: str, timestamp: str, keywords: List[str]):
    """写入记忆JSON文件"""
    os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    memory_data = {
        'value': value,
        'timestamp': timestamp,
        'keywords': keywords
    }
    with open(memory_path, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)

def load_index() -> dict:
    """加载索引文件（简易版，避免依赖 _utils）"""
    try:
        if os.path.exists("memory/index.json"):
            with open("memory/index.json", "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {"memories": {}, "total_memories": 0, "last_updated": datetime.now().isoformat()}
    except Exception:
        return {"memories": {}, "total_memories": 0, "last_updated": datetime.now().isoformat()}

def save_index(index: dict):
    """保存索引文件（简易版）"""
    try:
        os.makedirs("memory/", exist_ok=True)
        with open("memory/index.json", "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _handle_category_migration(index, key: str, old_category: str, new_category: str, old_keywords: List[str]):
    """处理记忆分类迁移：清理旧分类索引与文件"""
    # 更新旧分类计数
    if "categories" in index and old_category in index["categories"]:
        if key in index['categories'][old_category]['memory_keys']:
            index['categories'][old_category]['memory_keys'].remove(key)
            index['categories'][old_category]['count'] = max(0, index['categories'][old_category]['count'] - 1)
    
    # 删除旧文件
    old_path = os.path.join(CATEGORIES_DIR, old_category, f"{key}.json")
    if os.path.exists(old_path) and old_path != os.path.join(CATEGORIES_DIR, new_category, f"{key}.json"):
        try:
            os.remove(old_path)
        except OSError:
            pass  # 忽略删除失败
    
    # 清理旧关键词索引
    if "keyword_index" in index:
        for k in old_keywords:
            if k in index['keyword_index'] and key in index['keyword_index'][k]:
                index['keyword_index'][k].remove(key)
                if not index['keyword_index'][k]:
                    del index['keyword_index'][k]

def _update_index_on_save(index, key: str, category: str, memory_path: str, timestamp: str, keywords: List[str]):
    """统一更新索引：新增或迁移后刷新所有相关字段"""
    # 初始化 categories 和 keyword_index（如果不存在）
    if "categories" not in index:
        index["categories"] = {}
    if "keyword_index" not in index:
        index["keyword_index"] = {}
    
    # 分类统计
    if category not in index["categories"]:
        index["categories"][category] = {"count": 0, "memory_keys": []}
    if key not in index["categories"][category]["memory_keys"]:
        index["categories"][category]["count"] += 1
        index["categories"][category]["memory_keys"].append(key)
    
    # 主索引记录
    if "memories" not in index:
        index["memories"] = {}
    index["memories"][key] = {
        "key": key,
        "category": category,
        "file_path": memory_path,
        "timestamp": timestamp,
        "keywords": keywords
    }
    
    # 关键词索引
    for k in keywords:
        if k not in index["keyword_index"]:
            index["keyword_index"][k] = []
        if key not in index["keyword_index"][k]:
            index["keyword_index"][k].append(key)

def save_memory(key: str, value: str, keywords: List[str]) -> str:
    """
    保存记忆到分类目录并更新索引
    参数:
        key: 字符串，记忆关键词
        value: 字符串，记忆内容
        keywords: 必须提供的关键词列表（不再支持自动提取）
    """
    index = load_index()
    if index is None:
        return "错误：索引文件损坏，无法读取。"

    # 1. 确定分类和路径
    category = categorize_memory(key, value)
    timestamp = datetime.now().isoformat()
    keywords = list(set([key.lower()] + keywords))
    
    memory_path = os.path.join(CATEGORIES_DIR, category, f"{key}.json")

    # 2. 写入文件
    _ensure_category_dir(category)
    _write_memory_file(memory_path, value, timestamp, keywords)

    # 3. 处理迁移 or 新增
    if key in index.get("memories", {}):
        old_info = index["memories"][key]
        old_category = old_info.get('category', category)
        old_keywords = old_info.get('keywords', [])
        if old_category != category:
            _handle_category_migration(index, key, old_category, category, old_keywords)
    else:
        index["total_memories"] = index.get("total_memories", 0) + 1

    # 4. 统一更新索引
    _update_index_on_save(index, key, category, memory_path, timestamp, keywords)
    save_index(index)
    return f"记忆 '{key}' 已保存到分类 '{category}'"

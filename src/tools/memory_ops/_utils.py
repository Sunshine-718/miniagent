import re
from typing import List, Dict, Any
import json
import os
from datetime import datetime

CATEGORIES_DIR = "memory/"

def load_index() -> Dict[str, Any]:
    """加载索引文件"""
    try:
        if os.path.exists("memory/index.json"):
            with open("memory/index.json", "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {"memories": {}, "total_memories": 0, "last_updated": datetime.now().isoformat()}
    except Exception as e:
        return None

def save_index(index: Dict[str, Any]):
    """保存索引文件"""
    try:
        os.makedirs("memory/", exist_ok=True)
        with open("memory/index.json", "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

def _ensure_category_dir(category: str):
    """确保分类目录存在"""
    path = os.path.join(CATEGORIES_DIR, category)
    os.makedirs(path, exist_ok=True)

def _write_memory_file(file_path: str, value: str, timestamp: str, keywords: List[str]):
    """写入记忆文件"""
    data = {
        "value": value,
        "timestamp": timestamp,
        "keywords": keywords
    }
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _update_index_on_save(index: Dict[str, Any], key: str, category: str, file_path: str, timestamp: str, keywords: List[str]):
    """统一更新索引"""
    index["memories"][key] = {
        "category": category,
        "file_path": file_path,
        "timestamp": timestamp,
        "keywords": keywords
    }
    index["last_updated"] = timestamp

def _handle_category_migration(index: Dict[str, Any], key: str, old_category: str, new_category: str, old_keywords: List[str]):
    """处理分类迁移"""
    old_path = os.path.join(CATEGORIES_DIR, old_category, f"{key}.json")
    new_path = os.path.join(CATEGORIES_DIR, new_category, f"{key}.json")
    if os.path.exists(old_path):
        os.replace(old_path, new_path)
    if key in index["memories"]:
        del index["memories"][key]

def categorize_memory(key: str, value: str) -> str:
    """
    【已修复】智能分类记忆
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

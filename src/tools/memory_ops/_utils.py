import json
import os
import re
from datetime import datetime

# 统一配置路径
MEMORY_DIR = 'memory'
INDEX_FILE = os.path.join(MEMORY_DIR, 'index.json')
CATEGORIES_DIR = os.path.join(MEMORY_DIR, 'categories')


def load_index():
    """加载索引文件"""
    if not os.path.exists(INDEX_FILE):
        # 创建默认索引结构
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "total_memories": 0,
            "categories": {
                "user_preferences": {"count": 0, "memory_keys": []},
                "api_keys": {"count": 0, "memory_keys": []},
                "project_info": {"count": 0, "memory_keys": []},
                "documentation": {"count": 0, "memory_keys": []},
                "general": {"count": 0, "memory_keys": []}
            },
            "memories": {},
            "keyword_index": {}
        }

    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def save_index(index):
    """保存索引文件"""
    index['updated_at'] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def extract_keywords(text):
    """从文本中提取关键词"""
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
                  'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could', 'shall', 'should', 'may', 'might', 'must'}
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return list(set(keywords))


def categorize_memory(key, value):
    """根据记忆key和内容确定分类"""
    text = (key + " " + value).lower()

    if any(k in text for k in ['preference', 'user', '喜欢', '偏好', '习惯']):
        return 'user_preferences'
    elif any(k in text for k in ['api', 'key', 'token', 'secret', 'password']):
        return 'api_keys'
    elif any(k in text for k in ['project', '结构', '架构', 'path', 'dir']):
        return 'project_info'
    elif any(k in text for k in ['doc', 'manual', 'guide', '限制', 'rule']):
        return 'documentation'
    else:
        return 'general'

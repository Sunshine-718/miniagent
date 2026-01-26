import random

def rock_paper_scissors(user_choice: str) -> str:
    """
    石头剪刀布游戏
    
    参数:
        user_choice: 用户的选择，支持中英文：
                    "rock"或"石头" - 石头
                    "paper"或"布" - 布
                    "scissors"或"剪刀" - 剪刀
        
    返回:
        游戏结果字符串，包含AI的选择和胜负结果
    """
    # 定义有效选择和映射
    choice_map = {
        "rock": "石头",
        "石头": "石头",
        "paper": "布",
        "布": "布",
        "scissors": "剪刀",
        "剪刀": "剪刀"
    }
    
    # 标准化用户输入
    user_choice_lower = user_choice.lower()
    
    # 检查输入是否有效
    if user_choice_lower not in choice_map:
        valid_choices = list(set([k for k in choice_map.keys() if len(k) > 1]))
        return f"错误：无效的选择 '{user_choice}'。请从 {valid_choices} 中选择。"
    
    user_normalized = choice_map[user_choice_lower]
    
    # AI随机选择（使用英文键值方便逻辑判断）
    ai_choices = ["rock", "paper", "scissors"]
    ai_choice_en = random.choice(ai_choices)
    ai_choice_cn = choice_map[ai_choice_en]
    
    # 将用户选择转换为英文用于逻辑判断
    user_choice_en = None
    for eng, chn in choice_map.items():
        if chn == user_normalized and eng in ai_choices:
            user_choice_en = eng
            break
    
    # 判断胜负
    if user_choice_en == ai_choice_en:
        result = "平局"
    elif (user_choice_en == "rock" and ai_choice_en == "scissors") or \
         (user_choice_en == "scissors" and ai_choice_en == "paper") or \
         (user_choice_en == "paper" and ai_choice_en == "rock"):
        result = "你赢了！"
    else:
        result = "你输了！"
    
    # 格式化结果
    return f"你出了：{user_normalized}\nAI出了：{ai_choice_cn}\n结果：{result}"

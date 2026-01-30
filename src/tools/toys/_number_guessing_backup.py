import random
import json
import os

def number_guessing_game(action: str = "start", guess: int = None, 
                        min_num: int = 1, max_num: int = 100,
                        game_id: str = "default") -> str:
    """
    数字猜谜游戏
    
    参数:
        action: 操作类型
            "start" - 开始新游戏
            "guess" - 猜测数字
            "hint" - 获取提示（当前范围）
            "status" - 查看游戏状态
            "reset" - 重置游戏
        guess: 猜测的数字（当action为"guess"时必需）
        min_num: 最小数字，默认1
        max_num: 最大数字，默认100
        game_id: 游戏ID，允许多个独立游戏，默认"default"
        
    返回:
        游戏状态或结果字符串
    
    示例:
        >>> number_guessing_game("start", min_num=1, max_num=50)
        "新游戏开始！猜一个 1 到 50 之间的数字。"
        
        >>> number_guessing_game("guess", 25)
        "太小了！再试一次。 (第1次猜测)"
        
        >>> number_guessing_game("hint")
        "提示：数字在 25 到 50 之间。"
        
        >>> number_guessing_game("status")
        "游戏进行中。范围：1-50，已猜测：1次"
    """
    # 游戏状态文件路径
    state_dir = "storage/game_states"
    os.makedirs(state_dir, exist_ok=True)
    state_file = os.path.join(state_dir, f"number_guessing_{game_id}.json")
    
    # 加载或初始化游戏状态
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except:
            state = {}
    else:
        state = {}
    
    # 处理不同操作
    if action == "start":
        # 开始新游戏
        target = random.randint(min_num, max_num)
        state = {
            "target_number": target,
            "min_num": min_num,
            "max_num": max_num,
            "guesses": 0,
            "game_over": False,
            "hint_min": min_num,
            "hint_max": max_num
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)
            
        return f"新游戏开始！猜一个 {min_num} 到 {max_num} 之间的数字。"
    
    elif action == "guess":
        # 猜测数字
        if "target_number" not in state:
            return "请先使用 'start' 开始新游戏。"
        
        if state["game_over"]:
            return f"游戏已结束！正确答案是 {state['target_number']}，你用了 {state['guesses']} 次猜中。"
        
        if guess is None:
            return "错误：猜测时需要提供guess参数。"
        
        try:
            guess_num = int(guess)
        except ValueError:
            return f"错误：'{guess}' 不是有效的数字。"
        
        # 更新猜测次数
        state["guesses"] += 1
        
        # 检查范围
        if guess_num < state["min_num"] or guess_num > state["max_num"]:
            return f"数字必须在 {state['min_num']} 到 {state['max_num']} 之间。"
        
        # 更新提示范围
        if guess_num < state["target_number"]:
            if guess_num > state["hint_min"]:
                state["hint_min"] = guess_num
            result = f"太小了！再试一次。 (第{state['guesses']}次猜测)"
        elif guess_num > state["target_number"]:
            if guess_num < state["hint_max"]:
                state["hint_max"] = guess_num
            result = f"太大了！再试一次。 (第{state['guesses']}次猜测)"
        else:
            state["game_over"] = True
            result = f"恭喜！你猜对了！数字是 {state['target_number']}。你用了 {state['guesses']} 次猜中。"
        
        # 保存状态
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)
            
        return result
    
    elif action == "hint":
        # 获取提示
        if "target_number" not in state:
            return "请先使用 'start' 开始新游戏。"
        
        if state["game_over"]:
            return f"游戏已结束！正确答案是 {state['target_number']}。"
        
        return f"提示：数字在 {state['hint_min']} 到 {state['hint_max']} 之间。"
    
    elif action == "status":
        # 查看状态
        if "target_number" not in state:
            return "没有进行中的游戏。使用 'start' 开始新游戏。"
        
        if state["game_over"]:
            return f"游戏已结束。正确答案：{state['target_number']}，猜测次数：{state['guesses']}"
        else:
            return f"游戏进行中。范围：{state['min_num']}-{state['max_num']}，已猜测：{state['guesses']}次"
    
    elif action == "reset":
        # 重置游戏
        if os.path.exists(state_file):
            os.remove(state_file)
        return "游戏已重置。"
    
    else:
        return f"错误：无效的操作 '{action}'。请使用 'start', 'guess', 'hint', 'status' 或 'reset'。"

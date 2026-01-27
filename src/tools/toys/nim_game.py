#!/usr/bin/env python3
"""
尼姆游戏（Nim Game）工具
支持标准尼姆和反尼姆两种模式，可自定义规则
"""

import random
from typing import Dict, Tuple, Optional, List


class NimGame:
    """尼姆游戏核心类"""
    
    def __init__(self, game_id: str = "default"):
        """初始化游戏"""
        self.game_id = game_id
        self.reset()
    
    def reset(self, 
              total_balls: int = 15, 
              min_take: int = 1, 
              max_take: int = 3, 
              misere: bool = True,
              vs_ai: bool = True,
              ai_difficulty: str = "normal") -> str:
        """
        重置游戏状态
        
        Args:
            total_balls: 初始小球总数
            min_take: 每次最少取球数
            max_take: 每次最多取球数
            misere: True=反尼姆（取最后一个输），False=标准尼姆（取最后一个赢）
            vs_ai: True=人机对战，False=双人对战
            ai_difficulty: AI难度（easy, normal, hard）
        """
        self.total_balls = total_balls
        self.remaining_balls = total_balls
        self.min_take = min_take
        self.max_take = max_take
        self.misere = misere
        self.vs_ai = vs_ai
        self.ai_difficulty = ai_difficulty
        self.current_player = 1  # 玩家1先手
        self.game_over = False
        self.winner = None
        self.history = []
        
        # 验证参数
        if min_take < 1:
            raise ValueError("最小取球数必须至少为1")
        if max_take < min_take:
            raise ValueError("最大取球数必须大于等于最小取球数")
        if total_balls < 1:
            raise ValueError("小球总数必须至少为1")
        
        return f"游戏已重置！初始有{total_balls}个小球，每次可以取{min_take}-{max_take}个。\n" \
               f"模式：{'反尼姆（取最后一个输）' if misere else '标准尼姆（取最后一个赢）'}。\n" \
               f"对战：{'人机对战' if vs_ai else '双人对战'}。\n" \
               f"当前玩家：玩家{self.current_player}。"
    
    def take_balls(self, num_balls: int) -> str:
        """
        玩家取球
        
        Args:
            num_balls: 要取的球数
        """
        if self.game_over:
            return "游戏已结束！请使用reset开始新游戏。"
        
        # 验证取球数量
        if num_balls < self.min_take or num_balls > self.max_take:
            return f"取球数量必须在{self.min_take}到{self.max_take}之间！"
        
        if num_balls > self.remaining_balls:
            return f"剩余球数不足！当前只剩{self.remaining_balls}个球。"
        
        # 执行取球
        self.remaining_balls -= num_balls
        player_name = f"玩家{self.current_player}"
        self.history.append((self.current_player, num_balls, self.remaining_balls))
        
        result = f"{player_name}取走了{num_balls}个球，剩余{self.remaining_balls}个球。"
        
        # 检查游戏是否结束
        if self.remaining_balls == 0:
            self.game_over = True
            if self.misere:
                # 反尼姆：取最后一个球的玩家输
                self.winner = 2 if self.current_player == 1 else 1
                result += f"\n游戏结束！{player_name}取走了最后一个球，玩家{self.winner}获胜！"
            else:
                # 标准尼姆：取最后一个球的玩家赢
                self.winner = self.current_player
                result += f"\n游戏结束！{player_name}取走了最后一个球，获胜！"
        else:
            # 切换玩家
            self.current_player = 2 if self.current_player == 1 else 1
            result += f"\n轮到玩家{self.current_player}。"
            
            # 如果是人机对战且轮到AI（玩家2），自动执行AI回合
            if self.vs_ai and self.current_player == 2 and not self.game_over:
                result += "\n" + self.ai_turn()
        
        return result
    
    def ai_turn(self) -> str:
        """AI取球"""
        if self.game_over:
            return "游戏已结束！"
        
        if self.ai_difficulty == "easy":
            # 简单AI：随机取球
            max_possible = min(self.max_take, self.remaining_balls)
            num_balls = random.randint(self.min_take, max_possible)
        elif self.ai_difficulty == "hard":
            # 困难AI：使用必胜策略
            num_balls = self._calculate_winning_move()
            if num_balls == 0:
                # 没有必胜策略，随机取
                max_possible = min(self.max_take, self.remaining_balls)
                num_balls = random.randint(self.min_take, max_possible)
        else:
            # 普通AI：70%使用策略，30%随机
            if random.random() < 0.7:
                num_balls = self._calculate_winning_move()
                if num_balls == 0:
                    max_possible = min(self.max_take, self.remaining_balls)
                    num_balls = random.randint(self.min_take, max_possible)
            else:
                max_possible = min(self.max_take, self.remaining_balls)
                num_balls = random.randint(self.min_take, max_possible)
        
        return self.take_balls(num_balls)
    
    def _calculate_winning_move(self) -> int:
        """计算必胜策略的取球数（返回0表示没有必胜策略）"""
        # 尼姆游戏的必胜策略：使剩余球数模(max_take+1)等于0
        target_mod = (self.max_take + 1)
        remainder = self.remaining_balls % target_mod
        
        if remainder == 0:
            # 已经处于不利位置，没有必胜策略
            return 0
        else:
            # 计算应该取多少球使剩余球数模(target_mod)等于0
            move = remainder
            if move < self.min_take:
                # 如果计算出的取球数小于最小限制，尝试其他策略
                move = self.min_take
            
            # 确保不超过最大限制和剩余球数
            move = min(move, self.max_take, self.remaining_balls)
            
            # 验证取球后不会立即输
            if self.remaining_balls - move == 0 and self.misere:
                # 反尼姆中取最后一个会输，避免这种情况
                # 尝试其他取法
                for test_move in range(self.min_take, min(self.max_take, self.remaining_balls) + 1):
                    if self.remaining_balls - test_move > 0:
                        return test_move
                return 0  # 没有安全的选择
            
            return move
    
    def get_status(self) -> str:
        """获取游戏状态"""
        status = f"游戏ID: {self.game_id}\n"
        status += f"剩余球数: {self.remaining_balls}/{self.total_balls}\n"
        status += f"当前玩家: 玩家{self.current_player}\n"
        status += f"取球范围: {self.min_take}-{self.max_take}\n"
        status += f"游戏模式: {'反尼姆（取最后一个输）' if self.misere else '标准尼姆（取最后一个赢）'}\n"
        status += f"对战模式: {'人机对战' if self.vs_ai else '双人对战'}\n"
        status += f"AI难度: {self.ai_difficulty}\n"
        status += f"游戏状态: {'已结束' if self.game_over else '进行中'}\n"
        
        if self.game_over and self.winner:
            status += f"获胜者: 玩家{self.winner}"
        
        if self.history:
            status += "\n\n取球历史:\n"
            for i, (player, taken, remaining) in enumerate(self.history, 1):
                status += f"  回合{i}: 玩家{player}取{taken}球，剩余{remaining}球\n"
        
        return status
    
    def get_board(self) -> str:
        """显示当前棋盘（球的状态）"""
        if self.remaining_balls == 0:
            return "所有球已被取完！"
        
        # 用emoji表示球
        balls_display = "⚫" * self.remaining_balls
        return f"剩余球数: {self.remaining_balls}\n{balls_display}"
    
    def get_hint(self) -> str:
        """获取策略提示"""
        if self.game_over:
            return "游戏已结束！"
        
        winning_move = self._calculate_winning_move()
        if winning_move > 0:
            return f"策略提示: 取{winning_move}个球可以占据有利位置！"
        else:
            return "策略提示: 当前没有必胜策略，尽量随机取球迷惑对手。"


# 游戏管理器，支持多个独立游戏实例
_game_instances: Dict[str, NimGame] = {}


def _get_game(game_id: str = "default") -> NimGame:
    """获取或创建游戏实例"""
    if game_id not in _game_instances:
        _game_instances[game_id] = NimGame(game_id)
    return _game_instances[game_id]


def nim_game(
    action: str,
    num_balls: Optional[int] = None,
    total_balls: int = 15,
    min_take: int = 1,
    max_take: int = 3,
    misere: bool = True,
    vs_ai: bool = True,
    ai_difficulty: str = "normal",
    game_id: str = "default"
) -> str:
    """
    尼姆游戏主函数
    
    Args:
        action: 操作类型
            "start" - 开始新游戏
            "reset" - 重置游戏
            "take" - 取球
            "ai_turn" - AI回合
            "status" - 游戏状态
            "board" - 显示棋盘
            "hint" - 策略提示
            "settings" - 显示游戏设置
        num_balls: 取球数量（当action为"take"时必需）
        total_balls: 初始球数（start/reset时使用）
        min_take: 最小取球数
        max_take: 最大取球数
        misere: True=反尼姆（取最后一个输），False=标准尼姆（取最后一个赢）
        vs_ai: True=人机对战，False=双人对战
        ai_difficulty: AI难度（easy, normal, hard）
        game_id: 游戏ID，允许多个独立游戏
    """
    try:
        game = _get_game(game_id)
        
        if action == "start" or action == "reset":
            return game.reset(total_balls, min_take, max_take, misere, vs_ai, ai_difficulty)
        
        elif action == "take":
            if num_balls is None:
                return "请指定取球数量！使用方式：nim_game('take', num_balls=2)"
            return game.take_balls(num_balls)
        
        elif action == "ai_turn":
            return game.ai_turn()
        
        elif action == "status":
            return game.get_status()
        
        elif action == "board":
            return game.get_board()
        
        elif action == "hint":
            return game.get_hint()
        
        elif action == "settings":
            return f"当前游戏设置:\n" \
                   f"  游戏ID: {game_id}\n" \
                   f"  初始球数: {total_balls}\n" \
                   f"  取球范围: {min_take}-{max_take}\n" \
                   f"  模式: {'反尼姆（取最后一个输）' if misere else '标准尼姆（取最后一个赢）'}\n" \
                   f"  对战: {'人机对战' if vs_ai else '双人对战'}\n" \
                   f"  AI难度: {ai_difficulty}"
        
        else:
            return f"未知操作: {action}。可用操作: start, reset, take, ai_turn, status, board, hint, settings"
    
    except Exception as e:
        return f"游戏出错: {str(e)}"


if __name__ == "__main__":
    # 测试代码
    print("=== 尼姆游戏测试 ===")
    print(nim_game("start"))
    print(nim_game("status"))
    print(nim_game("take", num_balls=2))
    print(nim_game("board"))
    print(nim_game("hint"))
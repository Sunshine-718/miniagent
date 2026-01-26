import json
import os
import random
from typing import Dict, List, Optional, Tuple


class TicTacToe:
    """井字棋游戏类，支持AI对战和玩家类型设置"""
    
    def __init__(self, x_player_type: str = "human", o_player_type: str = "ai"):
        self.board = [' '] * 9
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.move_history = []
        
        self.player_types = {
            'X': x_player_type.lower(),
            'O': o_player_type.lower()
        }
        
        for player, ptype in self.player_types.items():
            if ptype not in ["human", "ai"]:
                raise ValueError(f"玩家{player}的类型必须是'human'或'ai'")
    
    def get_available_moves(self) -> List[int]:
        return [i for i, cell in enumerate(self.board) if cell == ' ']
    
    def make_move(self, position: int) -> bool:
        if position < 0 or position > 8:
            return False
        
        if self.board[position] != ' ':
            return False
        
        if self.game_over:
            return False
        
        self.board[position] = self.current_player
        self.move_history.append((self.current_player, position))
        
        self.check_game_over()
        
        if not self.game_over:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        
        return True
    
    def check_game_over(self):
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in winning_lines:
            a, b, c = line
            if self.board[a] != ' ' and self.board[a] == self.board[b] == self.board[c]:
                self.game_over = True
                self.winner = self.board[a]
                return
        
        if ' ' not in self.board:
            self.game_over = True
            self.winner = 'Draw'
    
    def evaluate_board(self) -> int:
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in winning_lines:
            a, b, c = line
            if self.board[a] == 'X' and self.board[b] == 'X' and self.board[c] == 'X':
                return 10
            if self.board[a] == 'O' and self.board[b] == 'O' and self.board[c] == 'O':
                return -10
        
        return 0
    
    def negamax(self, depth, player, alpha=-float('inf'), beta=float('inf')):
        score = self.evaluate_board()
        if score != 0 or depth == 0 or not self.get_available_moves():
            return score * (1 if player == 'X' else -1)
        
        best_value = -float('inf')
        
        for move in self.get_available_moves():
            self.board[move] = player
            next_player = 'O' if player == 'X' else 'X'
            value = -self.negamax(depth - 1, next_player, -beta, -alpha)
            self.board[move] = ' '
            
            if value > best_value:
                best_value = value
            
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        
        return best_value
    
    def get_best_move(self, player='O'):
        available_moves = self.get_available_moves()
        
        if not available_moves:
            return None
        
        if len(available_moves) == 9:
            return random.choice([0, 2, 4, 6, 8])
        
        best_move = None
        best_value = -float('inf')
        
        for move in available_moves:
            self.board[move] = player
            next_player = 'O' if player == 'X' else 'X'
            value = -self.negamax(len(available_moves), next_player)
            self.board[move] = ' '
            
            if value > best_value:
                best_value = value
                best_move = move
            elif value == best_value and random.random() < 0.3:
                best_move = move
        
        return best_move
    
    def get_ai_move(self) -> Optional[int]:
        if self.game_over:
            return None
        
        if self.player_types[self.current_player] != "ai":
            return None
        
        return self.get_best_move(self.current_player)
    
    def play_ai_turn(self) -> Tuple[bool, Optional[int], str]:
        if self.game_over:
            return False, None, "游戏已结束"
        
        if self.player_types[self.current_player] != "ai":
            return False, None, f"当前玩家{self.current_player}不是AI"
        
        move = self.get_ai_move()
        if move is None:
            return False, None, "没有可用的走法"
        
        success = self.make_move(move)
        if not success:
            return False, None, f"AI走法失败：位置{move}"
        
        return True, move, f"AI({self.board[move]})在位置{move}下棋"
    
    def print_board(self) -> str:
        """打印当前棋盘"""
        board_str = ""
        for i in range(3):
            row = self.board[i*3:(i+1)*3]
            row_display = [cell if cell != ' ' else ' ' for cell in row]
            board_str += " " + " | ".join(row_display) + " \n"
            if i < 2:
                board_str += "---+---+---\n"
        return board_str
    
    def get_board_positions(self) -> str:
        """返回带位置编号的棋盘，方便用户选择"""
        board_str = "棋盘位置：\n"
        for i in range(3):
            positions = [str(i*3 + j) for j in range(3)]
            row = self.board[i*3:(i+1)*3]
            row_display = [cell if cell != ' ' else positions[j] for j, cell in enumerate(row)]
            board_str += " " + " | ".join(row_display) + " \n"
            if i < 2:
                board_str += "---+---+---\n"
        return board_str
    
    def get_game_state(self) -> Dict:
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_history': self.move_history,
            'player_types': self.player_types
        }
    
    def load_game_state(self, state: Dict):
        self.board = state.get('board', [' ']*9)
        self.current_player = state.get('current_player', 'X')
        self.game_over = state.get('game_over', False)
        self.winner = state.get('winner', None)
        self.move_history = state.get('move_history', [])
        self.player_types = state.get('player_types', {'X': 'human', 'O': 'ai'})


def tic_tac_toe_game(action: str = "start", 
                     position: int = None,
                     x_player_type: str = "human",
                     o_player_type: str = "ai",
                     game_id: str = "default",
                     show_positions: bool = True) -> str:
    """
    井字棋游戏（兼容原始API）
    
    参数:
        action: 操作类型
            "start" - 开始新游戏
            "move" - 下棋（人类玩家）
            "ai_move" - AI下棋（兼容原始API）
            "ai_turn" - AI下棋（增强版API）
            "auto_turn" - 自动执行当前玩家的回合
            "status" - 查看游戏状态
            "board" - 查看棋盘
            "reset" - 重置游戏
            "settings" - 查看游戏设置
        position: 下棋位置（0-8），当action为"move"时必需
        game_id: 游戏ID，允许多个独立游戏，默认"default"
        show_positions: 是否显示位置编号，默认True
        
    返回:
        游戏状态字符串
    """
    # 游戏状态文件路径（使用原始文件名保持兼容）
    state_dir = "storage/game_states"
    os.makedirs(state_dir, exist_ok=True)
    state_file = os.path.join(state_dir, f"tic_tac_toe_{game_id}.json")
    
    # 加载或初始化游戏
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 恢复游戏状态
            game = TicTacToe(
                x_player_type=state_data.get('player_types', {}).get('X', x_player_type),
                o_player_type=state_data.get('player_types', {}).get('O', o_player_type)
            )
            game.load_game_state(state_data)
        except:
            game = TicTacToe(x_player_type=x_player_type, o_player_type=o_player_type)
    else:
        game = TicTacToe(x_player_type=x_player_type, o_player_type=o_player_type)
    
    # 处理ai_move动作（兼容原始API）
    if action == "ai_move":
        action = "ai_turn"
    
    if action == "start":
        # 开始新游戏
        game = TicTacToe(x_player_type=x_player_type, o_player_type=o_player_type)
        
        # 保存状态
        state_data = game.get_game_state()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False)
        
        result = "井字棋游戏开始！X先手。\n"
        result += f"玩家设置: X={x_player_type}, O={o_player_type}\n"
        
        if show_positions:
            result += game.get_board_positions()
        else:
            result += game.print_board()
            
        result += "\n使用位置编号0-8下棋。"
        
        # 如果当前玩家是AI，提示可以自动下棋
        if game.player_types[game.current_player] == "ai":
            result += "\n当前玩家是AI，可以使用'ai_move'或'ai_turn'让AI下棋。"
            
        return result
    
    elif action == "settings":
        # 查看游戏设置
        result = "游戏设置:\n"
        result += f"  X玩家: {game.player_types['X']}\n"
        result += f"  O玩家: {game.player_types['O']}\n"
        result += f"  当前玩家: {game.current_player}\n"
        
        if game.game_over:
            result += "  游戏状态: 已结束"
            if game.winner:
                if game.winner == 'Draw':
                    result += " (平局)"
                else:
                    result += f" ({game.winner}获胜)"
        else:
            result += "  游戏状态: 进行中"
            
        return result
    
    elif action == "board":
        # 查看棋盘
        if show_positions:
            return game.get_board_positions()
        else:
            return game.print_board()
    
    elif action == "status":
        # 查看游戏状态
        if game.game_over:
            if game.winner == 'Draw':
                result = "游戏结束：平局！"
            else:
                result = f"游戏结束：{game.winner}获胜！"
            
            # 显示移动历史
            if game.move_history:
                result += "\n移动历史："
                for i, (player, pos) in enumerate(game.move_history, 1):
                    result += f"\n{i}. {player}在位置{pos}"
        else:
            player_type = game.player_types[game.current_player]
            result = f"游戏进行中，当前玩家：{game.current_player} ({player_type})"
            
        return result
    
    elif action == "move":
        # 人类玩家下棋
        if game.game_over:
            return "游戏已结束，请使用'start'开始新游戏。"
        
        if position is None:
            return "错误：请指定下棋位置（0-8）。"
        
        if position < 0 or position > 8:
            return "错误：位置必须在0-8之间。"
        
        if game.player_types[game.current_player] != "human":
            return f"错误：当前玩家{game.current_player}是AI，请使用'ai_move'或'ai_turn'让AI下棋。"
        
        if not game.make_move(position):
            return "错误：该位置已被占用。请选择空位置。"
        
        state_data = game.get_game_state()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False)
        
        result = f"你在位置{position}下了{game.board[position]}\n"
        if show_positions:
            result += game.get_board_positions()
        else:
            result += game.print_board()
        
        if game.game_over:
            if game.winner == 'Draw':
                result += "\n游戏结束：平局！"
            else:
                result += f"\n游戏结束：{game.winner}获胜！"
        
        return result
    
    elif action == "ai_turn":
        if game.game_over:
            return "游戏已结束，请使用'start'开始新游戏。"
        
        success, move, message = game.play_ai_turn()
        
        if not success:
            return message
        
        state_data = game.get_game_state()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False)
        
        result = f"{message}\n"
        if show_positions:
            result += game.get_board_positions()
        else:
            result += game.print_board()
        
        if game.game_over:
            if game.winner == 'Draw':
                result += "\n游戏结束：平局！"
            else:
                result += f"\n游戏结束：{game.winner}获胜！"
        
        return result
    
    elif action == "auto_turn":
        if game.game_over:
            return "游戏已结束，请使用'start'开始新游戏。"
        
        if game.player_types[game.current_player] == "ai":
            return tic_tac_toe_game("ai_turn", game_id=game_id, show_positions=show_positions)
        else:
            return f"当前玩家{game.current_player}是人类，请使用'move'下棋。"
    
    elif action == "reset":
        if os.path.exists(state_file):
            os.remove(state_file)
        return "游戏已重置。"
    
    else:
        return f"错误：无效的操作 '{action}'。请使用 'start', 'move', 'ai_move', 'ai_turn', 'auto_turn', 'status', 'board', 'settings' 或 'reset'。"

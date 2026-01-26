import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# ==================== 抽象基类 ====================

class Deck(ABC):
    """牌堆抽象基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.cards = self._create_deck()
    
    @abstractmethod
    def _create_deck(self) -> List[Dict[str, Any]]:
        """创建牌堆的具体实现"""
        pass
    
    @abstractmethod
    def draw(self, number_of_cards: int, with_replacement: bool = False) -> List[Dict[str, Any]]:
        """从牌堆中抽取指定数量的牌"""
        pass
    
    @abstractmethod
    def format_result(self, drawn_cards: List[Dict[str, Any]], 
                     with_replacement: bool = False) -> str:
        """格式化抽取结果"""
        pass

# ==================== 具体牌堆类 ====================

class StandardDeck(Deck):
    """标准扑克牌堆（52张 + 可选大小王）"""
    
    def __init__(self, include_jokers: bool = False):
        self.include_jokers = include_jokers
        deck_name = "标准扑克牌" if not include_jokers else "标准扑克牌（含大小王）"
        super().__init__(deck_name)
    
    def _create_deck(self) -> List[Dict[str, Any]]:
        suits = ["♠", "♥", "♦", "♣"]
        suit_names = {"♠": "黑桃", "♥": "红心", "♦": "方块", "♣": "梅花"}
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append({
                    "type": "standard",
                    "suit": suit,
                    "rank": rank,
                    "suit_name": suit_names[suit],
                    "display": f"{suit}{rank}"
                })
        
        if self.include_jokers:
            cards.append({"type": "joker", "suit": "🃏", "rank": "小王", "suit_name": "", "display": "🃏小王"})
            cards.append({"type": "joker", "suit": "🃏", "rank": "大王", "suit_name": "", "display": "🃏大王"})
        
        return cards
    
    def draw(self, number_of_cards: int, with_replacement: bool = False) -> List[Dict[str, Any]]:
        if not with_replacement:
            if number_of_cards > len(self.cards):
                raise ValueError(f"最多只能抽取{len(self.cards)}张牌（不放回）")
            return random.sample(self.cards, number_of_cards)
        else:
            return [random.choice(self.cards) for _ in range(number_of_cards)]
    
    def format_result(self, drawn_cards: List[Dict[str, Any]], with_replacement: bool = False) -> str:
        result = f"从{self.name}中抽取了{len(drawn_cards)}张牌"
        if with_replacement:
            result += "（放回抽取）"
        result += ":\n"
        
        for i, card in enumerate(drawn_cards, 1):
            if card["type"] == "joker":
                result += f"{i}. {card['rank']} ({card['display']})\n"
            else:
                result += f"{i}. {card['suit_name']}{card['rank']} ({card['display']})\n"
        
        return result

class TarotDeck(Deck):
    """塔罗牌堆（78张）"""
    
    def __init__(self):
        super().__init__("塔罗牌")
    
    def _create_deck(self) -> List[Dict[str, Any]]:
        suits = ["权杖", "圣杯", "宝剑", "星币"]
        court_ranks = ["侍从", "骑士", "皇后", "国王"]
        major_arcana = ["愚者", "魔术师", "女祭司", "皇后", "皇帝", "教皇", 
                       "恋人", "战车", "力量", "隐士", "命运之轮", "正义", 
                       "倒吊人", "死神", "节制", "恶魔", "塔", "星星", 
                       "月亮", "太阳", "审判", "世界"]
        
        cards = []
        for suit in suits:
            for rank in court_ranks:
                cards.append({"type": "minor_court", "suit": suit, "rank": rank, "display": f"{suit}{rank}"})
            for num in range(1, 11):
                cards.append({"type": "minor_number", "suit": suit, "rank": str(num), "display": f"{suit}{num}"})
        
        for card_name in major_arcana:
            cards.append({"type": "major", "name": card_name, "display": card_name})
        
        return cards
    
    def draw(self, number_of_cards: int, with_replacement: bool = False) -> List[Dict[str, Any]]:
        if not with_replacement:
            if number_of_cards > len(self.cards):
                raise ValueError(f"最多只能抽取{len(self.cards)}张牌（不放回）")
            return random.sample(self.cards, number_of_cards)
        else:
            return [random.choice(self.cards) for _ in range(number_of_cards)]
    
    def format_result(self, drawn_cards: List[Dict[str, Any]], with_replacement: bool = False) -> str:
        result = f"从{self.name}中抽取了{len(drawn_cards)}张牌"
        if with_replacement:
            result += "（放回抽取）"
        result += ":\n"
        
        for i, card in enumerate(drawn_cards, 1):
            if card["type"] == "major":
                result += f"{i}. 大阿卡纳：{card['name']}\n"
            elif card["type"] == "minor_court":
                result += f"{i}. 小阿卡纳（宫廷）：{card['suit']}{card['rank']}\n"
            else:
                result += f"{i}. 小阿卡纳（数字）：{card['suit']}{card['rank']}\n"
        
        return result

class UNODeck(Deck):
    """UNO牌堆（108张）"""
    
    def __init__(self):
        super().__init__("UNO牌")
    
    def _create_deck(self) -> List[Dict[str, Any]]:
        colors = ["红色", "蓝色", "绿色", "黄色"]
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        actions = ["跳过", "反转", "+2", "万能", "+4"]
        
        cards = []
        for color in colors:
            cards.append({"type": "number", "color": color, "value": "0", "display": f"{color}0"})
            for num in numbers[1:]:
                for _ in range(2):
                    cards.append({"type": "number", "color": color, "value": num, "display": f"{color}{num}"})
        
        for color in colors:
            for action in actions[:3]:
                for _ in range(2):
                    cards.append({"type": "action", "color": color, "action": action, "display": f"{color}{action}"})
        
        for action in actions[3:]:
            for _ in range(4):
                cards.append({"type": "wild", "action": action, "display": action})
        
        return cards
    
    def draw(self, number_of_cards: int, with_replacement: bool = False) -> List[Dict[str, Any]]:
        if not with_replacement:
            if number_of_cards > len(self.cards):
                raise ValueError(f"最多只能抽取{len(self.cards)}张牌（不放回）")
            return random.sample(self.cards, number_of_cards)
        else:
            return [random.choice(self.cards) for _ in range(number_of_cards)]
    
    def format_result(self, drawn_cards: List[Dict[str, Any]], with_replacement: bool = False) -> str:
        result = f"从{self.name}中抽取了{len(drawn_cards)}张牌"
        if with_replacement:
            result += "（放回抽取）"
        result += ":\n"
        
        for i, card in enumerate(drawn_cards, 1):
            if card["type"] == "number":
                result += f"{i}. {card['color']}{card['value']}\n"
            elif card["type"] == "action":
                result += f"{i}. {card['color']}{card['action']}\n"
            else:
                result += f"{i}. {card['action']}\n"
        
        return result

# ==================== 调度函数 ====================

def _create_deck(deck_type: str = "standard", include_jokers: bool = False) -> Deck:
    """
    创建指定类型的牌堆（内部函数，不对外暴露）
    
    参数:
        deck_type: 牌堆类型，可选值："standard"（标准扑克牌）、"poker"（同standard）、
                  "tarot"（塔罗牌）、"uno"（UNO牌）
        include_jokers: 是否包含大小王（仅对标准扑克牌有效）
    
    返回:
        Deck 实例
    """
    deck_creators = {
        "standard": lambda: StandardDeck(include_jokers),
        "poker": lambda: StandardDeck(include_jokers),
        "tarot": lambda: TarotDeck(),
        "uno": lambda: UNODeck()
    }
    
    if deck_type not in deck_creators:
        supported = ", ".join(deck_creators.keys())
        raise ValueError(f"不支持的牌堆类型 '{deck_type}'。支持的牌堆类型：{supported}")
    
    return deck_creators[deck_type]()

# ==================== 主函数 ====================

def draw_cards(number_of_cards: int = 1, deck_type: str = "standard", 
                 with_replacement: bool = False, include_jokers: bool = False) -> str:
    """
    从指定类型的牌堆中抽取指定数量的牌
    
    参数:
        number_of_cards: 抽牌数量，默认为1
        deck_type: 牌堆类型，可选值："standard"（标准扑克牌）、"poker"（同standard）、
                  "tarot"（塔罗牌）、"uno"（UNO牌），默认为"standard"
        with_replacement: 是否放回抽取（即抽牌后放回牌堆），默认为False（不放回）
        include_jokers: 是否包含大小王（仅对标准扑克牌有效），默认为False
    
    返回:
        格式化后的抽牌结果字符串
    
    示例:
        >>> draw_cards(3, "standard")
        "从标准扑克牌中抽取了3张牌:\n1. 红心A (♥A)\n2. 黑桃K (♠K)\n3. 方块7 (♦7)"
        
        >>> draw_cards(2, "tarot")
        "从塔罗牌中抽取了2张牌:\n1. 大阿卡纳：愚者\n2. 小阿卡纳（数字）：权杖3"
    """
    if number_of_cards < 1:
        return "错误：抽牌数量必须至少为1"
    
    try:
        deck = _create_deck(deck_type, include_jokers)
        drawn_cards = deck.draw(number_of_cards, with_replacement)
        return deck.format_result(drawn_cards, with_replacement)
    except ValueError as e:
        return f"错误：{e}"
    except Exception as e:
        return f"未知错误：{str(e)}"

import random


def roll_dices(number_of_dices: int = 1):
    """
    掷骰子
    参数：
        number_of_dices: 骰子数，默认是1
    返回：
        返回一个长度是number_of_dices的列表的字符串
    """
    number_of_dices = int(number_of_dices)
    if number_of_dices < 1:
        return f"骰子数必须大于1，你传入的数量是：{number_of_dices}"
    result = [random.randint(1, 6) for _ in range(number_of_dices)]
    return str(result)

import random


def flip_coins(number_of_coins: int = 1):
    """
    投硬币
    参数：
        number_of_coins: 硬币数，默认：1
    返回：
        返回一个长度是number_of_coins的列表的字符串，0 代表反面，1代表正面
    """
    number_of_coins = int(number_of_coins)
    if number_of_coins < 1:
        return f"硬币数必须大于1，你传入的数量是：{number_of_coins}"
    result = [random.randint(0, 1) for _ in range(number_of_coins)]
    return str(result)
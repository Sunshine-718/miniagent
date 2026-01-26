import requests
from src import config


def check_deepseek_balance():
    """
    查询deepseek API账户余额
    参数:
        无
    返回:
        账户余额
    用法:
        check_deepseek_balance()
    """
    url = "https://api.deepseek.com/user/balance"
    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {config.DEEPSEEK_API_KEY}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text

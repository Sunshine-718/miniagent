import requests


def get_weather(location: str = "") -> str:
    """
    获取指定位置的天气预报，包含气温信息。
    参数:
        location: 字符串，位置（例如 "Guangzhou" 或 "" 表示自动定位）
    返回:
        天气预报字符串，包含气温和降雨概率。
    用法:
        get_weather(location=<位置>)
    """
    try:
        base_url = "https://wttr.in/"
        if location:
            url = f"{base_url}{location}?format=j1"
        else:
            url = f"{base_url}?format=j1"

        response = requests.get(url, headers={"User-Agent": "curl"})
        response.raise_for_status()
        data = response.json()

        tomorrow_forecast = data["weather"][1]
        date = tomorrow_forecast["date"]
        hourly_forecast = tomorrow_forecast["hourly"][0]
        weather_desc = hourly_forecast["weatherDesc"][0]["value"]
        chanceofrain = hourly_forecast["chanceofrain"]
        tempC = hourly_forecast["tempC"]
        tempF = hourly_forecast["tempF"]

        result = f"明天（{date}）的天气预报：\n"
        result += f"天气状况：{weather_desc}\n"
        result += f"气温：{tempC}°C ({tempF}°F)\n"
        result += f"降雨概率：{chanceofrain}%\n"
        if int(chanceofrain) > 50:
            result += "明天很可能会下雨，建议带伞。"
        else:
            result += "明天不太可能下雨，但天气多变，请关注最新预报。"
        return result
    except Exception as e:
        return f"获取天气信息时出错：{str(e)}"
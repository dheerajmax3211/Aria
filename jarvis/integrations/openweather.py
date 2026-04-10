import requests
from loguru import logger


class OpenWeatherAPI:
    def __init__(self, api_key: str, base_url: str = "https://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url

    def get_current_weather(self, location: str, units: str = "metric") -> dict:
        try:
            url = f"{self.base_url}/weather"
            params = {"q": location, "appid": self.api_key, "units": units}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "location": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"],
            }
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return {}

    def get_forecast(self, location: str, days: int = 3, units: str = "metric") -> list[dict]:
        try:
            url = f"{self.base_url}/forecast"
            params = {"q": location, "appid": self.api_key, "units": units}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            daily = {}
            for item in data["list"]:
                date = item["dt_txt"].split(" ")[0]
                if date not in daily and len(daily) < days:
                    daily[date] = {
                        "date": date,
                        "temperature": item["main"]["temp"],
                        "description": item["weather"][0]["description"],
                        "icon": item["weather"][0]["icon"],
                    }
            return list(daily.values())
        except Exception as e:
            logger.error(f"Forecast fetch failed: {e}")
            return []

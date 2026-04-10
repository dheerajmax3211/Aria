from loguru import logger

from jarvis.config import settings
from jarvis.integrations.openweather import OpenWeatherAPI


class WeatherAgent:
    def __init__(self):
        self.api = None
        self.location = settings.user_location
        self._init()

    def _init(self):
        if settings.openweather_api_key:
            self.api = OpenWeatherAPI(settings.openweather_api_key)
            logger.info(f"Weather agent initialized for {self.location}")
        else:
            logger.warning("OpenWeather API key not set, weather agent disabled")

    def get_current(self) -> str:
        if not self.api:
            return "Weather service not configured. Add OPENWEATHER_API_KEY to .env"
        data = self.api.get_current_weather(self.location)
        if not data:
            return "Unable to fetch weather data"
        return (
            f"Currently in {data['location']}: "
            f"{data['temperature']} degrees, {data['description']}. "
            f"Humidity {data['humidity']} percent, wind {data['wind_speed']} meters per second."
        )

    def get_forecast(self, days: int = 3) -> str:
        if not self.api:
            return "Weather service not configured"
        forecast = self.api.get_forecast(self.location, days=days)
        if not forecast:
            return "Unable to fetch forecast data"
        parts = []
        for day in forecast:
            parts.append(f"{day['date']}: {day['temperature']} degrees, {day['description']}")
        return "Forecast: " + ". ".join(parts)

    def get_briefing(self) -> str:
        if not self.api:
            return ""
        current = self.api.get_current_weather(self.location)
        forecast = self.api.get_forecast(self.location, days=2)
        if not current:
            return ""
        briefing = f"In {current['location']} it's {current['temperature']} degrees, {current['description']}."
        if forecast:
            tomorrow = forecast[1] if len(forecast) > 1 else None
            if tomorrow:
                briefing += f" Tomorrow: {tomorrow['temperature']} degrees, {tomorrow['description']}."
        rain_keywords = ["rain", "storm", "thunder", "shower"]
        if any(kw in current["description"].lower() for kw in rain_keywords):
            briefing += " You might want to carry an umbrella."
        if forecast and any(kw in forecast[0].get("description", "").lower() for kw in rain_keywords):
            briefing += " Rain expected later today."
        return briefing

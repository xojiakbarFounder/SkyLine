import requests


class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def get_current_weather(self, latitude, longitude):
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,wind_direction_10m",
                "timezone": "auto"
            }

            response = requests.get(self.BASE_URL, params=params, timeout=15)

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Weather API error: {response.status_code}",
                    "data": None
                }

            data = response.json().get("current", {})

            return {
                "success": True,
                "message": "Weather loaded successfully.",
                "data": {
                    "temperature": data.get("temperature_2m"),
                    "wind_speed": data.get("wind_speed_10m"),
                    "wind_direction": data.get("wind_direction_10m")
                }
            }

        except requests.RequestException as error:
            return {
                "success": False,
                "message": str(error),
                "data": None
            }
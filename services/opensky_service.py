import requests


class OpenSkyService:
    BASE_URL = "https://opensky-network.org/api/states/all"

    def get_live_states(self, limit=20):
        try:
            headers = {
            "User-Agent": "SkyNetDSA/1.0"
}

            response = requests.get(
             self.BASE_URL,
              headers=headers,
              timeout=15
        )

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"OpenSky API error: {response.status_code}",
                    "data": []
                }

            result = response.json()
            states = result.get("states", [])

            if not states:
                return {
                    "success": False,
                    "message": "No live aircraft data received.",
                    "data": []
                }

            formatted_states = []

            for state in states[:limit]:
                formatted_states.append({
                    "icao24": state[0],
                    "callsign": state[1].strip() if state[1] else "Unknown",
                    "origin_country": state[2],
                    "longitude": state[5],
                    "latitude": state[6],
                    "baro_altitude": state[7],
                    "velocity": state[9],
                    "true_track": state[10]
                })

            return {
                "success": True,
                "message": "Live aircraft data loaded successfully.",
                "data": formatted_states
            }

        except requests.RequestException as error:
            return {
                "success": False,
                "message": f"Connection error: {error}",
                "data": []
            }
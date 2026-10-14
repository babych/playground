from .models import TemperatureResponse
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_temperature(lat: float, lon: float) -> TemperatureResponse:
    url = f"{OPEN_METEO_URL}?latitude={lat}&longitude={lon}&current=temperature_2m"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()

    return TemperatureResponse(
        latitude=lat,
        longitude=lon,
        temperature=data["current"]["temperature_2m"],
        unit=data["current_units"]["temperature_2m"]
    )

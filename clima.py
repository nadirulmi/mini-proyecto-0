# clima.py — uso: python clima.py "Buenos Aires"
import argparse
import sys
import httpx
from pydantic import BaseModel

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
CLIMA_URL = "https://api.open-meteo.com/v1/forecast"

class Lugar(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float

class Actual(BaseModel):
    temperature_2m: float
    wind_speed_10m: float

def buscar_lugar(ciudad: str) -> Lugar:
    r = httpx.get(GEO_URL, params={"name": ciudad, "count": 1, "language": "es"}, timeout=10)
    r.raise_for_status()
    resultados = r.json().get("results")
    if not resultados:
        raise ValueError(f"No encontré la ciudad '{ciudad}'")
    return Lugar.model_validate(resultados[0])

def clima_actual(lugar: Lugar) -> Actual:
    params = {
        "latitude": lugar.latitude,
        "longitude": lugar.longitude,
        "current": "temperature_2m,wind_speed_10m",
    }
    r = httpx.get(CLIMA_URL, params=params, timeout=10)
    r.raise_for_status()
    return Actual.model_validate(r.json()["current"])

def main() -> None:
    parser = argparse.ArgumentParser(description="Clima actual de una ciudad")
    parser.add_argument("ciudad")
    args = parser.parse_args()
    try:
        lugar = buscar_lugar(args.ciudad)
        actual = clima_actual(lugar)
    except ValueError as e:
        print(e)
        sys.exit(1)
    except httpx.HTTPError as e:
        print(f"Falló la conexión: {e}")
        sys.exit(2)
    print(f"{lugar.name}, {lugar.country}")
    print(f"  Temperatura: {actual.temperature_2m} °C")
    print(f"  Viento:      {actual.wind_speed_10m} km/h")

if __name__ == "__main__":
    main()
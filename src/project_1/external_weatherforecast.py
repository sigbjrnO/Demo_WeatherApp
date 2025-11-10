from typing import Optional, TypedDict, List
from dataclasses import dataclass, asdict
import aiohttp

# https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=58.50723&lon=8.62932
#  OBS: Requires this format for user_agent header: 
    # "acmeweathersite.com support@acmeweathersite.com"
    # "AcmeWeatherApp/0.9 github.com/acmeweatherapp"

@dataclass()
class WeatherData:
    time: str
    air_temperature: float
    wind_speed: float
    wind_from_direction: float

@dataclass()
class Weather:
    source_timestamp: str
    weatherSeries: List[WeatherData]


async def get_weatherforecast(latitude: float, longitude: float):
    async with aiohttp.ClientSession(headers={"User-Agent": "Project-1 https://github.com/sigbjrno"}) as session:
        async with session.get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}") as resp:
            response = await resp.json()
    
    geometry = response["geometry"]
    properties = response["properties"]

    weather = Weather(
        properties["meta"]["updated_at"],
        []
    )
    
    for timeserie in properties["timeseries"]:
        weather.weatherSeries.append(
            WeatherData(
                timeserie["time"],
                timeserie["data"]["instant"]["details"]["air_temperature"],
                timeserie["data"]["instant"]["details"]["wind_speed"],
                timeserie["data"]["instant"]["details"]["wind_from_direction"]
            )
        )

    return asdict(weather)
    # return response

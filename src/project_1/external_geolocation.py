from typing import Optional, TypedDict, List
from dataclasses import dataclass, asdict
import aiohttp

@dataclass()
class Geolocation:
    location_id: int
    fylke: "GeolocationName"
    kommune: "GeolocationName"
    latitude: float
    longitude: float
    pretty_name: str


async def get_geolocation(search_string: Optional[str] = None, 
                          kommune_name: Optional[str] = None, 
                          fylke_name: Optional[str] = None) -> List["Geolocation"]:
    
    # https://ws.geonorge.no/stedsnavn/v1/#/default/get_navn
    
    base_url = "https://api.kartverket.no/stedsnavn/v1"

    geolocations: List[Geolocation] = []

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/navn?sok={search_string}&fuzzy=true&utkoordsys=4258&treffPerSide=100&side=1") as resp:
            response = await resp.json()

            data = response["navn"]
            

            for item in data:
                location_id = item["stedsnummer"]
                fylke = {"name": item["fylker"][0]["fylkesnavn"], "number": item["fylker"][0]["fylkesnummer"]}
                kommune = {"name": item["kommuner"][0]["kommunenavn"], "number": item["kommuner"][0]["kommunenummer"]}
                lat = item["representasjonspunkt"]["nord"]
                lon = item["representasjonspunkt"]["øst"]
                pretty_name = item["skrivemåte"]

                geolocation = Geolocation(location_id, fylke, kommune, lat, lon, pretty_name)

                geolocations.append(geolocation)

    return geolocations
    

class GeolocationName(TypedDict):
    name: str
    number: str
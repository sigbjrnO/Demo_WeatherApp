import aiohttp
from aiohttp.web_request import Request
import external_geolocation
import external_weatherforecast
from typing import List
from dataclasses import asdict

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select, and_

import database_tables


routes = aiohttp.web.RouteTableDef()

@routes.get("/")
async def hello(request: Request):
    return aiohttp.web.FileResponse('index.html')

@routes.get("/weatherforecast")
async def get_weatherForecast(request: Request):
    latitude = float(request.rel_url.query.get('latitude', 0))
    longitude = float(request.rel_url.query.get('longitude', 0))
    
    resp = await external_weatherforecast.get_weatherforecast(latitude, longitude)

    return aiohttp.web.json_response(resp)

@routes.get("/location/search/{input}")
async def get_geolocation(request: Request):
    
    db_engine:AsyncEngine = request.app["db_engine"]
    
    input = request.match_info['input']

    geolocations: List[external_geolocation.Geolocation] = []

    

    async with db_engine.connect() as conn:
        
        geolocation_ids: List[int] = []
        
        cutoff = datetime.now() - timedelta(days=1)

        search = await conn.execute(select(database_tables.T_geolocation_search_mapping).where(
            and_(
                database_tables.T_geolocation_search_mapping.c.search_term == input,
                database_tables.T_geolocation_search_mapping.c.created_at > cutoff,
            )
        ))
        
        for search_row in search.mappings().all():
            geolocation_ids.extend(search_row["geolocation_ids"])


        result_geolocation = await conn.execute(select(database_tables.T_geolocation).where(database_tables.T_geolocation.c["geolocation_id"].in_(geolocation_ids)))
        
        for row in result_geolocation.mappings().all():
            geolocations.append(
                external_geolocation.Geolocation(
                    row["geolocation_id"],
                    {"name": "", "number": row["fylke_number"]},
                    {"name": "", "number": row["kommune_number"]},
                    row["latitude"],
                    row["longitude"],
                    row["name"]
                )
            )
    
    print("== DB HIT == ", len(geolocations))

    if len(geolocations) == 0:


        geolocations = await external_geolocation.get_geolocation(input)

        async with db_engine.begin() as conn:

            await conn.execute(
                insert(database_tables.T_geolocation_search_mapping).prefix_with("OR REPLACE"),
                [{
                    "search_term": input, 
                    "created_at": datetime.now(), 
                    "geolocation_ids": [geolocation.location_id for geolocation in geolocations], 
                    
                }]
            )


            await conn.execute(
                insert(database_tables.T_geolocation).prefix_with("OR REPLACE"), 
                [{
                    "geolocation_id": geolocation.location_id,
                    "name": geolocation.pretty_name, 
                    "kommune_number": geolocation.kommune["number"], 
                    "fylke_number": geolocation.fylke["number"], 
                    "latitude": geolocation.latitude, 
                    "longitude": geolocation.longitude
                    
                } for geolocation in geolocations]
            )

    data = [asdict(geolocation) for geolocation in geolocations]

    return aiohttp.web.json_response(data)
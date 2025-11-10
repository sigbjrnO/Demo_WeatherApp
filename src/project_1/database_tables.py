from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, JSON

meta = MetaData()

T_geolocation_search_mapping = Table(
    "geolocation_search_mapping",
    meta,
    Column("search_term", String(), primary_key=True, unique=True),
    Column("created_at", DateTime()),
    Column("geolocation_ids", JSON()), # [1,2,3]
)

T_geolocation = Table(
    "geolocation",
    meta,
    Column("id", Integer(), primary_key=True, unique=True),
    Column("geolocation_id", Integer(), index=True, unique=True),
    Column("name", String()),
    Column("kommune_number", String()),
    Column("fylke_number", String()),
    Column("latitude", Float()),
    Column("longitude", Float()),

)
from typing import Annotated

from fastapi import FastAPI, File, UploadFile

from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from fastapi.encoders import jsonable_encoder

from bloom.logger import logger

import json

app = FastAPI()

@app.get("/vessels")
async def read_vessels():
        with open(settings.vessel_data) as file:
            return json.load(file)

@app.get("/vessels/*/lastPosition")
async def read_vessels_last_positions():
        with open(settings.vessel_last_position_data) as file:
            return json.load(file)

@app.get("/vessels/tracks")
async def read_vessels_tracks():
        with open(settings.tracks_by_vessel_and_voyage_data) as file:
            return json.load(file)
        
@app.get("/vessels/tracks/by-mmsi/{mmsi}")
async def read_vessels_tracks(mmsi:int):
        with open(settings.tracks_by_vessel_and_voyage_data) as file:
            return list(filter(lambda d: d ['properties']['vessel_mmsi'] in [mmsi],json.load(file)))


@app.get("/vessels/by-mmsi/{mmsi}/lastPosition")
async def read_vessels_last_positions(mmsi:int):
        with open(settings.vessel_last_position_data) as file:
            return list(filter(lambda d: d['vessel_mmsi'] in [mmsi],json.load(file)))

@app.get("/vessels/by-mmsi/{mmsi}")
async def read_vessels_by_mmsi(mmsi: int):
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        db = use_cases.db()
        return vessel_repository.get_vessel_by_mmsi(session,mmsi)
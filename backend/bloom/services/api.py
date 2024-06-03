from fastapi import FastAPI, APIRouter
from fastapi import Request

from datetime import datetime

app = FastAPI()

@app.get("/vessels")
async def list_vessels():
    return {"vessels": ["TODO"]}

@app.get("/vessels/{vessel_id}")
async def get_vessel(vessel_id: int):
    return {"vessel": "TODO"}

@app.get("/vessels/{vessel_id}/positions")
async def list_vessel_positions(vessel_id: int, start: datetime = datetime.now(), end:datetime=None):
    return {"positions": ["TODO"]}

@app.get("/vessels/{vessel_id}/positions/last")
async def list_vessel_position_last(vessel_id: int, date:datetime = datetime.now()):
    return {"position": ["TODO"]}

@app.get("/vessels/{vessel_id}/excursions")
async def list_vessel_excursions(vessel_id: int):
    return {"excursions": ["TODO"]}


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}")
async def get_vessel_excursion(vessel_id: int,excursions_id: int):
    return {"excursion": "TODO"}


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments")
async def list_vessel_excursion_segments(vessel_id: int,excursions_id: int):
    return {"segments": ["TODO"]}

@app.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments/{segment_id}")
async def get_vessel_excursion_segment(vessel_id: int,excursions_id: int, segment_id:int):
    return {"segment": "TODO"}

@app.get("/ports")
async def list_ports():
    return {"ports": ["TODO"]}

@app.get("/ports/{port_id}")
async def get_port(port_id:int):
    return {"port": "TODO"}

@app.get("/zones")
async def list_zones():
    return {"zones": ["TODO"]}

@app.get("/zones/{zones_id}")
async def get_zone(zones_id:int):
    return {"zone": "TODO"}

@app.get("/statics/{zones}")
async def get_statics_zones():
    return {}

@app.get("/maptiles/mpa")
async def get_maptile_mpa():
    return {"data":{}}

@app.get("/maptiles/territorial")
async def get_maptile_territorial():
    return {"data":{}}

@app.get("/maptiles/coastal")
async def get_maptile_coastal():
    return {"data":{}}

@app.get("/maptiles")
async def list_maptiles(request:Request):
    return {
                "mpa":          f"{request.url_for('get_maptile_mpa')}",
                "territorial":  f"{request.url_for('get_maptile_territorial')}",
                "coastal":      f"{request.url_for('get_maptile_coastal')}",
            }

@app.get("/maptiles")
async def list_maptiles():
    return {"data":{}}

@app.get("/")
async def root(request:Request):
    return {
            "maptiles": f"{request.url_for('list_maptiles')}",
            "ports":    f"{request.url_for('list_ports')}",
            "vessels":  f"{request.url_for('list_vessels')}",
            "zones":    f"{request.url_for('list_zones')}",
            }
"""
Router para endpoints relacionados con estaciones de recarga
"""
from fastapi import APIRouter

router = APIRouter(
    prefix="/charging-stations",
    tags=["charging-stations"],
    responses={404: {"description": "Estación no encontrada"}}
)

@router.get("/")
async def get_charging_stations():
    """Obtener lista de todas las estaciones de recarga"""
    return {
        "message": "Endpoint para obtener estaciones de recarga",
        "status": "not_implemented",
        "data": []
    }

@router.get("/{station_id}")
async def get_charging_station(station_id: str):
    """Obtener información de una estación específica"""
    return {
        "message": f"Endpoint para obtener estación {station_id}",
        "status": "not_implemented",
        "station_id": station_id
    }

@router.post("/")
async def create_charging_station():
    """Crear una nueva estación de recarga"""
    return {
        "message": "Endpoint para crear estación de recarga",
        "status": "not_implemented"
    }

@router.get("/{station_id}/status")
async def get_station_status(station_id: str):
    """Obtener estado actual de una estación"""
    return {
        "message": f"Endpoint para estado de estación {station_id}",
        "status": "not_implemented",
        "station_id": station_id
    }

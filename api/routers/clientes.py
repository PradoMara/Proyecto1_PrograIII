"""
Router para endpoints relacionados con clientes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..simulation_manager import simulation_manager

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={404: {"description": "Cliente no encontrado"}}
)

@router.get("/")
async def obtener_clientes():
    """Obtener la lista completa de clientes registrados en el sistema"""
    try:
        result = simulation_manager.get_clients_data()
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener clientes: {str(e)}",
            "data": []
        }

@router.get("/{client_id}")
async def obtener_cliente(client_id: str):
    """Obtener la información detallada de un cliente específico por su ID"""
    try:
        result = simulation_manager.get_client_by_id(client_id)
        
        if result["status"] == "error" and "no encontrado" in result["message"]:
            raise HTTPException(
                status_code=404,
                detail=result
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener cliente: {str(e)}",
            "data": None
        }

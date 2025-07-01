"""
Router para endpoints relacionados con órdenes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..simulation_manager import simulation_manager

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Orden no encontrada"}}
)

@router.get("/")
async def get_orders():
    """Listar todas las órdenes registradas en el sistema"""
    try:
        result = simulation_manager.get_orders_data()
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener órdenes: {str(e)}",
            "data": []
        }

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Obtener detalle de una orden específica por su ID"""
    try:
        result = simulation_manager.get_order_by_id(order_id)
        
        if result["status"] == "error" and "no encontrada" in result["message"]:
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
            "message": f"Error al obtener orden: {str(e)}",
            "data": None
        }

@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancelar una orden específica"""
    try:
        result = simulation_manager.cancel_order(order_id)
        
        if result["status"] == "error":
            if "no encontrada" in result["message"]:
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=400, detail=result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al cancelar orden: {str(e)}",
            "success": False
        }

@router.post("/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Marcar una orden específica como completada"""
    try:
        result = simulation_manager.complete_order(order_id)
        
        if result["status"] == "error":
            if "no encontrada" in result["message"]:
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=400, detail=result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al completar orden: {str(e)}",
            "success": False
        }

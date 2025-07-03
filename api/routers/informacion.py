"""
Router para endpoints de información y reportes de visitas
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from ..simulation_manager import simulation_manager

router = APIRouter(
    prefix="/info",
    tags=["informacion"],
    responses={404: {"description": "Información no encontrada"}}
)

@router.get("/reportes/visitas/clientes")
async def obtener_ranking_clientes_visitados():
    """Obtener el ranking de clientes más visitados en las rutas de la simulación"""
    try:
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": []
            }
        
        visit_stats = simulation_manager.get_visit_statistics()
        
        if visit_stats["status"] != "success":
            return visit_stats
        
        clients_data = visit_stats["data"].get("clients", [])
        
        return {
            "status": "success",
            "message": "Ranking de clientes más visitados obtenido exitosamente",
            "data": clients_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener ranking de clientes: {str(e)}",
            "data": []
        }

@router.get("/reportes/visitas/recargas")
async def obtener_ranking_recargas_visitadas():
    """Obtener el ranking de nodos de recarga más visitados"""
    try:
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": []
            }
        
        visit_stats = simulation_manager.get_visit_statistics()
        
        if visit_stats["status"] != "success":
            return visit_stats
        
        recharges_data = visit_stats["data"].get("recharges", [])
        
        return {
            "status": "success",
            "message": "Ranking de nodos de recarga más visitados obtenido exitosamente",
            "data": recharges_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener ranking de recargas: {str(e)}",
            "data": []
        }

@router.get("/reportes/visitas/almacenes")
async def obtener_ranking_almacenes_visitados():
    """Obtener el ranking de nodos de almacenamiento más visitados"""
    try:
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": []
            }
        
        visit_stats = simulation_manager.get_visit_statistics()
        
        if visit_stats["status"] != "success":
            return visit_stats
        
        storages_data = visit_stats["data"].get("storages", [])
        
        return {
            "status": "success",
            "message": "Ranking de nodos de almacenamiento más visitados obtenido exitosamente",
            "data": storages_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener ranking de almacenes: {str(e)}",
            "data": []
        }

@router.get("/reportes/resumen")
async def obtener_resumen_simulacion():
    """Obtener un resumen general de la simulación activa"""
    try:
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": {}
            }
        
        summary = simulation_manager.get_simulation_summary()
        return summary
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener resumen de simulación: {str(e)}",
            "data": {}
        }

@router.post("/detener-simulacion")
async def detener_simulacion():
    """Finaliza la simulación activa"""
    try:
        result = simulation_manager.stop_simulation()
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al detener simulación: {str(e)}",
            "success": False
        }

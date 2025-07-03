"""
Router para endpoints relacionados con reportes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import io
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from api.simulation_manager import simulation_manager

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Reporte no encontrado"}}
)

@router.get("/pdf")
async def generate_pdf_report():
    """Generar y obtener el informe PDF resumen del sistema y las órdenes"""
    try:
        # Verificar si la simulación está activa
        if not simulation_manager.is_simulation_running():
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Simulación no iniciada - No se puede generar reporte",
                    "data": None
                }
            )
        
        # Importar la utilidad de PDF
        try:
            from utils.pdf_report import generate_pdf_report
        except ImportError as e:
            print(f"Error importing PDF utility: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "Error al importar utilidad de PDF",
                    "data": None
                }
            )
        
        # Obtener datos de la simulación para el reporte
        clients_data = simulation_manager.get_clients_data()
        orders_data = simulation_manager.get_orders_data()
        visit_stats = simulation_manager.get_visit_statistics()
        summary = simulation_manager.get_simulation_summary()
        
        if clients_data["status"] != "success" or orders_data["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "Error al obtener datos de la simulación",
                    "data": None
                }
            )
        
        # Preparar datos para el reporte
        simulation_data = {
            'clients': clients_data["data"],
            'orders': orders_data["data"],
            'visit_statistics': visit_stats.get("data", {}),
            'summary': summary.get("data", {})
        }
        
        # Generar PDF
        pdf_buffer = generate_pdf_report(simulation_data)
        
        # Configurar nombre del archivo
        filename = f"reporte_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Retornar como streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Error al generar reporte: {str(e)}",
                "data": None
            }
        )

@router.get("/pdf/preview")
async def preview_pdf_report():
    """Obtener información previa del reporte PDF sin generarlo"""
    try:
        # Verificar si la simulación está activa
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada - No se puede generar reporte",
                "data": None
            }
        
        # Obtener estadísticas básicas para preview
        clients_data = simulation_manager.get_clients_data()
        orders_data = simulation_manager.get_orders_data()
        visit_stats = simulation_manager.get_visit_statistics()
        summary = simulation_manager.get_simulation_summary()
        
        if clients_data["status"] != "success" or orders_data["status"] != "success":
            return {
                "status": "error",
                "message": "Error al obtener datos de la simulación",
                "data": None
            }
        
        # Calcular estadísticas del reporte
        total_clients = len(clients_data["data"])
        total_orders = len(orders_data["data"])
        
        visit_data = visit_stats.get("data", {})
        clients_visits = len(visit_data.get("clients", []))
        recharges_visits = len(visit_data.get("recharges", []))
        storages_visits = len(visit_data.get("storages", []))
        
        network_stats = summary.get("data", {}).get("network_stats", {})
        
        return {
            "status": "success",
            "message": "Preview del reporte PDF generado exitosamente",
            "data": {
                "report_info": {
                    "generation_date": datetime.now().isoformat(),
                    "filename_pattern": f"reporte_simulacion_YYYYMMDD_HHMMSS.pdf"
                },
                "content_summary": {
                    "clients_table": {
                        "total_clients": total_clients,
                        "description": "Tabla con ID, nombre, tipo y total de órdenes de cada cliente"
                    },
                    "orders_table": {
                        "total_orders": total_orders,
                        "description": "Tabla con origen, destino, estado, prioridad, fechas y costos"
                    },
                    "charts": {
                        "node_distribution": {
                            "type": "pie_chart",
                            "description": "Distribución de nodos por tipo",
                            "data_available": bool(network_stats)
                        },
                        "client_visits": {
                            "type": "bar_chart",
                            "description": "Clientes más visitados",
                            "data_points": clients_visits
                        },
                        "recharge_visits": {
                            "type": "bar_chart", 
                            "description": "Estaciones de recarga más visitadas",
                            "data_points": recharges_visits
                        },
                        "storage_visits": {
                            "type": "bar_chart",
                            "description": "Nodos de almacenamiento más visitados", 
                            "data_points": storages_visits
                        }
                    }
                },
                "network_summary": network_stats
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al generar preview: {str(e)}",
            "data": None
        }

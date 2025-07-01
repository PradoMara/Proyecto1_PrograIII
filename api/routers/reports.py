"""
Router para endpoints relacionados con reportes
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
import io
from datetime import datetime
from ..simulation_manager import simulation_manager

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Reporte no encontrado"}}
)

@router.get("/reports/pdf")
async def generate_pdf_report():
    """Generar y obtener el informe PDF resumen del sistema y las órdenes"""
    try:
        # Verificar si la simulación está activa
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada - No se puede generar reporte",
                "data": None
            }
        
        # Obtener datos de la simulación para el reporte
        summary = simulation_manager.get_simulation_summary()
        
        if summary["status"] != "success":
            return summary
        
        # Simulación de generación de PDF con datos reales
        return {
            "status": "simulated",
            "message": "Generación de PDF simulada con datos de la simulación activa",
            "data": {
                "report_type": "simulation_summary_pdf",
                "generated_at": datetime.now().isoformat(),
                "simulation_data": summary["data"],
                "note": "En implementación real retornaría FileResponse con PDF"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al generar reporte: {str(e)}",
            "data": None
        }

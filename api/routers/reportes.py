"""
Router para endpoints relacionados con reportes
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
import io
import os
import tempfile
from datetime import datetime
from ..simulation_manager import simulation_manager

router = APIRouter(
    prefix="/reportes",
    tags=["reportes"],
    responses={404: {"description": "Reporte no encontrado"}}
)

@router.get("/pdf")
async def generar_reporte_pdf():
    """Generar y obtener el informe PDF resumen del sistema y las órdenes"""
    try:
        # Verificar si la simulación está activa
        if not simulation_manager.is_simulation_running():
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Simulación no iniciada - No se puede generar reporte",
                    "data": None
                }
            )
        
        # Obtener datos de la simulación para el reporte
        summary = simulation_manager.get_simulation_summary()
        
        if summary["status"] != "success":
            return JSONResponse(
                status_code=500,
                content=summary
            )
        
        # Intentar generar PDF real usando la librería utils.pdf_report
        try:
            from utils.pdf_report import generate_pdf_report
            
            # Crear archivo temporal para el PDF
            temp_dir = tempfile.mkdtemp()
            pdf_filename = f"reporte_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            # Generar PDF con datos reales
            generate_pdf_report(
                simulation_data=summary["data"],
                output_path=pdf_path
            )
            
            # Verificar que el archivo se creó
            if os.path.exists(pdf_path):
                return FileResponse(
                    path=pdf_path,
                    media_type="application/pdf",
                    filename=pdf_filename,
                    headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
                )
            else:
                raise FileNotFoundError("No se pudo generar el archivo PDF")
                
        except ImportError:
            # Si no está disponible la librería PDF, devolver datos estructurados
            return JSONResponse(
                status_code=200,
                content={
                    "status": "partial_success",
                    "message": "Reporte generado en formato JSON (PDF no disponible)",
                    "data": {
                        "report_type": "resumen_simulacion_json",
                        "generated_at": datetime.now().isoformat(),
                        "simulation_data": summary["data"],
                        "note": "Para generar PDF instalar: pip install reportlab"
                    }
                }
            )
        except Exception as pdf_error:
            # Si hay error generando PDF, devolver datos estructurados
            return JSONResponse(
                status_code=200,
                content={
                    "status": "partial_success",
                    "message": f"Error generando PDF, datos en JSON: {str(pdf_error)}",
                    "data": {
                        "report_type": "resumen_simulacion_json",
                        "generated_at": datetime.now().isoformat(),
                        "simulation_data": summary["data"],
                        "error": str(pdf_error)
                    }
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error al generar reporte: {str(e)}",
                "data": None
            }
        )

@router.get("/datos")
async def obtener_datos_reporte():
    """Obtener datos del reporte en formato JSON"""
    try:
        # Verificar si la simulación está activa
        if not simulation_manager.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": None
            }
        
        # Obtener resumen de la simulación
        summary = simulation_manager.get_simulation_summary()
        if summary["status"] != "success":
            return summary
        
        # Obtener datos adicionales para el reporte
        clients_data = simulation_manager.get_clients_data()
        orders_data = simulation_manager.get_orders_data()
        visit_stats = simulation_manager.get_visit_statistics()
        
        return {
            "status": "success",
            "message": "Datos del reporte obtenidos exitosamente",
            "data": {
                "generated_at": datetime.now().isoformat(),
                "summary": summary["data"],
                "clients": clients_data["data"] if clients_data["status"] == "success" else [],
                "orders": orders_data["data"] if orders_data["status"] == "success" else [],
                "visit_statistics": visit_stats["data"] if visit_stats["status"] == "success" else {},
                "totals": {
                    "total_clients": len(clients_data["data"]) if clients_data["status"] == "success" else 0,
                    "total_orders": len(orders_data["data"]) if orders_data["status"] == "success" else 0,
                    "orders_by_status": _get_orders_by_status(orders_data["data"]) if orders_data["status"] == "success" else {}
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener datos del reporte: {str(e)}",
            "data": None
        }

def _get_orders_by_status(orders: list) -> dict:
    """Agrupa órdenes por estado"""
    status_count = {}
    for order in orders:
        status = order.get("Status", "Desconocido")
        status_count[status] = status_count.get(status, 0) + 1
    return status_count

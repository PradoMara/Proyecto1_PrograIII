"""
Router para endpoints relacionados con clientes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Cliente no encontrado"}}
)

@router.get("/")
async def get_clients():
    """Obtener la lista completa de clientes registrados en el sistema"""
    return {
        "message": "Lista de clientes obtenida exitosamente",
        "status": "success",
        "data": [
            {
                "client_id": "CLI001",
                "name": "Juan Pérez",
                "email": "juan.perez@email.com",
                "phone": "+56912345678",
                "address": "Av. Principal 123, Santiago",
                "status": "active"
            },
            {
                "client_id": "CLI002", 
                "name": "María González",
                "email": "maria.gonzalez@email.com",
                "phone": "+56987654321",
                "address": "Calle Secundaria 456, Valparaíso",
                "status": "active"
            }
        ],
        "total": 2
    }

@router.get("/{client_id}")
async def get_client(client_id: str):
    """Obtener la información detallada de un cliente específico por su ID"""
    
    # Simulación de búsqueda de cliente
    if client_id == "CLI001":
        return {
            "message": "Cliente encontrado exitosamente",
            "status": "success",
            "data": {
                "client_id": "CLI001",
                "name": "Juan Pérez",
                "email": "juan.perez@email.com",
                "phone": "+56912345678",
                "address": "Av. Principal 123, Santiago",
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "total_orders": 15,
                "last_order": "2024-12-01T14:22:00Z"
            }
        }
    
    # Cliente no encontrado
    raise HTTPException(
        status_code=404,
        detail={
            "message": f"Cliente con ID {client_id} no encontrado",
            "status": "error",
            "client_id": client_id
        }
    )

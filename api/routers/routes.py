"""
Router para endpoints relacionados con órdenes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Orden no encontrada"}}
)

@router.get("/")
async def get_orders():
    """Listar todas las órdenes registradas en el sistema"""
    return {
        "message": "Lista de órdenes obtenida exitosamente",
        "status": "success",
        "data": [
            {
                "order_id": "ORD001",
                "client_id": "CLI001",
                "client_name": "Juan Pérez",
                "status": "pending",
                "created_at": "2024-12-01T10:30:00Z",
                "delivery_address": "Av. Principal 123, Santiago",
                "items": [
                    {"name": "Producto A", "quantity": 2, "weight": 1.5}
                ],
                "total_weight": 1.5,
                "priority": "normal"
            },
            {
                "order_id": "ORD002",
                "client_id": "CLI002",
                "client_name": "María González",
                "status": "in_progress",
                "created_at": "2024-12-01T11:15:00Z",
                "delivery_address": "Calle Secundaria 456, Valparaíso",
                "items": [
                    {"name": "Producto B", "quantity": 1, "weight": 2.0}
                ],
                "total_weight": 2.0,
                "priority": "high"
            }
        ],
        "total": 2,
        "summary": {
            "pending": 1,
            "in_progress": 1,
            "completed": 0,
            "cancelled": 0
        }
    }

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Obtener detalle de una orden específica por su ID"""
    
    # Simulación de búsqueda de orden
    if order_id == "ORD001":
        return {
            "message": "Orden encontrada exitosamente",
            "status": "success",
            "data": {
                "order_id": "ORD001",
                "client_id": "CLI001",
                "client_name": "Juan Pérez",
                "client_email": "juan.perez@email.com",
                "client_phone": "+56912345678",
                "status": "pending",
                "created_at": "2024-12-01T10:30:00Z",
                "updated_at": "2024-12-01T10:30:00Z",
                "delivery_address": "Av. Principal 123, Santiago",
                "items": [
                    {
                        "item_id": "ITM001",
                        "name": "Producto A",
                        "description": "Descripción del producto A",
                        "quantity": 2,
                        "weight": 1.5,
                        "dimensions": {"length": 10, "width": 8, "height": 5}
                    }
                ],
                "total_weight": 1.5,
                "priority": "normal",
                "estimated_delivery": "2024-12-01T16:00:00Z",
                "tracking_history": [
                    {
                        "timestamp": "2024-12-01T10:30:00Z",
                        "status": "created",
                        "description": "Orden creada exitosamente"
                    }
                ]
            }
        }
    
    # Orden no encontrada
    raise HTTPException(
        status_code=404,
        detail={
            "message": f"Orden con ID {order_id} no encontrada",
            "status": "error",
            "order_id": order_id
        }
    )

@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancelar una orden específica"""
    
    # Simulación de validación de orden
    if order_id == "ORD001":
        return {
            "message": "Orden cancelada exitosamente",
            "status": "success",
            "data": {
                "order_id": order_id,
                "previous_status": "pending",
                "new_status": "cancelled",
                "cancelled_at": "2024-12-01T15:30:00Z",
                "cancellation_reason": "Cancelación solicitada por API"
            }
        }
    elif order_id == "ORD002":
        # Orden no cancelable
        raise HTTPException(
            status_code=400,
            detail={
                "message": "La orden no puede ser cancelada en su estado actual",
                "status": "error",
                "order_id": order_id,
                "current_status": "in_progress",
                "reason": "La orden ya está en progreso y no puede cancelarse"
            }
        )
    
    # Orden no encontrada
    raise HTTPException(
        status_code=404,
        detail={
            "message": f"Orden con ID {order_id} no encontrada",
            "status": "error",
            "order_id": order_id
        }
    )

@router.post("/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Marcar una orden específica como completada"""
    
    # Simulación de validación de orden
    if order_id == "ORD002":
        return {
            "message": "Orden completada exitosamente",
            "status": "success",
            "data": {
                "order_id": order_id,
                "previous_status": "in_progress",
                "new_status": "completed",
                "completed_at": "2024-12-01T16:45:00Z",
                "delivery_confirmation": {
                    "delivered_by": "DRONE-001",
                    "delivery_time": "2024-12-01T16:45:00Z",
                    "recipient_signature": "digital_signature_hash"
                }
            }
        }
    elif order_id == "ORD001":
        # Orden no completable
        raise HTTPException(
            status_code=400,
            detail={
                "message": "La orden no puede ser completada en su estado actual",
                "status": "error",
                "order_id": order_id,
                "current_status": "pending",
                "reason": "La orden debe estar en progreso para poder completarse"
            }
        )
    
    # Orden no encontrada
    raise HTTPException(
        status_code=404,
        detail={
            "message": f"Orden con ID {order_id} no encontrada",
            "status": "error",
            "order_id": order_id
        }
    )

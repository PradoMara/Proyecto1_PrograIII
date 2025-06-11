"""
Entidades del dominio (negocio) - Clase Order

Define la estructura y comportamiento de las órdenes/pedidos en el sistema de grafos conectados.
"""

from datetime import datetime
from typing import Optional
import uuid


class Orden:
    """
    Representa una orden/pedido en el sistema de grafos conectados.
    
    Una orden conecta un cliente con nodos de origen y destino.
    """
    
    def __init__(
        self,
        order_id: str = None,
        client: str = "",
        client_id: str = "",
        origin: str = "",
        destination: str = "",
        priority: str = "normal"
    ):
        """
        Inicializa una nueva orden.
        
        Args:
            order_id: Identificador único de la orden
            client: Nombre del cliente que realizó la orden
            client_id: ID del cliente que realizó la orden
            origin: Nodo de origen
            destination: Nodo de destino
            priority: Prioridad de la orden (low, normal, high, critical)
        """
        self.order_id = order_id or f"ORD_{uuid.uuid4().hex[:8].upper()}"
        self.client = client
        self.client_id = client_id
        self.origin = origin
        self.destination = destination
        self.status = "pending"
        self.priority = priority
        self.created_at = datetime.now()
        self.delivered_at: Optional[datetime] = None
        self.route_cost = 0.0
    
    def mark_delivered(self) -> None:
        """
        Marca la orden como entregada.
        """
        self.status = "delivered"
        self.delivered_at = datetime.now()
    
    def set_route_cost(self, cost: float) -> None:
        """
        Establece el costo de la ruta.
        
        Args:
            cost: Costo de la ruta
        """
        self.route_cost = cost
    
    def __str__(self) -> str:
        return f"Order(ID: {self.order_id}, Client: {self.client}, Origin: {self.origin}, Destination: {self.destination}, Status: {self.status})"
    
    def __repr__(self) -> str:
        return (f"Orden(order_id='{self.order_id}', client='{self.client}', "
                f"client_id='{self.client_id}', status='{self.status}', priority='{self.priority}')")

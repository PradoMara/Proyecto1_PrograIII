"""
Entidades del dominio (negocio) - Clase Client

Define la estructura y comportamiento de los clientes en el sistema de grafos conectados.
"""

from typing import Optional
import uuid


class Cliente:
    """
    Representa un cliente en el sistema de grafos conectados.
    
    Un cliente puede realizar pedidos.
    """
    
    def __init__(
        self,
        client_id: str = None,
        name: str = "",
        type: str = "regular"
    ):
        """
        Inicializa un nuevo cliente.
        
        Args:
            client_id: Identificador único del cliente
            name: Nombre del cliente
            type: Tipo de cliente (premium, regular, corporativo, vip)
        """
        self.client_id = client_id or f"CLI_{uuid.uuid4().hex[:8].upper()}"
        self.name = name or f"Cliente_{self.client_id[-4:]}"
        self.type = type
        self.total_orders = 0
    
    def increment_orders(self) -> None:
        """
        Incrementa el contador de órdenes del cliente.
        """
        self.total_orders += 1
    
    def __str__(self) -> str:
        return f"Cliente(ID: {self.client_id}, Name: {self.name}, Type: {self.type}, Total Orders: {self.total_orders})"
    
    def __repr__(self) -> str:
        return (f"Cliente(client_id='{self.client_id}', name='{self.name}', "
                f"type='{self.type}', total_orders={self.total_orders})")

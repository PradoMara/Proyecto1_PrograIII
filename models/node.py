from enum import Enum
from datetime import datetime
import random
import string

class NodeType(Enum):
    """Tipos de nodos en la red de drones"""
    STORAGE = "📦"      # Almacenamiento (20%)
    CHARGING = "🔋"     # Recarga (20%)
    CLIENT = "👤"       # Cliente (60%)

class Node:
    """Representa un nodo en la red de distribución"""
    
    def __init__(self, node_id, node_type, name=None, x=0, y=0):
        self.id = node_id
        self.type = node_type
        self.name = name or self._generate_name()
        self.x = x
        self.y = y
        self.visit_count = 0  # Contador de visitas para estadísticas
        
    def _generate_name(self):
        """Genera un nombre aleatorio para el nodo"""
        return ''.join(random.choices(string.ascii_uppercase, k=1))
    
    def increment_visit(self):
        """Incrementa el contador de visitas"""
        self.visit_count += 1
    
    def __str__(self):
        return f"{self.type.value} {self.name}"
    
    def __repr__(self):
        return f"Node({self.id}, {self.type.name}, {self.name})"

class Order:
    """Representa una orden de entrega"""
    
    def __init__(self, order_id, client_id, origin_id, destination_id, priority=1):
        self.id = order_id
        self.client_id = client_id
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.priority = priority
        self.status = "Pendiente"
        self.creation_date = datetime.now()
        self.delivery_date = None
        self.total_cost = 0
        self.route_path = []
    
    def complete_delivery(self, cost, route_path):
        """Marca la orden como completada"""
        self.status = "Entregado"
        self.delivery_date = datetime.now()
        self.total_cost = cost
        self.route_path = route_path
    
    def to_dict(self):
        """Convierte la orden a diccionario para visualización"""
        return {
            "ID": self.id,
            "Cliente ID": self.client_id,
            "Origen": self.origin_id,
            "Destino": self.destination_id,
            "Status": self.status,
            "Fecha Creación": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Prioridad": self.priority,
            "Fecha Entrega": self.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if self.delivery_date else "N/A",
            "Costo Total": self.total_cost
        }

class Client:
    """Representa un cliente en el sistema"""
    
    def __init__(self, client_id, name, node_id):
        self.id = client_id
        self.name = name
        self.node_id = node_id
        self.total_orders = 0
        self.orders = []
    
    def add_order(self, order):
        """Agrega una orden al cliente"""
        self.orders.append(order)
        self.total_orders += 1
    
    def to_dict(self):
        """Convierte el cliente a diccionario para visualización"""
        return {
            "ID": self.id,
            "Nombre": self.name,
            "Tipo": "Cliente",
            "Total Pedidos": self.total_orders,
            "Nodo ID": self.node_id
        }

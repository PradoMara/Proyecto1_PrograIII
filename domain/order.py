import uuid
from datetime import datetime
import random

class Order:
    def __init__(self, client_id, origin_node, destination_node):
        self.id = str(uuid.uuid4())[:8]
        self.client_id = client_id
        self.origin = origin_node
        self.destination = destination_node
        self.status = "pendiente"
        self.created_at = datetime.now()
        self.priority = random.choice(["alta", "media", "baja"])
        self.delivery_date = None
        self.total_cost = 0
        self.route = []
    
    def complete_delivery(self, route, cost):
        self.status = "entregado"
        self.delivery_date = datetime.now()
        self.total_cost = cost
        self.route = route
    
    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "origin": str(self.origin),
            "destination": str(self.destination),
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "priority": self.priority,
            "delivery_date": self.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if self.delivery_date else None,
            "total_cost": self.total_cost,
            "route": [str(node) for node in self.route]
        }

import uuid
from datetime import datetime

class Client:
    def __init__(self, node_id, name):
        self.id = str(uuid.uuid4())[:8]
        self.node_id = node_id
        self.name = name
        self.type = "cliente"
        self.total_orders = 0
        self.created_at = datetime.now()
    
    def increment_orders(self):
        self.total_orders += 1
    
    def to_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "name": self.name,
            "type": self.type,
            "total_orders": self.total_orders,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

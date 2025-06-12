class Route:
    def __init__(self, origin, destination, path, cost):
        self.origin = origin
        self.destination = destination
        self.path = path
        self.cost = cost
        self.frequency = 1
    
    def increment_frequency(self):
        self.frequency += 1
    
    def get_route_key(self):
        return f"{self.origin}->{self.destination}"
    
    def to_dict(self):
        return {
            "origin": str(self.origin),
            "destination": str(self.destination),
            "path": [str(node) for node in self.path],
            "cost": self.cost,
            "frequency": self.frequency
        }

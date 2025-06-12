from collections import deque
from models.node import NodeType

class PathFinder:
    """Clase para encontrar rutas considerando limitaciones de batería"""
    
    def __init__(self, graph):
        self.graph = graph
        self.MAX_BATTERY = 50
    
    def find_path_bfs(self, start, end):
        """Encuentra el camino más corto usando BFS con consideración de batería"""
        if start == end:
            return [start]
        
        # BFS simple sin restricciones de batería primero
        queue = deque([(start, [start])])
        visited = set()
        
        while queue:
            current, path = queue.popleft()
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor, weight in self.graph.edges[current]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    
                    if neighbor == end:
                        # Verificar si el camino es válido con batería
                        cost = self._calculate_cost(new_path)
                        if cost <= self.MAX_BATTERY or self._has_charging_station(new_path):
                            return new_path
                    
                    if len(new_path) <= len(self.graph.nodes):
                        queue.append((neighbor, new_path))
        
        # Si no encontramos ruta simple, intentar con estaciones de carga
        return self._bfs_with_charging(start, end)
    
    def find_path_dfs(self, start, end):
        """Encuentra un camino usando DFS con consideración de batería"""
        visited = set()
        
        def dfs_recursive(current, target, battery, path):
            if current == target:
                return path + [current]
            
            if current in visited or battery < 0:
                return None
            
            visited.add(current)
            
            for neighbor, weight in self.graph.edges[current]:
                if neighbor not in visited:
                    new_battery = battery - weight
                    
                    # Recargar si es estación de carga
                    if self.graph.nodes[neighbor].type == NodeType.CHARGING:
                        new_battery = self.MAX_BATTERY
                    
                    result = dfs_recursive(neighbor, target, new_battery, path + [current])
                    if result:
                        return result
            
            visited.remove(current)
            return None
        
        result = dfs_recursive(start, end, self.MAX_BATTERY, [])
        return result if result else []
    
    def topological_sort_path(self, start, end):
        """Búsqueda con prioridad por tipos de nodos"""
        # Prioridades por tipo
        type_priority = {
            NodeType.STORAGE: 1,
            NodeType.CHARGING: 2,
            NodeType.CLIENT: 3
        }
        
        if start == end:
            return [start]
        
        queue = deque([(start, self.MAX_BATTERY, [start])])
        visited = set()
        
        while queue:
            current, battery, path = queue.popleft()
            
            if current in visited:
                continue
            visited.add(current)
            
            # Ordenar vecinos por prioridad y peso
            neighbors = sorted(
                self.graph.edges[current],
                key=lambda x: (type_priority.get(self.graph.nodes[x[0]].type, 4), x[1])
            )
            
            for neighbor, weight in neighbors:
                if neighbor not in visited:
                    new_battery = battery - weight
                    new_path = path + [neighbor]
                    
                    if neighbor == end and new_battery >= 0:
                        return new_path
                    
                    if new_battery >= 0:
                        # Recargar en estaciones
                        if self.graph.nodes[neighbor].type == NodeType.CHARGING:
                            new_battery = self.MAX_BATTERY
                        
                        if len(new_path) <= len(self.graph.nodes):
                            queue.append((neighbor, new_battery, new_path))
        
        return []
    
    def _bfs_with_battery(self, start, end):
        """BFS básico considerando batería"""
        queue = deque([(start, self.MAX_BATTERY, [start])])
        visited = {}  # Cambiar a diccionario para rastrear la mejor batería por nodo
        
        while queue:
            current, battery, path = queue.popleft()
            
            # Si ya visitamos este nodo con mejor batería, continuar
            if current in visited and visited[current] >= battery:
                continue
            visited[current] = battery
            
            # Si llegamos al destino, retornar el camino
            if current == end:
                return path
            
            for neighbor, weight in self.graph.edges[current]:
                new_battery = battery - weight
                new_path = path + [neighbor]
                
                # Permitir rutas con batería negativa si hay estación de carga cercana
                should_add = False
                
                if new_battery >= 0:
                    should_add = True
                elif self.graph.nodes[neighbor].type == NodeType.CHARGING:
                    # Si es estación de carga, resetear batería
                    new_battery = self.MAX_BATTERY
                    should_add = True
                elif new_battery >= -10:  # Permitir un poco de batería negativa
                    should_add = True
                
                if should_add and (neighbor not in visited or visited[neighbor] < new_battery):
                    # Evitar bucles infinitos
                    if len(new_path) <= len(self.graph.nodes) + 5:
                        queue.append((neighbor, new_battery, new_path))
        
        return []
    
    def _bfs_with_charging(self, start, end):
        """BFS que incluye estaciones de carga obligatorias"""
        charging_stations = self.graph.get_charging_nodes()
        
        best_path = []
        min_cost = float('inf')
        
        for station in charging_stations:
            # Ruta hasta estación
            path_to_station = self._bfs_with_battery(start, station)
            if not path_to_station:
                continue
            
            # Ruta desde estación hasta destino
            path_from_station = self._bfs_with_battery(station, end)
            if not path_from_station:
                continue
            
            # Combinar rutas
            full_path = path_to_station + path_from_station[1:]
            cost = self._calculate_cost(full_path)
            
            if cost < min_cost:
                min_cost = cost
                best_path = full_path
        
        return best_path
    
    def _calculate_cost(self, path):
        """Calcula el costo total de un camino"""
        if len(path) < 2:
            return 0
        
        total = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            for neighbor, weight in self.graph.edges[current]:
                if neighbor == next_node:
                    total += weight
                    break
        
        return total
    
    def get_path_info(self, path):
        """Obtiene información detallada de un camino"""
        if not path:
            return {"path": [], "path_string": "", "cost": 0, "valid": False}
        
        if len(path) == 1:
            node_name = self.graph.nodes[path[0]].name
            return {
                "path": path,
                "path_string": node_name,
                "cost": 0,
                "valid": True
            }
        
        cost = self._calculate_cost(path)
        path_string = " → ".join([self.graph.nodes[node].name for node in path])
        
        return {
            "path": path,
            "path_string": path_string,
            "cost": round(cost, 2),
            "valid": cost <= self.MAX_BATTERY or self._has_charging_station(path)
        }
    
    def _has_charging_station(self, path):
        """Verifica si hay estaciones de carga en el camino"""
        for node_id in path[1:-1]:
            if self.graph.nodes[node_id].type == NodeType.CHARGING:
                return True
        return False

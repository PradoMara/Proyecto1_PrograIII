from collections import deque, defaultdict
from models.node import NodeType

class PathFinder:
    """Clase para encontrar rutas en el grafo considerando limitaciones de batería"""
    
    def __init__(self, graph):
        self.graph = graph
        self.MAX_BATTERY = graph.MAX_BATTERY
    
    def find_path_bfs(self, start, end):
        """
        Encuentra el camino más corto usando BFS modificado para considerar batería.
        Si no se puede llegar directamente, incluye estaciones de carga.
        """
        # Intentar ruta directa primero
        direct_path = self._bfs_with_battery(start, end, self.MAX_BATTERY)
        if direct_path:
            return direct_path
        
        # Si no se puede llegar directamente, buscar ruta con recarga
        return self._bfs_with_charging_stations(start, end)
    
    def find_path_dfs(self, start, end):
        """
        Encuentra un camino usando DFS modificado para considerar batería.
        """
        visited = set()
        path = []
        
        def dfs_recursive(current, target, current_battery, current_path):
            if current == target:
                return current_path + [current]
            
            if current in visited or current_battery < 0:
                return None
            
            visited.add(current)
            current_path.append(current)
            
            # Ordenar vecinos por peso para priorizar rutas más cortas
            neighbors = sorted(self.graph.edges[current], key=lambda x: x[1])
            
            for neighbor, weight in neighbors:
                if neighbor not in visited:
                    new_battery = current_battery - weight
                    
                    # Si es estación de carga, recargar batería
                    if self.graph.nodes[neighbor].type == NodeType.CHARGING:
                        new_battery = self.MAX_BATTERY
                    
                    result = dfs_recursive(neighbor, target, new_battery, current_path.copy())
                    if result:
                        return result
            
            current_path.pop()
            visited.remove(current)
            return None
        
        result = dfs_recursive(start, end, self.MAX_BATTERY, [])
        return result if result else []
    
    def _bfs_with_battery(self, start, end, max_battery):
        """BFS considerando limitaciones de batería"""
        if start == end:
            return [start]
        
        queue = deque([(start, max_battery, [start])])
        visited = set([(start, max_battery)])
        
        while queue:
            current, battery, path = queue.popleft()
            
            for neighbor, weight in self.graph.edges[current]:
                new_battery = battery - weight
                new_path = path + [neighbor]
                
                # Si llegamos al destino y tenemos batería suficiente
                if neighbor == end and new_battery >= 0:
                    return new_path
                
                # Si tenemos batería suficiente para continuar
                if new_battery >= 0 and (neighbor, new_battery) not in visited:
                    visited.add((neighbor, new_battery))
                    
                    # Si es estación de carga, recargar
                    if self.graph.nodes[neighbor].type == NodeType.CHARGING:
                        new_battery = max_battery
                    
                    queue.append((neighbor, new_battery, new_path))
        
        return []
    
    def _bfs_with_charging_stations(self, start, end):
        """BFS que incluye estaciones de carga obligatorias"""
        charging_stations = self.graph.get_charging_nodes()
        
        # Buscar la mejor ruta pasando por estaciones de carga
        best_path = []
        min_cost = float('inf')
        
        for station in charging_stations:
            # Ruta desde start hasta station
            path_to_station = self._bfs_with_battery(start, station, self.MAX_BATTERY)
            if not path_to_station:
                continue
            
            # Ruta desde station hasta end (con batería completa)
            path_from_station = self._bfs_with_battery(station, end, self.MAX_BATTERY)
            if not path_from_station:
                continue
            
            # Combinar rutas (evitar duplicar la estación de carga)
            full_path = path_to_station + path_from_station[1:]
            total_cost = self._calculate_path_cost(full_path)
            
            if total_cost < min_cost:
                min_cost = total_cost
                best_path = full_path
        
        return best_path
    
    def _calculate_path_cost(self, path):
        """Calcula el costo total de un camino"""
        if len(path) < 2:
            return 0
        
        total_cost = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            # Buscar el peso de la arista
            for neighbor, weight in self.graph.edges[current]:
                if neighbor == next_node:
                    total_cost += weight
                    break
        
        return total_cost
    
    def topological_sort_path(self, start, end):
        """
        Implementación de búsqueda usando ordenamiento topológico modificado.
        Útil para rutas con dependencias de carga.
        """
        # Para este caso, usaremos un enfoque similar a BFS pero priorizando
        # el orden topológico basado en tipos de nodos
        return self._priority_bfs(start, end)
    
    def _priority_bfs(self, start, end):
        """BFS con prioridad basada en tipos de nodos"""
        if start == end:
            return [start]
        
        # Prioridades: STORAGE (1) -> CHARGING (2) -> CLIENT (3)
        type_priority = {
            NodeType.STORAGE: 1,
            NodeType.CHARGING: 2,
            NodeType.CLIENT: 3
        }
        
        queue = deque([(start, self.MAX_BATTERY, [start], 0)])  # (node, battery, path, cost)
        visited = {}  # {node: min_cost_to_reach}
        
        while queue:
            current, battery, path, cost = queue.popleft()
            
            # Si ya visitamos este nodo con menor costo, continuar
            if current in visited and visited[current] <= cost:
                continue
            visited[current] = cost
            
            # Ordenar vecinos por prioridad de tipo y peso
            neighbors = sorted(
                self.graph.edges[current],
                key=lambda x: (type_priority.get(self.graph.nodes[x[0]].type, 4), x[1])
            )
            
            for neighbor, weight in neighbors:
                new_battery = battery - weight
                new_cost = cost + weight
                new_path = path + [neighbor]
                
                # Si llegamos al destino
                if neighbor == end and new_battery >= 0:
                    return new_path
                
                # Si tenemos batería suficiente para continuar
                if new_battery >= 0:
                    # Si es estación de carga, recargar
                    if self.graph.nodes[neighbor].type == NodeType.CHARGING:
                        new_battery = self.MAX_BATTERY
                    
                    # Evitar ciclos largos
                    if len(new_path) <= len(self.graph.nodes):
                        queue.append((neighbor, new_battery, new_path, new_cost))
        
        return []
    
    def get_path_info(self, path):
        """Obtiene información detallada de un camino"""
        if not path or len(path) < 2:
            return {"path": path, "cost": 0, "valid": len(path) <= 1}
        
        total_cost = self._calculate_path_cost(path)
        is_valid = total_cost <= self.MAX_BATTERY or self._has_charging_station(path)
        
        # Construir string del camino
        path_str = " → ".join([self.graph.nodes[node].name for node in path])
        
        return {
            "path": path,
            "path_string": path_str,
            "cost": round(total_cost, 2),
            "valid": is_valid,
            "requires_charging": not is_valid or self._has_charging_station(path)
        }
    
    def _has_charging_station(self, path):
        """Verifica si el camino incluye estaciones de carga"""
        for node_id in path[1:-1]:  # Excluir origen y destino
            if self.graph.nodes[node_id].type == NodeType.CHARGING:
                return True
        return False

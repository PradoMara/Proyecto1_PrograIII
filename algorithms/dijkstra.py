import heapq
from models.node import NodeType

class Dijkstra:
    """Implementación del algoritmo de Dijkstra para encontrar el camino más corto"""
    
    def __init__(self, graph):
        self.graph = graph
        self.MAX_BATTERY = 50
    
    def find_shortest_path(self, start, end):
        """
        Encuentra el camino más corto entre dos nodos usando el algoritmo de Dijkstra
        
        Args:
            start: Nodo de inicio
            end: Nodo de destino
            
        Returns:
            tuple: (camino, distancia_total) o ([], float('inf')) si no hay camino
        """
        if start == end:
            return [start], 0
        
        # Inicializar distancias y predecesores
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start] = 0
        predecessors = {node: None for node in self.graph.nodes}
        
        # Cola de prioridad: (distancia, nodo)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            # Si llegamos al destino, construir el camino
            if current_node == end:
                return self._reconstruct_path(predecessors, start, end), current_dist
            
            # Explorar vecinos
            if current_node in self.graph.edges:
                for neighbor, weight in self.graph.edges[current_node]:
                    if neighbor not in visited:
                        new_dist = current_dist + weight
                        
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            predecessors[neighbor] = current_node
                            heapq.heappush(pq, (new_dist, neighbor))
        
        return [], float('inf')  # No hay camino
    
    def find_shortest_path_with_battery(self, start, end):
        """
        Encuentra el camino más corto considerando las limitaciones de batería
        
        Args:
            start: Nodo de inicio
            end: Nodo de destino
            
        Returns:
            dict: Información completa del camino incluyendo validez de batería
        """
        if start == end:
            return {
                "path": [start],
                "distance": 0,
                "battery_used": 0,
                "valid": True,
                "charging_stops": []
            }
        
        # Estado: (distancia, nodo, batería_restante)
        # distances guarda el mejor estado para cada (nodo, batería)
        distances = {}
        predecessors = {}
        
        # Cola de prioridad: (distancia, nodo, batería_restante)
        pq = [(0, start, self.MAX_BATTERY)]
        distances[(start, self.MAX_BATTERY)] = 0
        
        best_solution = None
        
        while pq:
            current_dist, current_node, battery = heapq.heappop(pq)
            
            # Si llegamos al destino
            if current_node == end:
                path = self._reconstruct_path_with_battery(predecessors, start, end, battery)
                best_solution = {
                    "path": path,
                    "distance": current_dist,
                    "battery_used": self.MAX_BATTERY - battery,
                    "valid": True,
                    "charging_stops": self._get_charging_stops(path)
                }
                break
            
            # Explorar vecinos
            if current_node in self.graph.edges:
                for neighbor, weight in self.graph.edges[current_node]:
                    new_dist = current_dist + weight
                    new_battery = battery - weight
                    
                    # Si es estación de carga, recargar batería
                    if self.graph.nodes[neighbor].type == NodeType.CHARGING:
                        new_battery = self.MAX_BATTERY
                    
                    # Solo continuar si tenemos batería suficiente o estamos en estación de carga
                    if new_battery >= 0 or self.graph.nodes[neighbor].type == NodeType.CHARGING:
                        state = (neighbor, new_battery)
                        
                        if state not in distances or new_dist < distances[state]:
                            distances[state] = new_dist
                            predecessors[state] = (current_node, battery)
                            heapq.heappush(pq, (new_dist, neighbor, new_battery))
        
        if best_solution:
            return best_solution
        
        return {
            "path": [],
            "distance": float('inf'),
            "battery_used": 0,
            "valid": False,
            "charging_stops": []
        }
    
    def find_all_shortest_paths(self, start):
        """
        Encuentra los caminos más cortos desde un nodo a todos los demás
        
        Args:
            start: Nodo de inicio
            
        Returns:
            dict: Diccionario con distancias y caminos a todos los nodos
        """
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start] = 0
        predecessors = {node: None for node in self.graph.nodes}
        
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            if current_node in self.graph.edges:
                for neighbor, weight in self.graph.edges[current_node]:
                    if neighbor not in visited:
                        new_dist = current_dist + weight
                        
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            predecessors[neighbor] = current_node
                            heapq.heappush(pq, (new_dist, neighbor))
        
        # Construir todos los caminos
        paths = {}
        for node in self.graph.nodes:
            if distances[node] != float('inf'):
                paths[node] = {
                    "path": self._reconstruct_path(predecessors, start, node),
                    "distance": distances[node]
                }
            else:
                paths[node] = {
                    "path": [],
                    "distance": float('inf')
                }
        
        return paths
    
    def _reconstruct_path(self, predecessors, start, end):
        """Reconstruye el camino desde los predecesores"""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        path.reverse()
        
        # Verificar que el camino es válido
        if path[0] != start:
            return []
        
        return path
    
    def _reconstruct_path_with_battery(self, predecessors, start, end, end_battery):
        """Reconstruye el camino considerando estados de batería"""
        path = []
        current_state = (end, end_battery)
        
        while current_state in predecessors:
            path.append(current_state[0])
            current_state = predecessors[current_state]
        
        if current_state:
            path.append(current_state[0])
        
        path.reverse()
        
        if path and path[0] != start:
            return []
        
        return path
    
    def _get_charging_stops(self, path):
        """Identifica las estaciones de carga en el camino"""
        charging_stops = []
        
        for i, node in enumerate(path):
            if self.graph.nodes[node].type == NodeType.CHARGING and i != 0 and i != len(path) - 1:
                charging_stops.append({
                    "node": node,
                    "position": i,
                    "name": self.graph.nodes[node].name
                })
        
        return charging_stops
    
    def get_path_info(self, path):
        """Obtiene información detallada de un camino"""
        if not path:
            return {
                "path": [],
                "path_string": "",
                "distance": float('inf'),
                "battery_required": 0,
                "valid": False,
                "charging_stops": []
            }
        
        if len(path) == 1:
            node_name = self.graph.nodes[path[0]].name
            return {
                "path": path,
                "path_string": node_name,
                "distance": 0,
                "battery_required": 0,
                "valid": True,
                "charging_stops": []
            }
        
        # Calcular distancia total y batería requerida
        total_distance = 0
        battery_required = 0
        current_battery = self.MAX_BATTERY
        
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            # Encontrar el peso de la arista
            edge_weight = 0
            if current in self.graph.edges:
                for neighbor, weight in self.graph.edges[current]:
                    if neighbor == next_node:
                        edge_weight = weight
                        break
            
            total_distance += edge_weight
            current_battery -= edge_weight
            
            # Si es estación de carga, recargar
            if self.graph.nodes[next_node].type == NodeType.CHARGING:
                current_battery = self.MAX_BATTERY
            
            battery_required = max(battery_required, self.MAX_BATTERY - current_battery)
        
        path_string = " → ".join([self.graph.nodes[node].name for node in path])
        
        return {
            "path": path,
            "path_string": path_string,
            "distance": round(total_distance, 2),
            "battery_required": round(battery_required, 2),
            "valid": battery_required <= self.MAX_BATTERY or len(self._get_charging_stops(path)) > 0,
            "charging_stops": self._get_charging_stops(path)
        }

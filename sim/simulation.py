import random
from collections import deque
from domain.client import Client
from domain.order import Order
from domain.route import Route
from tda.TDA_HaspMap import Map
from tda.AVL import insert, Node as AVLNode
from sim.init_simulation import SimulationInitializer

class Simulation:
    def __init__(self):
        self.initializer = SimulationInitializer()
        self.graph = None
        self.node_types = None
        self.clients = Map()
        self.orders = Map()
        self.routes_avl = None
        self.max_battery = 50
        self.simulation_active = False
        
    def start_simulation(self, n_nodes=15, n_edges=20, n_orders=10):
        """Inicia la simulación con los parámetros dados"""
        # Validaciones
        min_edges = n_nodes - 1
        if n_edges < min_edges:
            n_edges = min_edges
            
        # Generar red
        success = self.initializer.generate_connected_graph(n_nodes, n_edges)
        if not success:
            return False
            
        # Copiar referencias
        self.graph = self.initializer.graph
        self.node_types = self.initializer.node_types
        
        # Generar clientes y órdenes
        self._generate_clients_and_orders(n_orders)
        
        self.simulation_active = True
        return True
    
    def _generate_clients_and_orders(self, n_orders):
        """Genera clientes y órdenes aleatorias"""
        # Generar clientes
        client_names = ["Maria", "Carlos", "Ana", "Pedro", "Lucia", "Diego", "Sofia", "Miguel", 
                       "Carmen", "Roberto", "Elena", "Fernando", "Isabel", "Alejandro", "Patricia"]
        
        for i, client_node in enumerate(self.initializer.client_nodes):
            name = random.choice(client_names)
            client = Client(client_node, f"{name}_{i}")
            self.clients[client.id] = client
        
        # Generar órdenes
        client_ids = list(self.clients.keys())
        for _ in range(n_orders):
            if client_ids and self.initializer.storage_nodes and self.initializer.client_nodes:
                client_id = random.choice(client_ids)
                origin = random.choice(self.initializer.storage_nodes)
                destination = random.choice(self.initializer.client_nodes)
                
                order = Order(client_id, origin, destination)
                self.orders[order.id] = order
                
                # Incrementar contador del cliente
                client = self.clients[client_id]
                client.increment_orders()
    
    def find_path_with_battery(self, start, end):
        """Encuentra ruta considerando batería limitada usando BFS modificado"""
        if not self.graph or start not in self.graph.vertices() or end not in self.graph.vertices():
            return None, 0
            
        # BFS con consideración de batería
        queue = deque([(start, [start], 0)])  # (nodo_actual, camino, costo_acumulado)
        visited = set()
        
        while queue:
            current, path, cost = queue.popleft()
            
            if current == end:
                return path, cost
            
            if current in visited:
                continue
                
            visited.add(current)
            
            # Explorar vecinos
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    edge = self.graph.get_edge(current, neighbor)
                    if edge:
                        new_cost = cost + edge.element()
                        new_path = path + [neighbor]
                        
                        # Si excede batería, buscar estación de recarga
                        if new_cost > self.max_battery:
                            recharged_path = self._find_path_with_recharge(start, end, path, cost)
                            if recharged_path:
                                return recharged_path
                        else:
                            queue.append((neighbor, new_path, new_cost))
        
        # Si no encuentra ruta directa, intentar con recarga
        return self._find_path_with_recharge(start, end, [start], 0)
    
    def _find_path_with_recharge(self, start, end, current_path, current_cost):
        """Busca ruta que incluya estaciones de recarga"""
        # Encontrar la estación de recarga más cercana
        recharge_stations = self.initializer.recharge_nodes
        if not recharge_stations:
            return None, 0
            
        best_route = None
        best_cost = float('inf')
        
        for station in recharge_stations:
            if station not in current_path:
                # Ruta a la estación
                path_to_station, cost_to_station = self._simple_bfs(current_path[-1], station)
                if path_to_station and cost_to_station <= self.max_battery:
                    # Ruta desde la estación al destino
                    path_from_station, cost_from_station = self._simple_bfs(station, end)
                    if path_from_station and cost_from_station <= self.max_battery:
                        # Combinar rutas
                        total_path = current_path[:-1] + path_to_station + path_from_station[1:]
                        total_cost = current_cost + cost_to_station + cost_from_station
                        
                        if total_cost < best_cost:
                            best_route = total_path
                            best_cost = total_cost
        
        return (best_route, best_cost) if best_route else (None, 0)
    
    def _simple_bfs(self, start, end):
        """BFS simple para encontrar ruta entre dos nodos"""
        if start == end:
            return [start], 0
            
        queue = deque([(start, [start], 0)])
        visited = set()
        
        while queue:
            current, path, cost = queue.popleft()
            
            if current == end:
                return path, cost
                
            if current in visited:
                continue
                
            visited.add(current)
            
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    edge = self.graph.get_edge(current, neighbor)
                    if edge:
                        new_cost = cost + edge.element()
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path, new_cost))
        
        return None, 0
    
    def complete_delivery(self, origin, destination, route, cost):
        """Completa una entrega y registra la ruta"""
        # Buscar orden correspondiente
        for order_id in self.orders.keys():
            order = self.orders[order_id]
            if (str(order.origin) == str(origin) and 
                str(order.destination) == str(destination) and 
                order.status == "pendiente"):
                
                order.complete_delivery(route, cost)
                
                # Registrar ruta en AVL
                route_key = f"{origin}->{destination}"
                self.routes_avl = insert(self.routes_avl, route_key)
                
                return True
        
        return False
    
    def get_node_info(self):
        """Retorna información de distribución de nodos"""
        if not self.simulation_active:
            return None
        return self.initializer.get_node_distributions()
    
    def get_clients_list(self):
        """Retorna lista de clientes"""
        clients_list = []
        for client_id in self.clients.keys():
            client = self.clients[client_id]
            clients_list.append(client.to_dict())
        return clients_list
    
    def get_orders_list(self):
        """Retorna lista de órdenes"""
        orders_list = []
        for order_id in self.orders.keys():
            order = self.orders[order_id]
            orders_list.append(order.to_dict())
        return orders_list

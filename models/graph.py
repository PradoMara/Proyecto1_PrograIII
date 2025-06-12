import random
import math
from collections import defaultdict, deque
from models.node import Node, NodeType, Client, Order

class Graph:
    """Grafo que representa la red de distribución de drones"""
    
    def __init__(self):
        self.nodes = {}  # {node_id: Node}
        self.edges = defaultdict(list)  # {node_id: [(neighbor_id, weight), ...]}
        self.clients = {}  # {client_id: Client}
        self.orders = []  # Lista de órdenes
        self.next_order_id = 1
        self.next_client_id = 1
        
        # Constantes
        self.MAX_BATTERY = 50
        self.STORAGE_PERCENTAGE = 0.20
        self.CHARGING_PERCENTAGE = 0.20
        self.CLIENT_PERCENTAGE = 0.60
    
    def add_node(self, node_id, node_type, x=0, y=0):
        """Agrega un nodo al grafo"""
        node = Node(node_id, node_type, x=x, y=y)
        self.nodes[node_id] = node
        
        # Si es un nodo cliente, crear cliente asociado
        if node_type == NodeType.CLIENT:
            client = Client(self.next_client_id, f"Cliente_{self.next_client_id}", node_id)
            self.clients[self.next_client_id] = client
            self.next_client_id += 1
        
        return node
    
    def add_edge(self, node1, node2, weight):
        """Agrega una arista bidireccional entre dos nodos"""
        self.edges[node1].append((node2, weight))
        self.edges[node2].append((node1, weight))
    
    def generate_random_network(self, n_nodes, m_edges):
        """Genera una red aleatoria conectada"""
        self.nodes.clear()
        self.edges.clear()
        self.clients.clear()
        self.orders.clear()
        self.next_client_id = 1
        self.next_order_id = 1
        
        # Calcular cantidad de nodos por tipo
        n_storage = max(1, int(n_nodes * self.STORAGE_PERCENTAGE))
        n_charging = max(1, int(n_nodes * self.CHARGING_PERCENTAGE))
        n_clients = n_nodes - n_storage - n_charging
        
        # Crear nodos con posiciones aleatorias
        node_types = ([NodeType.STORAGE] * n_storage + 
                     [NodeType.CHARGING] * n_charging + 
                     [NodeType.CLIENT] * n_clients)
        random.shuffle(node_types)
        
        for i in range(n_nodes):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            self.add_node(i, node_types[i], x, y)
        
        # Generar árbol de expansión mínima para garantizar conectividad
        self._generate_minimum_spanning_tree()
        
        # Agregar aristas adicionales hasta alcanzar m_edges
        current_edges = len(self._get_all_edges()) // 2  # Dividir por 2 porque son bidireccionales
        additional_edges = max(0, m_edges - current_edges)
        
        for _ in range(additional_edges):
            self._add_random_edge()
    
    def _generate_minimum_spanning_tree(self):
        """Genera un árbol de expansión mínima para garantizar conectividad"""
        if len(self.nodes) < 2:
            return
        
        visited = set()
        start_node = list(self.nodes.keys())[0]
        visited.add(start_node)
        
        while len(visited) < len(self.nodes):
            min_weight = float('inf')
            best_edge = None
            
            for node_id in visited:
                for other_id in self.nodes:
                    if other_id not in visited:
                        weight = self._calculate_distance(node_id, other_id)
                        if weight < min_weight:
                            min_weight = weight
                            best_edge = (node_id, other_id)
            
            if best_edge:
                node1, node2 = best_edge
                self.add_edge(node1, node2, min_weight)
                visited.add(node2)
    
    def _add_random_edge(self):
        """Agrega una arista aleatoria que no exista"""
        nodes_list = list(self.nodes.keys())
        max_attempts = 100
        
        for _ in range(max_attempts):
            node1 = random.choice(nodes_list)
            node2 = random.choice(nodes_list)
            
            if node1 != node2 and not self._edge_exists(node1, node2):
                weight = self._calculate_distance(node1, node2)
                self.add_edge(node1, node2, weight)
                break
    
    def _edge_exists(self, node1, node2):
        """Verifica si existe una arista entre dos nodos"""
        return any(neighbor == node2 for neighbor, _ in self.edges[node1])
    
    def _calculate_distance(self, node1_id, node2_id):
        """Calcula la distancia euclidiana entre dos nodos escalada"""
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        dx = node1.x - node2.x
        dy = node1.y - node2.y
        distance = math.sqrt(dx * dx + dy * dy)
        # Escalar la distancia para que sea más manejable (máximo ~15 unidades)
        return min(15, max(1, distance * 0.15))
    
    def _get_all_edges(self):
        """Obtiene todas las aristas del grafo"""
        edges = []
        for node, neighbors in self.edges.items():
            for neighbor, weight in neighbors:
                edges.append((node, neighbor, weight))
        return edges
    
    def get_storage_nodes(self):
        """Obtiene todos los nodos de almacenamiento"""
        return [node_id for node_id, node in self.nodes.items() 
                if node.type == NodeType.STORAGE]
    
    def get_charging_nodes(self):
        """Obtiene todos los nodos de recarga"""
        return [node_id for node_id, node in self.nodes.items() 
                if node.type == NodeType.CHARGING]
    
    def get_client_nodes(self):
        """Obtiene todos los nodos cliente"""
        return [node_id for node_id, node in self.nodes.items() 
                if node.type == NodeType.CLIENT]
    
    def generate_orders(self, n_orders):
        """Genera órdenes aleatorias"""
        storage_nodes = self.get_storage_nodes()
        client_nodes = self.get_client_nodes()
        
        if not storage_nodes or not client_nodes:
            return
        
        for _ in range(n_orders):
            origin = random.choice(storage_nodes)
            destination = random.choice(client_nodes)
            
            # Encontrar cliente asociado al nodo destino
            client_id = None
            for cid, client in self.clients.items():
                if client.node_id == destination:
                    client_id = cid
                    break
            
            if client_id:
                priority = random.randint(1, 5)
                order = Order(self.next_order_id, client_id, origin, destination, priority)
                self.orders.append(order)
                self.clients[client_id].add_order(order)
                self.next_order_id += 1
    
    def get_network_stats(self):
        """Obtiene estadísticas de la red"""
        storage_count = len(self.get_storage_nodes())
        charging_count = len(self.get_charging_nodes())
        client_count = len(self.get_client_nodes())
        total_nodes = len(self.nodes)
        
        return {
            "total_nodes": total_nodes,
            "storage": {
                "count": storage_count,
                "percentage": (storage_count / total_nodes * 100) if total_nodes > 0 else 0
            },
            "charging": {
                "count": charging_count,
                "percentage": (charging_count / total_nodes * 100) if total_nodes > 0 else 0
            },
            "client": {
                "count": client_count,
                "percentage": (client_count / total_nodes * 100) if total_nodes > 0 else 0
            },
            "total_edges": len(self._get_all_edges()) // 2,
            "total_orders": len(self.orders)
        }
    
    def is_connected(self):
        """Verifica si el grafo es conexo usando BFS"""
        if not self.nodes:
            return True
        
        start_node = next(iter(self.nodes))
        visited = set()
        queue = deque([start_node])
        visited.add(start_node)
        
        while queue:
            current = queue.popleft()
            for neighbor, _ in self.edges[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return len(visited) == len(self.nodes)

import random
import math
from model.graph import Graph
from domain.client import Client
from domain.order import Order
from domain.route import Route
from tda.TDA_HaspMap import Map

class SimulationInitializer:
    def __init__(self):
        self.graph = None
        self.node_types = Map()
        self.storage_nodes = []
        self.recharge_nodes = []
        self.client_nodes = []
        self.all_nodes = []
        
    def generate_connected_graph(self, n_nodes, n_edges):
        """Genera un grafo conectado con n_nodes y n_edges"""
        self.graph = Graph(directed=False)
        self.all_nodes = []
        
        # Crear todos los nodos
        for i in range(n_nodes):
            node = self.graph.insert_vertex(f"Nodo_{i}")
            self.all_nodes.append(node)
        
        # Asignar tipos según las proporciones
        self._assign_node_types()
        
        # Crear árbol spanning para garantizar conectividad
        self._create_spanning_tree()
        
        # Agregar aristas adicionales hasta llegar a n_edges
        self._add_additional_edges(n_edges)
        
        return True
    
    def _assign_node_types(self):
        """Asigna tipos a los nodos según las proporciones 20%-20%-60%"""
        n_total = len(self.all_nodes)
        n_storage = max(1, int(n_total * 0.2))
        n_recharge = max(1, int(n_total * 0.2))
        
        # Crear una copia para mezclar
        shuffled_nodes = self.all_nodes.copy()
        random.shuffle(shuffled_nodes)
        
        # Asignar según proporciones
        self.storage_nodes = shuffled_nodes[:n_storage]
        self.recharge_nodes = shuffled_nodes[n_storage:n_storage + n_recharge]
        self.client_nodes = shuffled_nodes[n_storage + n_recharge:]
        
        # Registrar en el mapa de tipos
        for node in self.storage_nodes:
            self.node_types[node] = "📦 Almacenamiento"
        for node in self.recharge_nodes:
            self.node_types[node] = "🔋 Recarga"
        for node in self.client_nodes:
            self.node_types[node] = "👤 Cliente"
    
    def _create_spanning_tree(self):
        """Crea un árbol spanning para garantizar conectividad"""
        if len(self.all_nodes) < 2:
            return
            
        # Algoritmo de Prim modificado
        visited = {self.all_nodes[0]}
        
        while len(visited) < len(self.all_nodes):
            # Encontrar el siguiente nodo a conectar
            unvisited = [n for n in self.all_nodes if n not in visited]
            next_node = random.choice(unvisited)
            parent_node = random.choice(list(visited))
            
            # Crear arista con peso aleatorio
            weight = random.randint(1, 15)
            self.graph.insert_edge(parent_node, next_node, weight)
            visited.add(next_node)
    
    def _add_additional_edges(self, target_edges):
        """Agrega aristas adicionales hasta alcanzar el número objetivo"""
        current_edges = len(list(self.graph.edges()))
        max_possible = len(self.all_nodes) * (len(self.all_nodes) - 1) // 2
        
        attempts = 0
        while current_edges < min(target_edges, max_possible) and attempts < 1000:
            u = random.choice(self.all_nodes)
            v = random.choice(self.all_nodes)
            
            if u != v and not self.graph.get_edge(u, v):
                weight = random.randint(1, 15)
                self.graph.insert_edge(u, v, weight)
                current_edges += 1
            
            attempts += 1
    
    def get_node_distributions(self):
        """Retorna información sobre la distribución de nodos"""
        total = len(self.all_nodes)
        return {
            "total_nodes": total,
            "storage_nodes": len(self.storage_nodes),
            "storage_percent": round(len(self.storage_nodes) / total * 100, 1),
            "recharge_nodes": len(self.recharge_nodes),
            "recharge_percent": round(len(self.recharge_nodes) / total * 100, 1),
            "client_nodes": len(self.client_nodes),
            "client_percent": round(len(self.client_nodes) / total * 100, 1)
        }

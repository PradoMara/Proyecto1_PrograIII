import streamlit as st
from datetime import datetime
from models.graph import Graph
from models.node import NodeType
from algorithms.pathfinding import PathFinder
from data_structures.avl_tree import AVLTree
from utils.visualization import NetworkVisualizer

class DroneSimulation:
    """Sistema principal de simulación de drones"""
    
    def __init__(self):
        self.graph = Graph()
        self.pathfinder = PathFinder(self.graph)
        self.visualizer = NetworkVisualizer(self.graph)
        self.route_registry = AVLTree()
        self.is_initialized = False
    
    def initialize_simulation(self, n_nodes=15, m_edges=20, n_orders=10):
        """Inicializa la simulación con parámetros dados"""
        try:
            # Validaciones básicas
            min_edges = n_nodes - 1
            if m_edges < min_edges:
                m_edges = min_edges
                st.warning(f"Número de aristas ajustado a {m_edges} para garantizar conectividad.")
            
            if n_nodes > 150:
                st.error("El número máximo de nodos es 150.")
                return False
            
            if m_edges > 300:
                st.warning("El número máximo de aristas es 300.")
                m_edges = 300
            
            if n_orders > 300:
                st.warning("El número máximo de órdenes es 300.")
                n_orders = 300
            
            # Generar red
            self.graph.generate_random_network(n_nodes, m_edges)
            
            # Verificar conectividad
            if not self.graph.is_connected():
                st.error("Error: El grafo generado no es conexo. Reintentando...")
                return False
            
            # Generar órdenes
            self.graph.generate_orders(n_orders)
            
            # Actualizar componentes
            self.visualizer = NetworkVisualizer(self.graph)
            self.pathfinder = PathFinder(self.graph)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            st.error(f"Error al inicializar la simulación: {str(e)}")
            return False
    
    def calculate_route(self, origin, destination, algorithm="BFS"):
        """Calcula una ruta entre dos nodos"""
        if not self.is_initialized:
            st.error("Debe inicializar la simulación primero.")
            return None
        
        if origin not in self.graph.nodes or destination not in self.graph.nodes:
            st.error("Origen o destino no válidos.")
            return None
        
        try:
            # Usar BFS por defecto
            path = self.pathfinder.find_path_bfs(origin, destination)
            
            if not path:
                st.error("No se encontró una ruta válida entre los nodos seleccionados.")
                return None
            
            # Obtener información de la ruta
            route_info = self.pathfinder.get_path_info(path)
            
            # Incrementar contador de visitas
            for node_id in path:
                self.graph.nodes[node_id].increment_visit()
            
            return route_info
            
        except Exception as e:
            st.error(f"Error al calcular la ruta: {str(e)}")
            return None
    
    def complete_delivery(self, route_info, origin, destination):
        """Completa una entrega y registra la ruta"""
        if not route_info:
            return False
        
        try:
            # Registrar ruta en AVL
            self.route_registry.add_route(route_info['path'])
            
            # Buscar orden correspondiente y completarla
            for order in self.graph.orders:
                if (order.origin_id == origin and 
                    order.destination_id == destination and 
                    order.status == "Pendiente"):
                    
                    order.complete_delivery(route_info['cost'], route_info['path'])
                    return True
            
            # Si no hay orden existente, crear una nueva
            client_id = None
            for cid, client in self.graph.clients.items():
                if client.node_id == destination:
                    client_id = cid
                    break
            
            if client_id:
                from models.node import Order
                new_order = Order(self.graph.next_order_id, client_id, origin, destination)
                new_order.complete_delivery(route_info['cost'], route_info['path'])
                self.graph.orders.append(new_order)
                self.graph.clients[client_id].add_order(new_order)
                self.graph.next_order_id += 1
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error al completar la entrega: {str(e)}")
            return False
    
    def get_network_visualization(self, highlight_path=None):
        """Obtiene la visualización de la red"""
        if not self.is_initialized:
            return None
        
        try:
            return self.visualizer.plot_network(highlight_path)
        except Exception as e:
            st.error(f"Error al generar visualización: {str(e)}")
            return None
    
    def get_avl_visualization(self):
        """Obtiene la visualización del árbol AVL"""
        try:
            return self.visualizer.plot_avl_tree(self.route_registry)
        except Exception as e:
            st.error(f"Error al generar visualización AVL: {str(e)}")
            return None
    
    def get_clients_data(self):
        """Obtiene datos de clientes para visualización"""
        if not self.is_initialized:
            return []
        
        return [client.to_dict() for client in self.graph.clients.values()]
    
    def get_orders_data(self):
        """Obtiene datos de órdenes para visualización"""
        if not self.is_initialized:
            return []
        
        return [order.to_dict() for order in self.graph.orders]
    
    def get_route_analytics(self):
        """Obtiene análisis de rutas más frecuentes"""
        return self.route_registry.get_most_frequent_routes(20)
    
    def get_node_options(self):
        """Obtiene opciones de nodos para selectbox"""
        if not self.is_initialized:
            return []
        
        nodes = list(self.graph.nodes.keys())
        return [(node_id, f"{self.graph.nodes[node_id].type.value} {self.graph.nodes[node_id].name} (ID: {node_id})") 
                for node_id in nodes]
    
    def get_network_stats(self):
        """Obtiene estadísticas de la red"""
        if not self.is_initialized:
            return {}
        
        return self.graph.get_network_stats()
    
    def get_visit_statistics(self):
        """Obtiene estadísticas de visitas por tipo de nodo"""
        if not self.is_initialized:
            return {}, {}, {}
        
        storage_visits = {}
        charging_visits = {}
        client_visits = {}
        
        for node_id, node in self.graph.nodes.items():
            if node.visit_count > 0:
                if node.type == NodeType.STORAGE:
                    storage_visits[f"{node.type.value} {node.name}"] = node.visit_count
                elif node.type == NodeType.CHARGING:
                    charging_visits[f"{node.type.value} {node.name}"] = node.visit_count
                elif node.type == NodeType.CLIENT:
                    client_visits[f"{node.type.value} {node.name}"] = node.visit_count
        
        return storage_visits, charging_visits, client_visits

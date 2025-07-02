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
    
    def get_folium_map(self, highlight_path=None):
        """Obtiene el mapa de Folium con los nodos"""
        if not self.is_initialized:
            return None
        
        try:
            return self.visualizer.create_folium_map(highlight_path)
        except Exception as e:
            st.error(f"Error al generar mapa: {str(e)}")
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
    
    def get_visit_comparison_chart(self):
        """Genera gráfico de barras comparativo de nodos más visitados por tipo"""
        import matplotlib.pyplot as plt
        
        storage_visits, charging_visits, client_visits = self.get_visit_statistics()
        
        # Obtener top 3 de cada tipo
        top_storage = sorted(storage_visits.items(), key=lambda x: x[1], reverse=True)[:3]
        top_charging = sorted(charging_visits.items(), key=lambda x: x[1], reverse=True)[:3]
        top_clients = sorted(client_visits.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Si no hay datos suficientes, retornar None
        if not (top_storage or top_charging or top_clients):
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Preparar datos para el gráfico
        categories = []
        values = []
        colors = []
        
        # Agregar datos de almacenamiento
        for node, visits in top_storage:
            categories.append(f"📦 {node}")
            values.append(visits)
            colors.append('#FF6B6B')
        
        # Agregar datos de recarga
        for node, visits in top_charging:
            categories.append(f"🔋 {node}")
            values.append(visits)
            colors.append('#4ECDC4')
        
        # Agregar datos de clientes
        for node, visits in top_clients:
            categories.append(f"👤 {node}")
            values.append(visits)
            colors.append('#45B7D1')
        
        # Crear gráfico de barras
        bars = ax.bar(range(len(categories)), values, color=colors, alpha=0.8)
        
        # Configurar el gráfico
        ax.set_xlabel('Nodos por Tipo')
        ax.set_ylabel('Número de Visitas')
        ax.set_title('Comparación de Nodos Más Visitados por Tipo')
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        
        # Agregar valores sobre las barras
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{value}', ha='center', va='bottom', fontweight='bold')
        
        # Agregar leyenda
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#FF6B6B', alpha=0.8, label='📦 Almacenamiento'),
            plt.Rectangle((0,0),1,1, facecolor='#4ECDC4', alpha=0.8, label='🔋 Recarga'),
            plt.Rectangle((0,0),1,1, facecolor='#45B7D1', alpha=0.8, label='👤 Clientes')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def get_node_proportion_chart(self):
        """Genera gráfico de torta para proporción de nodos por rol"""
        import matplotlib.pyplot as plt
        
        if not self.is_initialized:
            return None
        
        stats = self.get_network_stats()
        if not stats:
            return None
        
        # Datos para el gráfico de torta
        labels = ['📦 Almacenamiento', '🔋 Recarga', '👤 Clientes']
        sizes = [
            stats['storage']['count'],
            stats['charging']['count'], 
            stats['client']['count']
        ]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        explode = (0.05, 0.05, 0.05)  # Separar un poco las secciones
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Crear gráfico de torta
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', explode=explode,
                                         shadow=True, startangle=90)
        
        # Configurar texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)
        
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        
        # Configurar el gráfico
        ax.set_title('Proporción de Nodos por Rol en la Red', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Agregar información adicional
        total_nodes = sum(sizes)
        ax.text(0, -1.3, f'Total de Nodos: {total_nodes}', 
               ha='center', fontsize=12, style='italic')
        
        plt.tight_layout()
        return fig

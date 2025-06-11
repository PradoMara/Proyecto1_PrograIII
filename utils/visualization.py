import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from models.node import NodeType

class NetworkVisualizer:
    """Clase para visualizar la red de drones"""
    
    def __init__(self, graph):
        self.graph = graph
        self.colors = {
            NodeType.STORAGE: '#FF6B6B',      # Rojo para almacenamiento
            NodeType.CHARGING: '#4ECDC4',    # Azul-verde para recarga
            NodeType.CLIENT: '#45B7D1'       # Azul para clientes
        }
        self.node_sizes = {
            NodeType.STORAGE: 800,
            NodeType.CHARGING: 600,
            NodeType.CLIENT: 400
        }
    
    def create_networkx_graph(self):
        """Crea un grafo NetworkX para visualización"""
        G = nx.Graph()
        
        # Agregar nodos con atributos
        for node_id, node in self.graph.nodes.items():
            G.add_node(node_id, 
                      type=node.type,
                      name=node.name,
                      pos=(node.x, node.y))
        
        # Agregar aristas
        for node_id, neighbors in self.graph.edges.items():
            for neighbor_id, weight in neighbors:
                if not G.has_edge(node_id, neighbor_id):
                    G.add_edge(node_id, neighbor_id, weight=weight)
        
        return G
    
    def plot_network(self, highlight_path=None, figsize=(12, 8)):
        """Visualiza la red completa"""
        G = self.create_networkx_graph()
        
        if not G.nodes():
            return None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Obtener posiciones de los nodos
        pos = nx.get_node_attributes(G, 'pos')
        if not pos:
            pos = nx.spring_layout(G, seed=42)
        
        # Preparar colores y tamaños por tipo
        node_colors = []
        node_sizes = []
        node_labels = {}
        
        for node_id in G.nodes():
            node = self.graph.nodes[node_id]
            node_colors.append(self.colors[node.type])
            node_sizes.append(self.node_sizes[node.type])
            node_labels[node_id] = f"{node.type.value}{node.name}"
        
        # Dibujar aristas normales
        edge_colors = ['gray' for _ in G.edges()]
        edge_widths = [1 for _ in G.edges()]
        
        # Resaltar camino si se proporciona
        if highlight_path and len(highlight_path) > 1:
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                         for i in range(len(highlight_path)-1)]
            
            for i, edge in enumerate(G.edges()):
                if edge in path_edges or edge[::-1] in path_edges:
                    edge_colors[i] = 'red'
                    edge_widths[i] = 3
        
        # Dibujar el grafo
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, 
                              width=edge_widths, alpha=0.6, ax=ax)
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8, ax=ax)
        
        nx.draw_networkx_labels(G, pos, node_labels, font_size=8, ax=ax)
        
        # Agregar pesos de aristas
        edge_labels = nx.get_edge_attributes(G, 'weight')
        edge_labels = {k: f"{v:.1f}" for k, v in edge_labels.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, ax=ax)
        
        # Configurar el plot
        ax.set_title("Red de Distribución de Drones", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # Agregar leyenda
        legend_elements = [
            plt.scatter([], [], c=self.colors[NodeType.STORAGE], s=100, 
                       label=f'{NodeType.STORAGE.value} Almacenamiento'),
            plt.scatter([], [], c=self.colors[NodeType.CHARGING], s=100, 
                       label=f'{NodeType.CHARGING.value} Recarga'),
            plt.scatter([], [], c=self.colors[NodeType.CLIENT], s=100, 
                       label=f'{NodeType.CLIENT.value} Cliente')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def plot_avl_tree(self, avl_tree, figsize=(12, 8)):
        """Visualiza el árbol AVL de rutas"""
        if not avl_tree.root:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No hay rutas registradas", 
                   ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        nodes, edges = avl_tree.get_tree_structure()
        
        if not nodes:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "Árbol AVL vacío", 
                   ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        # Crear grafo NetworkX para el árbol
        G = nx.DiGraph()
        
        for node_id, label in nodes:
            G.add_node(node_id, label=label)
        
        for parent, child in edges:
            G.add_edge(parent, child)
        
        # Usar layout jerárquico para árboles
        pos = self._hierarchical_layout(G)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Dibujar el árbol
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              arrows=True, arrowsize=20, ax=ax)
        
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=2000, alpha=0.8, ax=ax)
        
        # Agregar etiquetas personalizadas
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
        
        ax.set_title("Árbol AVL - Registro de Rutas", 
                    fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    def _hierarchical_layout(self, G):
        """Crea un layout jerárquico para visualizar el árbol"""
        if not G.nodes():
            return {}
        
        # Encontrar la raíz (nodo sin predecesores)
        roots = [n for n in G.nodes() if G.in_degree(n) == 0]
        if not roots:
            roots = [list(G.nodes())[0]]
        
        root = roots[0]
        
        # BFS para asignar niveles
        levels = {root: 0}
        queue = [root]
        max_level = 0
        
        while queue:
            node = queue.pop(0)
            level = levels[node]
            max_level = max(max_level, level)
            
            for child in G.successors(node):
                if child not in levels:
                    levels[child] = level + 1
                    queue.append(child)
        
        # Contar nodos por nivel
        level_counts = {}
        for node, level in levels.items():
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Asignar posiciones
        pos = {}
        level_indices = {level: 0 for level in range(max_level + 1)}
        
        for node in G.nodes():
            level = levels.get(node, 0)
            level_count = level_counts[level]
            index = level_indices[level]
            
            # Distribuir nodos horizontalmente en cada nivel
            if level_count == 1:
                x = 0
            else:
                x = (index / (level_count - 1)) * 2 - 1  # Entre -1 y 1
            
            y = max_level - level  # Niveles más altos arriba
            
            pos[node] = (x, y)
            level_indices[level] += 1
        
        return pos
    
    def create_statistics_plots(self, figsize=(15, 10)):
        """Crea gráficos estadísticos del sistema"""
        if not self.graph.nodes:
            return None
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 1. Distribución de tipos de nodos
        node_types = [node.type for node in self.graph.nodes.values()]
        type_counts = {}
        for node_type in [NodeType.STORAGE, NodeType.CHARGING, NodeType.CLIENT]:
            type_counts[node_type.value] = node_types.count(node_type)
        
        colors = [self.colors[NodeType.STORAGE], 
                 self.colors[NodeType.CHARGING], 
                 self.colors[NodeType.CLIENT]]
        
        ax1.pie(type_counts.values(), labels=type_counts.keys(), 
               colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Distribución de Tipos de Nodos")
        
        # 2. Nodos más visitados
        visited_counts = [(node.name, node.visit_count) 
                         for node in self.graph.nodes.values() 
                         if node.visit_count > 0]
        
        if visited_counts:
            visited_counts.sort(key=lambda x: x[1], reverse=True)
            top_visited = visited_counts[:10]
            
            names, counts = zip(*top_visited)
            ax2.bar(names, counts, color='skyblue')
            ax2.set_title("Nodos Más Visitados")
            ax2.set_xlabel("Nodos")
            ax2.set_ylabel("Visitas")
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, "No hay datos de visitas", 
                    ha='center', va='center', fontsize=12)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
        
        # 3. Estado de órdenes
        if self.graph.orders:
            order_statuses = [order.status for order in self.graph.orders]
            status_counts = {}
            for status in set(order_statuses):
                status_counts[status] = order_statuses.count(status)
            
            ax3.bar(status_counts.keys(), status_counts.values(), 
                   color=['green' if 'Entregado' in k else 'orange' for k in status_counts.keys()])
            ax3.set_title("Estado de Órdenes")
            ax3.set_xlabel("Estado")
            ax3.set_ylabel("Cantidad")
        else:
            ax3.text(0.5, 0.5, "No hay órdenes", 
                    ha='center', va='center', fontsize=12)
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
        
        # 4. Costos de rutas
        if self.graph.orders:
            completed_orders = [order for order in self.graph.orders 
                              if order.status == "Entregado" and order.total_cost > 0]
            
            if completed_orders:
                costs = [order.total_cost for order in completed_orders]
                ax4.hist(costs, bins=10, color='lightcoral', edgecolor='black')
                ax4.set_title("Distribución de Costos de Entrega")
                ax4.set_xlabel("Costo")
                ax4.set_ylabel("Frecuencia")
            else:
                ax4.text(0.5, 0.5, "No hay entregas completadas", 
                        ha='center', va='center', fontsize=12)
                ax4.set_xlim(0, 1)
                ax4.set_ylim(0, 1)
        else:
            ax4.text(0.5, 0.5, "No hay datos de costos", 
                    ha='center', va='center', fontsize=12)
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
        
        plt.tight_layout()
        return fig

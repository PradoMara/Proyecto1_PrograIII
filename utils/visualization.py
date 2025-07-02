import matplotlib.pyplot as plt
import networkx as nx
import folium
import random
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
            node_labels[node_id] = f"{node.name}"
        
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
                              node_size=1000, alpha=0.8, ax=ax)
        
        # Agregar etiquetas personalizadas
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=6, ax=ax)
        
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

    def create_folium_map(self, highlight_path=None):
        """Crea un mapa de Folium centrado en Temuco con los nodos de la red"""
        # Coordenadas de Temuco, Chile
        temuco_lat = -38.7359
        temuco_lon = -72.5904
        
        # Crear el mapa base centrado en Temuco
        m = folium.Map(
            location=[temuco_lat, temuco_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Definir colores para cada tipo de nodo
        color_map = {
            NodeType.STORAGE: 'red',
            NodeType.CHARGING: 'green', 
            NodeType.CLIENT: 'blue'
        }
        
        # Definir iconos para cada tipo de nodo
        icon_map = {
            NodeType.STORAGE: 'cube',
            NodeType.CHARGING: 'bolt',
            NodeType.CLIENT: 'user'
        }
        
        # Obtener límites de la ciudad de Temuco para distribuir los nodos
        lat_min, lat_max = temuco_lat - 0.03, temuco_lat + 0.03
        lon_min, lon_max = temuco_lon - 0.04, temuco_lon + 0.04
        
        # Mapear las coordenadas normalizadas a coordenadas geográficas de Temuco
        node_positions = {}
        for node_id, node in self.graph.nodes.items():
            # Normalizar las coordenadas x, y del rango 0-100 a un rango de 0 a 1
            normalized_x = node.x / 100.0  # Las coordenadas están entre 0 y 100
            normalized_y = node.y / 100.0  # Las coordenadas están entre 0 y 100
            
            # Mapear a las coordenadas de Temuco
            lat = lat_min + normalized_y * (lat_max - lat_min)
            lon = lon_min + normalized_x * (lon_max - lon_min)
            
            node_positions[node_id] = [lat, lon]
            
            # Crear marcador para el nodo
            folium.Marker(
                location=[lat, lon],
                popup=f"{node.type.value} {node.name}<br>ID: {node_id}<br>Visitas: {node.visit_count}",
                tooltip=f"{node.type.value} {node.name}",
                icon=folium.Icon(
                    color=color_map[node.type],
                    icon=icon_map[node.type],
                    prefix='fa'
                )
            ).add_to(m)
        
        # Agregar aristas como líneas en el mapa
        for node_id, neighbors in self.graph.edges.items():
            for neighbor_id, weight in neighbors:
                if node_id < neighbor_id:  # Evitar líneas duplicadas
                    start_pos = node_positions[node_id]
                    end_pos = node_positions[neighbor_id]
                    
                    # Color de la línea (rojo si está en el camino destacado)
                    line_color = 'red'
                    line_weight = 4
                    line_opacity = 0.8
                    
                    if highlight_path and len(highlight_path) > 1:
                        # Verificar si esta arista está en el camino destacado
                        is_in_path = False
                        for i in range(len(highlight_path) - 1):
                            if ((highlight_path[i] == node_id and highlight_path[i+1] == neighbor_id) or
                                (highlight_path[i] == neighbor_id and highlight_path[i+1] == node_id)):
                                is_in_path = True
                                break
                        
                        if not is_in_path:
                            line_color = 'blue'
                            line_weight = 2
                            line_opacity = 0.5
                    else:
                        line_color = 'blue'
                        line_weight = 2
                        line_opacity = 0.5
                    
                    folium.PolyLine(
                        locations=[start_pos, end_pos],
                        color=line_color,
                        weight=line_weight,
                        opacity=line_opacity,
                        popup=f"Peso: {weight}"
                    ).add_to(m)
        
        return m

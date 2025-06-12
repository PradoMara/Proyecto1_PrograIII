import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import math
import random

class NetworkXAdapter:
    def __init__(self, graph, node_types):
        self.graph = graph
        self.node_types = node_types
        self.nx_graph = None
        self.pos = None
        self.current_path = None
        
    def create_networkx_graph(self):
        """Convierte el grafo personalizado a NetworkX"""
        self.nx_graph = nx.Graph()
        
        # Agregar nodos
        for vertex in self.graph.vertices():
            self.nx_graph.add_node(str(vertex))
        
        # Agregar aristas
        for edge in self.graph.edges():
            u, v = edge.endpoints()
            weight = edge.element()
            self.nx_graph.add_edge(str(u), str(v), weight=weight)
        
        # Generar posiciones usando layout de fuerza
        self.pos = nx.spring_layout(self.nx_graph, k=3, iterations=50)
        
    def plot_network(self, figsize=(12, 8), highlight_path=None):
        """Dibuja la red completa con colores por tipo de nodo"""
        if not self.nx_graph:
            self.create_networkx_graph()
            
        fig, ax = plt.subplots(figsize=figsize)
        
        # Definir colores por tipo
        colors = {
            "📦 Almacenamiento": "#E74C3C",  # Rojo más fuerte
            "🔋 Recarga": "#2ECC71",        # Verde más fuerte
            "👤 Cliente": "#3498DB"         # Azul más fuerte
        }
        
        # Preparar nodos por tipo
        node_colors = []
        node_labels = {}
        
        for node_str in self.nx_graph.nodes():
            # Encontrar el vértice original
            original_vertex = None
            for vertex in self.graph.vertices():
                if str(vertex) == node_str:
                    original_vertex = vertex
                    break
            
            if original_vertex and original_vertex in self.node_types.keys():
                node_type = self.node_types[original_vertex]
                node_colors.append(colors.get(node_type, "#95A5A6"))
                
                # Crear etiqueta con emoji
                if node_type == "📦 Almacenamiento":
                    node_labels[node_str] = f"📦{node_str.split('_')[1]}"
                elif node_type == "🔋 Recarga":
                    node_labels[node_str] = f"🔋{node_str.split('_')[1]}"
                else:
                    node_labels[node_str] = f"👤{node_str.split('_')[1]}"
            else:
                node_colors.append("#95A5A6")
                node_labels[node_str] = node_str
        
        # Dibujar todas las aristas normales primero
        edge_colors = []
        edge_widths = []
        
        # Crear lista de aristas en la ruta destacada
        highlighted_edges = set()
        if highlight_path and len(highlight_path) > 1:
            for i in range(len(highlight_path) - 1):
                edge1 = (str(highlight_path[i]), str(highlight_path[i+1]))
                edge2 = (str(highlight_path[i+1]), str(highlight_path[i]))
                highlighted_edges.add(edge1)
                highlighted_edges.add(edge2)
        
        # Asignar colores y anchos a todas las aristas
        for edge in self.nx_graph.edges():
            if edge in highlighted_edges or (edge[1], edge[0]) in highlighted_edges:
                edge_colors.append("#E74C3C")  # Rojo brillante para la ruta
                edge_widths.append(4)
            else:
                edge_colors.append("#BDC3C7")  # Gris para aristas normales
                edge_widths.append(1)
        
        # Dibujar aristas
        nx.draw_networkx_edges(self.nx_graph, self.pos, 
                              edge_color=edge_colors, 
                              width=edge_widths, 
                              alpha=0.8, ax=ax)
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.nx_graph, self.pos, 
                              node_color=node_colors, 
                              node_size=1000, 
                              alpha=0.9, ax=ax)
        
        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(self.nx_graph, self.pos, 
                               node_labels, 
                               font_size=10, 
                               font_weight='bold', ax=ax)
        
        # Dibujar pesos de aristas
        edge_labels = {}
        for edge in self.graph.edges():
            u, v = edge.endpoints()
            weight = edge.element()
            edge_labels[(str(u), str(v))] = str(weight)
        
        nx.draw_networkx_edge_labels(self.nx_graph, self.pos, 
                                    edge_labels, 
                                    font_size=8, ax=ax)
        
        # Configurar el plot
        ax.set_title("Red de Drones - Correos Chile", 
                    fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # Crear leyenda
        legend_elements = [
            patches.Patch(color=colors["📦 Almacenamiento"], label="📦 Almacenamiento"),
            patches.Patch(color=colors["🔋 Recarga"], label="🔋 Recarga"),
            patches.Patch(color=colors["👤 Cliente"], label="👤 Cliente")
        ]
        
        if highlight_path and len(highlight_path) > 1:
            legend_elements.append(patches.Patch(color="#E74C3C", label="🛣️ Ruta Calculada"))
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
        
        plt.tight_layout()
        return fig
    
    def get_node_options(self, node_type_filter=None):
        """Retorna opciones de nodos para selectbox"""
        options = []
        
        for vertex in self.graph.vertices():
            if vertex in self.node_types.keys():
                vertex_type = self.node_types[vertex]
                
                if node_type_filter is None or vertex_type == node_type_filter:
                    # Crear nombres más descriptivos
                    node_id = str(vertex).split('_')[1] if '_' in str(vertex) else str(vertex)
                    
                    if vertex_type == "📦 Almacenamiento":
                        display_name = f"📦 Almacén {node_id}"
                    elif vertex_type == "🔋 Recarga":
                        display_name = f"🔋 Estación {node_id}"
                    else:
                        display_name = f"👤 Cliente {node_id}"
                    
                    options.append((str(vertex), display_name))
        
        return options

# Visualización Streamlit y adaptadores gráficos
# Adaptador de grafo → matplotlib

"""
Adaptador NetworkX para el Sistema de Grafos Conectados

Convierte grafos del TDA personalizado al formato NetworkX para facilitar
la visualización y análisis con herramientas estándar.
"""

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import sys
import os

from model.graph_base import Graph
from model.vertex_base import Vertex
from model.edge_base import Edge
from model.generador_grafo import RolNodo


# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NetworkXAdapter:
    """Adaptador para convertir grafos personalizados a NetworkX"""
    
    @staticmethod
    def convertir_a_networkx(grafo: Graph) -> nx.Graph:
        """
        Convierte un grafo del TDA personalizado a NetworkX
        
        Args:
            grafo: Grafo del TDA personalizado
            
        Returns:
            nx.Graph: Grafo en formato NetworkX
        """
        # Crear grafo NetworkX
        G = nx.Graph()
        
        # Agregar nodos con sus atributos
        for vertice in grafo.vertices():
            datos = vertice.element()
            G.add_node(
                datos.get('id', id(vertice)),
                **datos
            )
        
        # Agregar aristas con sus atributos
        for arista in grafo.edges():
            endpoints = arista.endpoints()
            v1_data = endpoints[0].element()
            v2_data = endpoints[1].element()
            edge_data = arista.element()
            
            G.add_edge(
                v1_data.get('id', id(endpoints[0])),
                v2_data.get('id', id(endpoints[1])),
                **edge_data
            )
        
        return G
    
    @staticmethod
    def crear_layout_interactivo(G: nx.Graph, layout_type: str = "spring") -> Dict[int, Tuple[float, float]]:
        """
        Crea un layout para visualización interactiva
        
        Args:
            G: Grafo NetworkX
            layout_type: Tipo de layout ("spring", "circular", "kamada_kawai", "random")
            
        Returns:
            Dict con posiciones de nodos
        """
        if len(G.nodes()) == 0:
            return {}
        
        if layout_type == "spring":
            return nx.spring_layout(G, k=1, iterations=50, seed=42)
        elif layout_type == "circular":
            return nx.circular_layout(G)
        elif layout_type == "kamada_kawai":
            return nx.kamada_kawai_layout(G)
        elif layout_type == "random":
            return nx.random_layout(G, seed=42)
        else:
            return nx.spring_layout(G, seed=42)
    
    @staticmethod
    def crear_visualizacion_plotly(G: nx.Graph, 
                                  pos: Optional[Dict] = None,
                                  resaltar_camino: Optional[List[int]] = None,
                                  titulo: str = "Grafo de Red") -> go.Figure:
        """
        Crea una visualización interactiva del grafo con Plotly
        
        Args:
            G: Grafo NetworkX
            pos: Posiciones de nodos (opcional)
            resaltar_camino: Lista de IDs de nodos para resaltar como ruta
            titulo: Título del gráfico
            
        Returns:
            go.Figure: Visualización Plotly del grafo
        """
        if len(G.nodes()) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay nodos para visualizar",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Calcular posiciones si no se proporcionan
        if pos is None:
            pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Crear trazos de aristas
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Información de la arista
            peso = G[edge[0]][edge[1]].get('weight', 1.0)
            edge_info.append(f"Arista {edge[0]} ↔ {edge[1]}<br>Peso: {peso:.2f}")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Crear trazos de aristas resaltadas si hay camino
        highlighted_edge_trace = None
        if resaltar_camino and len(resaltar_camino) > 1:
            highlight_edge_x = []
            highlight_edge_y = []
            
            for i in range(len(resaltar_camino) - 1):
                if resaltar_camino[i] in pos and resaltar_camino[i+1] in pos:
                    x0, y0 = pos[resaltar_camino[i]]
                    x1, y1 = pos[resaltar_camino[i+1]]
                    highlight_edge_x.extend([x0, x1, None])
                    highlight_edge_y.extend([y0, y1, None])
            
            highlighted_edge_trace = go.Scatter(
                x=highlight_edge_x, y=highlight_edge_y,
                line=dict(width=4, color='#FF4444'),
                hoverinfo='none',
                mode='lines',
                name='Ruta Resaltada'
            )
        
        # Preparar datos de nodos
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        node_info = []
        
        # Colores por rol
        color_map = {
            RolNodo.ALMACENAMIENTO: '#FF6B6B',
            RolNodo.RECARGA: '#4ECDC4',
            RolNodo.CLIENTE: '#45B7D1',
            'sin_rol': '#95A5A6'
        }
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Información del nodo
            node_data = G.nodes[node]
            nombre = node_data.get('nombre', f'Nodo {node}')
            rol = node_data.get('rol', 'sin_rol')
            grado = G.degree(node)
            
            node_text.append(str(node))
            node_colors.append(color_map.get(rol, color_map['sin_rol']))
            
            # Tamaño basado en grado
            base_size = 20
            size_multiplier = 1 + (grado * 0.3)
            node_sizes.append(base_size * size_multiplier)
            
            # Información hover
            info = (f"<b>{nombre}</b><br>"
                   f"ID: {node}<br>"
                   f"Rol: {rol.title()}<br>"
                   f"Grado: {grado}<br>"
                   f"Coordenadas: ({x:.2f}, {y:.2f})")
            node_info.append(info)
        
        # Resaltar camino si se proporciona
        if resaltar_camino:
            for i, node in enumerate(G.nodes()):
                if node in resaltar_camino:
                    # Hacer los nodos del camino más grandes y con borde destacado
                    node_sizes[i] *= 1.5
                    if node == resaltar_camino[0]:
                        node_colors[i] = '#00FF00'  # Verde para origen
                    elif node == resaltar_camino[-1]:
                        node_colors[i] = '#FF0000'  # Rojo para destino
                    else:
                        node_colors[i] = '#FFA500'  # Naranja para nodos intermedios
        
        # Crear trazo de nodos
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white'),
                opacity=0.8
            )
        )
        
        # Crear figura
        data = [edge_trace, node_trace]
        if highlighted_edge_trace:
            data.insert(1, highlighted_edge_trace)  # Insertar antes de los nodos
        
        fig = go.Figure(data=data)
        
        fig.update_layout(
            title=dict(text=titulo, font=dict(size=16)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[dict(
                text="Arrastra para mover | Zoom con rueda del mouse",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(size=12, color="#888")
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig
    
    @staticmethod
    def crear_matriz_adyacencia_heatmap(G: nx.Graph) -> go.Figure:
        """
        Crea un heatmap de la matriz de adyacencia
        
        Args:
            G: Grafo NetworkX
            
        Returns:
            go.Figure: Heatmap de la matriz de adyacencia
        """
        if len(G.nodes()) == 0:
            return go.Figure()
        
        # Obtener matriz de adyacencia
        matriz = nx.adjacency_matrix(G).todense()
        nodos = list(G.nodes())
        
        # Crear heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matriz,
            x=[f"Nodo {n}" for n in nodos],
            y=[f"Nodo {n}" for n in nodos],
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title="Matriz de Adyacencia",
            xaxis_title="Nodos",
            yaxis_title="Nodos",
            width=600,
            height=600
        )
        
        return fig
    
    @staticmethod
    def analizar_metricas_red(G: nx.Graph) -> Dict[str, Any]:
        """
        Calcula métricas avanzadas de la red
        
        Args:
            G: Grafo NetworkX
            
        Returns:
            Dict con métricas de la red
        """
        if len(G.nodes()) == 0:
            return {}
        
        metricas = {}
        
        try:
            # Métricas básicas
            metricas['num_nodos'] = G.number_of_nodes()
            metricas['num_aristas'] = G.number_of_edges()
            metricas['densidad'] = nx.density(G)
            
            # Métricas de conectividad
            metricas['conectado'] = nx.is_connected(G)
            metricas['num_componentes'] = nx.number_connected_components(G)
            
            if nx.is_connected(G):
                # Métricas solo para grafos conectados
                metricas['diametro'] = nx.diameter(G)
                metricas['radio'] = nx.radius(G)
                metricas['excentricidad_promedio'] = np.mean(list(nx.eccentricity(G).values()))
                
                # Centralidad
                centralidad_grado = nx.degree_centrality(G)
                centralidad_cercania = nx.closeness_centrality(G)
                centralidad_intermediacion = nx.betweenness_centrality(G)
                
                metricas['centralidad_grado_max'] = max(centralidad_grado.values())
                metricas['centralidad_cercania_max'] = max(centralidad_cercania.values())
                metricas['centralidad_intermediacion_max'] = max(centralidad_intermediacion.values())
                
                # Coeficiente de clustering
                metricas['clustering_promedio'] = nx.average_clustering(G)
            
            # Distribución de grados
            grados = [d for n, d in G.degree()]
            metricas['grado_promedio'] = np.mean(grados)
            metricas['grado_max'] = max(grados) if grados else 0
            metricas['grado_min'] = min(grados) if grados else 0
            metricas['grado_std'] = np.std(grados)
            
        except Exception as e:
            metricas['error'] = str(e)
        
        return metricas
    
    @staticmethod
    def crear_grafico_distribucion_grados(G: nx.Graph) -> go.Figure:
        """
        Crea un gráfico de la distribución de grados
        
        Args:
            G: Grafo NetworkX
            
        Returns:
            go.Figure: Gráfico de distribución de grados
        """
        if len(G.nodes()) == 0:
            return go.Figure()
        
        # Obtener distribución de grados
        grados = [d for n, d in G.degree()]
        
        # Crear histograma
        fig = go.Figure(data=[go.Histogram(
            x=grados,
            nbinsx=max(10, len(set(grados))),
            marker_color='lightblue',
            opacity=0.7
        )])
        
        fig.update_layout(
            title="Distribución de Grados",
            xaxis_title="Grado",
            yaxis_title="Frecuencia",
            bargap=0.1
        )
        
        return fig
    
    @staticmethod
    def resaltar_ruta_en_grafo(G: nx.Graph, ruta: List[int], 
                              pos: Optional[Dict] = None) -> go.Figure:
        """
        Crea una visualización del grafo resaltando una ruta específica
        
        Args:
            G: Grafo NetworkX
            ruta: Lista de IDs de nodos que forman la ruta
            pos: Posiciones de nodos (opcional)
            
        Returns:
            go.Figure: Visualización con ruta resaltada
        """
        fig = NetworkXAdapter.crear_visualizacion_plotly(
            G, pos, resaltar_camino=ruta, 
            titulo=f"Ruta Resaltada ({len(ruta)} nodos)"
        )
        
        # Agregar información de la ruta
        if len(ruta) > 1:
            fig.add_annotation(
                text=f"Ruta: {' → '.join(map(str, ruta))}",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                xanchor='left', yanchor='top',
                showarrow=False,
                font=dict(size=12, color="black"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1
            )
        
        return fig

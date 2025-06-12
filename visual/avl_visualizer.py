import streamlit as st
import matplotlib.pyplot as plt

class AVLVisualizer:
    def __init__(self, avl_root):
        self.root = avl_root
    
    def draw_avl_tree(self):
        """Dibuja gráficamente el árbol AVL"""
        if not self.root:
            st.info("No hay rutas registradas aún.")
            return None
            
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Calcular posiciones de nodos
        positions = {}
        self._calculate_positions(self.root, 0, 0, 6, positions)
        
        # Dibujar aristas
        self._draw_edges(self.root, positions, ax)
        
        # Dibujar nodos
        for node, (x, y) in positions.items():
            circle = plt.Circle((x, y), 0.3, color='lightblue', ec='black')
            ax.add_patch(circle)
            ax.text(x, y, str(node.key)[:10], ha='center', va='center', fontsize=8, weight='bold')
        
        ax.set_xlim(-7, 7)
        ax.set_ylim(-5, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title("Árbol AVL - Rutas Más Frecuentes", fontsize=14, weight='bold')
        
        return fig
    
    def _calculate_positions(self, node, x, y, width, positions):
        """Calcula posiciones para los nodos del árbol"""
        if node is None:
            return
            
        positions[node] = (x, y)
        
        if node.left:
            self._calculate_positions(node.left, x - width/2, y - 1, width/2, positions)
        
        if node.right:
            self._calculate_positions(node.right, x + width/2, y - 1, width/2, positions)
    
    def _draw_edges(self, node, positions, ax):
        """Dibuja las aristas del árbol"""
        if node is None:
            return
            
        x, y = positions[node]
        
        if node.left:
            left_x, left_y = positions[node.left]
            ax.plot([x, left_x], [y, left_y], 'k-', alpha=0.6)
            self._draw_edges(node.left, positions, ax)
        
        if node.right:
            right_x, right_y = positions[node.right]
            ax.plot([x, right_x], [y, right_y], 'k-', alpha=0.6)
            self._draw_edges(node.right, positions, ax)

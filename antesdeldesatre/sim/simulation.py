

from model import Graph
from typing import Dict, List, Optional

def buscar_vertice_por_nombre(grafo: Graph, nombre: str):

    for vertice in grafo.vertices():
        if vertice.element().get('nombre') == nombre:
            return vertice
    return None


def obtener_vecinos(grafo: Graph, vertex):

    return list(grafo.neighbors(vertex))


def validar_conectividad(grafo: Graph) -> bool:
   
    vertices = list(grafo.vertices())
    if len(vertices) <= 1:
        return True
    
    visitados = set()
    pila = [vertices[0]]
    
    while pila:
        v_actual = pila.pop()
        if v_actual not in visitados:
            visitados.add(v_actual)
            for vecino in grafo.neighbors(v_actual):
                if vecino not in visitados:
                    pila.append(vecino)
    
    return len(visitados) == len(vertices)

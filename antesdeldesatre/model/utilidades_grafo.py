# Utilidades modulares para trabajar con grafos
# Clases independientes que proporcionan funcionalidades reutilizables

from typing import List, Dict, Set, Optional, Tuple, Any
from .graph_base import Graph
from .vertex_base import Vertex
from .edge_base import Edge
import heapq


class ConsultorGrafo:
    @staticmethod
    def buscar_vertice_por_nombre(grafo: Graph, nombre: str) -> Optional[Vertex]:
    
        for vertice in grafo.vertices():
            if vertice.element().get('nombre') == nombre:
                return vertice
        return None
    
    @staticmethod
    def buscar_vertice_por_id(grafo: Graph, id_vertice: int) -> Optional[Vertex]:
    
        for vertice in grafo.vertices():
            if vertice.element().get('id') == id_vertice:
                return vertice
        return None
    
    @staticmethod
    def buscar_vertices_por_atributo(grafo: Graph, atributo: str, valor: Any) -> List[Vertex]:

        return [v for v in grafo.vertices() if v.element().get(atributo) == valor]
    
    @staticmethod
    def obtener_vecinos(grafo: Graph, vertice: Vertex) -> List[Vertex]:

        return list(grafo.neighbors(vertice))
    
    @staticmethod
    def obtener_grado(grafo: Graph, vertice: Vertex) -> int:
        
        return grafo.degree(vertice)
    
    @staticmethod
    def obtener_aristas_incidentes(grafo: Graph, vertice: Vertex) -> List[Edge]:
        
        return list(grafo.incident_edges(vertice))
    
    @staticmethod
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
    
    @staticmethod
    def obtener_componentes_conexas(grafo: Graph) -> List[List[Vertex]]:
        
        vertices = list(grafo.vertices())
        visitados = set()
        componentes = []
        
        for vertice in vertices:
            if vertice not in visitados:
                componente = []
                pila = [vertice]
                
                while pila:
                    v_actual = pila.pop()
                    if v_actual not in visitados:
                        visitados.add(v_actual)
                        componente.append(v_actual)
                        for vecino in grafo.neighbors(v_actual):
                            if vecino not in visitados:
                                pila.append(vecino)
                
                componentes.append(componente)
        
        return componentes


class CalculadorDistancias:
   
    @staticmethod
    def dijkstra(grafo: Graph, origen: Vertex) -> Tuple[Dict[Vertex, float], Dict[Vertex, Optional[Vertex]]]:
      
        distancias = {v: float('inf') for v in grafo.vertices()}
        predecesores = {v: None for v in grafo.vertices()}
        distancias[origen] = 0
        
        # cola de prioridad: distancia, id_unico, vertice
        
        heap = [(0, 0, origen)]
        visitados = set()
        contador = 1
        
        while heap:
            dist_actual, _, v_actual = heapq.heappop(heap)
            
            if v_actual in visitados:
                continue
            
            visitados.add(v_actual)
            
            # examinar vecinos
            for arista in grafo.incident_edges(v_actual):
                vecino = arista.opposite(v_actual)
                peso = arista.element().get('peso', 1.0)
                nueva_distancia = dist_actual + peso
                
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    predecesores[vecino] = v_actual
                    heapq.heappush(heap, (nueva_distancia, contador, vecino))
                    contador += 1
        
        return distancias, predecesores
    
    @staticmethod
    def reconstruir_camino(predecesores: Dict[Vertex, Optional[Vertex]], origen: Vertex, destino: Vertex) -> Optional[List[Vertex]]:
       
        if predecesores[destino] is None and destino != origen:
            return None  # no hay camino
        
        camino = []
        actual = destino
        
        while actual is not None:
            camino.append(actual)
            actual = predecesores[actual]
        
        camino.reverse()
        return camino if camino[0] == origen else None
    
    @staticmethod
    def calcular_distancia_entre(grafo: Graph, origen: Vertex, destino: Vertex) -> Optional[float]:
       
        distancias, _ = CalculadorDistancias.dijkstra(grafo, origen)
        dist = distancias.get(destino, float('inf'))
        return dist if dist != float('inf') else None
    
    @staticmethod
    def encontrar_camino_mas_corto(grafo: Graph, origen: Vertex, destino: Vertex) -> Optional[Tuple[List[Vertex], float]]:
        
        distancias, predecesores = CalculadorDistancias.dijkstra(grafo, origen)
        
        if distancias[destino] == float('inf'):
            return None
        
        camino = CalculadorDistancias.reconstruir_camino(predecesores, origen, destino)
        if camino is None:
            return None
        
        return camino, distancias[destino]


class BuscadorNodos:
    
    @staticmethod
    def buscar_nodos_por_rol(grafo: Graph, rol: str) -> List[Vertex]:
       
        return ConsultorGrafo.buscar_vertices_por_atributo(grafo, 'rol', rol)
    
    @staticmethod
    def buscar_nodo_mas_cercano_por_rol(grafo: Graph, origen: Vertex, rol: str) -> Optional[Tuple[Vertex, float]]:
        
        nodos_con_rol = BuscadorNodos.buscar_nodos_por_rol(grafo, rol)
        
        if not nodos_con_rol:
            return None
        
        
        distancias, _ = CalculadorDistancias.dijkstra(grafo, origen)
        
        
        nodo_mas_cercano = None
        distancia_minima = float('inf')
        
        for nodo in nodos_con_rol:
            if nodo == origen:  # El origen ya tiene el rol buscado
                return nodo, 0.0
            
            distancia = distancias.get(nodo, float('inf'))
            if distancia < distancia_minima:
                distancia_minima = distancia
                nodo_mas_cercano = nodo
        
        if nodo_mas_cercano is not None and distancia_minima != float('inf'):
            return nodo_mas_cercano, distancia_minima
        
        return None
    
    @staticmethod
    def buscar_k_nodos_mas_cercanos_por_rol(grafo: Graph, origen: Vertex, rol: str, k: int) -> List[Tuple[Vertex, float]]:
       
        nodos_con_rol = BuscadorNodos.buscar_nodos_por_rol(grafo, rol)
        
        if not nodos_con_rol:
            return []
        
       
        distancias, _ = CalculadorDistancias.dijkstra(grafo, origen)
        
       
        candidatos = []
        for nodo in nodos_con_rol:
            if nodo == origen:  # El origen ya tiene el rol buscado
                candidatos.append((nodo, 0.0))
            else:
                distancia = distancias.get(nodo, float('inf'))
                if distancia != float('inf'):
                    candidatos.append((nodo, distancia))
        
        
        candidatos.sort(key=lambda x: x[1])
        return candidatos[:k]
    
    @staticmethod
    def obtener_estadisticas_roles(grafo: Graph) -> Dict[str, Dict[str, Any]]:
       
        vertices = list(grafo.vertices())
        total_vertices = len(vertices)
        
        estadisticas = {}
        
      
        por_rol = {}
        for v in vertices:
            rol = v.element().get('rol', 'sin_rol')
            if rol not in por_rol:
                por_rol[rol] = []
            por_rol[rol].append(v)
        
        
        for rol, nodos in por_rol.items():
            cantidad = len(nodos)
            porcentaje = (cantidad / total_vertices) * 100 if total_vertices > 0 else 0
            
           
            grados = [grafo.degree(nodo) for nodo in nodos]
            grado_promedio = sum(grados) / len(grados) if grados else 0
            grado_max = max(grados) if grados else 0
            grado_min = min(grados) if grados else 0
            
            estadisticas[rol] = {
                'cantidad': cantidad,
                'porcentaje': round(porcentaje, 2),
                'grado_promedio': round(grado_promedio, 2),
                'grado_maximo': grado_max,
                'grado_minimo': grado_min,
                'nodos': nodos
            }
        
        return estadisticas

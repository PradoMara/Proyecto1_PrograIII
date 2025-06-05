# Generador modular de grafos conectados con roles asignados

import random
from typing import List, Dict, Set, Optional
from .graph_base import Graph
from .vertex_base import Vertex


class RolNodo:
    ALMACENAMIENTO = "almacenamiento"
    RECARGA = "recarga" 
    CLIENTE = "cliente"
    
    @classmethod
    def todos_los_roles(cls) -> List[str]:
        return [cls.ALMACENAMIENTO, cls.RECARGA, cls.CLIENTE]


class ConfiguracionRoles:
    
    def __init__(self, almacenamiento: float = 0.2, recarga: float = 0.3, cliente: float = 0.5):
       
        if abs(almacenamiento + recarga + cliente - 1.0) > 0.001:
            raise ValueError("Los porcentajes deben sumar 1.0")
            
        self.almacenamiento = almacenamiento
        self.recarga = recarga
        self.cliente = cliente
    
    def calcular_cantidad_nodos(self, total_nodos: int) -> Dict[str, int]:
        # Caso especial: con un solo nodo, asignar al rol con mayor porcentaje
        if total_nodos == 1:
            # Encontrar el rol con mayor porcentaje
            if self.cliente >= self.recarga and self.cliente >= self.almacenamiento:
                return {RolNodo.ALMACENAMIENTO: 0, RolNodo.RECARGA: 0, RolNodo.CLIENTE: 1}
            elif self.recarga >= self.almacenamiento:
                return {RolNodo.ALMACENAMIENTO: 0, RolNodo.RECARGA: 1, RolNodo.CLIENTE: 0}
            else:
                return {RolNodo.ALMACENAMIENTO: 1, RolNodo.RECARGA: 0, RolNodo.CLIENTE: 0}
        
        # Para múltiples nodos, garantizar al menos 1 de almacenamiento y recarga
        n_alm = max(1, round(total_nodos * self.almacenamiento))
        n_rec = max(1, round(total_nodos * self.recarga))
        n_cli = max(0, total_nodos - n_alm - n_rec)
        
        return {
            RolNodo.ALMACENAMIENTO: n_alm,
            RolNodo.RECARGA: n_rec,
            RolNodo.CLIENTE: n_cli
        }


class GeneradorGrafoConectado:

    
    def __init__(self, configuracion_roles: Optional[ConfiguracionRoles] = None):
        self.configuracion_roles = configuracion_roles or ConfiguracionRoles()
        self._semilla_aleatoria = None
    
    def establecer_semilla(self, semilla: int):
        self._semilla_aleatoria = semilla
        random.seed(semilla)
    
    def crear_grafo_conectado(self, numero_nodos: int, probabilidad_arista: float = 0.3) -> Graph:
        self._validar_parametros(numero_nodos, probabilidad_arista)
        
        if self._semilla_aleatoria is not None:
            random.seed(self._semilla_aleatoria)
        
        grafo = Graph(directed=False)
        
        vertices = self._crear_vertices_con_roles(grafo, numero_nodos)
        
        
        if len(vertices) > 1:
            self._crear_arbol_expansion(grafo, vertices)
        
        self._agregar_aristas_adicionales(grafo, vertices, probabilidad_arista)
        
        return grafo
    
    def crear_grafo_con_roles_personalizados(self, distribución_roles: Dict[str, int], probabilidad_arista: float = 0.3) -> Graph:
        
        total_nodos = sum(distribución_roles.values())
        if total_nodos < 1:
            raise ValueError("Debe haber al menos un nodo")
        
        grafo = Graph(directed=False)
        vertices = self._crear_vertices_con_distribución(grafo, distribución_roles)
        
        if len(vertices) > 1:
            self._crear_arbol_expansion(grafo, vertices)
        
        self._agregar_aristas_adicionales(grafo, vertices, probabilidad_arista)
        
        return grafo
    
    def _validar_parametros(self, numero_nodos: int, probabilidad_arista: float):
        if numero_nodos < 1:
            raise ValueError("El número de nodos debe ser mayor a 0")
        if not 0.0 <= probabilidad_arista <= 1.0:
            raise ValueError("La probabilidad de arista debe estar entre 0.0 y 1.0")
    
    def _crear_vertices_con_roles(self, grafo: Graph, numero_nodos: int) -> List[Vertex]:
        distribución = self.configuracion_roles.calcular_cantidad_nodos(numero_nodos)
        return self._crear_vertices_con_distribución(grafo, distribución)
    
    def _crear_vertices_con_distribución(self, grafo: Graph, distribución_roles: Dict[str, int]) -> List[Vertex]:

        vertices = []
        contador_id = 0
        
        lista_roles = []
        for rol, cantidad in distribución_roles.items():
            lista_roles.extend([rol] * cantidad)
        
        random.shuffle(lista_roles)
        
        for rol in lista_roles:
            datos = {
                'id': contador_id,
                'rol': rol,
                'nombre': f"{rol}_{contador_id}",
                'propiedades': {}  
            }
            vertice = grafo.insert_vertex(datos)
            vertices.append(vertice)
            contador_id += 1
            
        return vertices
    
    def _crear_arbol_expansion(self, grafo: Graph, vertices: List[Vertex]):
        if len(vertices) < 2:
            return
        
        no_conectados = vertices[1:]
        conectados = [vertices[0]]
        
        while no_conectados:
            v_conectado = random.choice(conectados)
            v_nuevo = random.choice(no_conectados)
            
            peso = round(random.uniform(1.0, 10.0), 2)
            datos_arista = {
                'peso': peso, 
                'tipo': 'expansion',
                'creado_en': 'generacion'
            }
            grafo.insert_edge(v_conectado, v_nuevo, datos_arista)
            
            conectados.append(v_nuevo)
            no_conectados.remove(v_nuevo)
    
    def _agregar_aristas_adicionales(self, grafo: Graph, vertices: List[Vertex], probabilidad: float):
        if probabilidad <= 0.0:
            return
        
        n = len(vertices)
        for i in range(n):
            for j in range(i + 1, n):
                v1, v2 = vertices[i], vertices[j]
                
                if not grafo.get_edge(v1, v2) and random.random() < probabilidad:
                    peso = round(random.uniform(1.0, 10.0), 2)
                    datos_arista = {
                        'peso': peso, 
                        'tipo': 'adicional',
                        'creado_en': 'generacion'
                    }
                    grafo.insert_edge(v1, v2, datos_arista)
    
    def obtener_estadisticas_grafo(self, grafo: Graph) -> Dict:
        vertices = list(grafo.vertices())
        aristas = list(grafo.edges())
        
        conteo_roles = {}
        for v in vertices:
            rol = v.element()['rol']
            conteo_roles[rol] = conteo_roles.get(rol, 0) + 1
        
        n = len(vertices)
        max_aristas = n * (n - 1) // 2
        densidad = len(aristas) / max_aristas if max_aristas > 0 else 0
        
        return {
            'numero_vertices': len(vertices),
            'numero_aristas': len(aristas),
            'densidad': round(densidad, 3),
            'distribución_roles': conteo_roles,
            'esta_conectado': self._verificar_conectividad(grafo),
            'grado_promedio': round(2 * len(aristas) / len(vertices), 2) if vertices else 0
        }
    
    def _verificar_conectividad(self, grafo: Graph) -> bool:
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
    
    def imprimir_resumen_grafo(self, grafo: Graph):
        stats = self.obtener_estadisticas_grafo(grafo)
        
        print("=" * 50)
        print("RESUMEN DEL GRAFO GENERADO")
        print("=" * 50)
        print(f"Número de vértices: {stats['numero_vertices']}")
        print(f"Número de aristas: {stats['numero_aristas']}")
        print(f"Densidad del grafo: {stats['densidad']}")
        print(f"Grado promedio: {stats['grado_promedio']}")
        print(f"¿Está conectado?: {'Sí' if stats['esta_conectado'] else 'No'}")
        
        print("\nDistribución de roles:")
        total_vertices = stats['numero_vertices']
        for rol, cantidad in stats['distribución_roles'].items():
            porcentaje = (cantidad / total_vertices) * 100 if total_vertices > 0 else 0
            print(f"  • {rol}: {cantidad} nodos ({porcentaje:.1f}%)")
        
        print("=" * 50)

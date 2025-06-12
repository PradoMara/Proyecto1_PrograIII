"""
Pruebas unitarias para el módulo utilidades_grafo.py

Estas pruebas cubren:
- ConsultorGrafo: Búsquedas, navegación y análisis de conectividad
- CalculadorDistancias: Algoritmo Dijkstra y cálculo de caminos
- BuscadorNodos: Búsquedas especializadas por roles y estadísticas
"""

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model.utilidades_grafo import ConsultorGrafo, CalculadorDistancias, BuscadorNodos
from model.generador_grafo import GeneradorGrafoConectado, RolNodo, ConfiguracionRoles
from model.graph_base import Graph
from model.vertex_base import Vertex


class TestConsultorGrafo(unittest.TestCase):
    """Pruebas para la clase ConsultorGrafo"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.grafo = Graph(directed=False)
        
        # Crear algunos vértices de prueba
        self.v1 = self.grafo.insert_vertex({
            'id': 1, 'nombre': 'nodo_1', 'rol': 'almacenamiento', 'activo': True
        })
        self.v2 = self.grafo.insert_vertex({
            'id': 2, 'nombre': 'nodo_2', 'rol': 'recarga', 'activo': False
        })
        self.v3 = self.grafo.insert_vertex({
            'id': 3, 'nombre': 'nodo_3', 'rol': 'cliente', 'activo': True
        })
        self.v4 = self.grafo.insert_vertex({
            'id': 4, 'nombre': 'nodo_4', 'rol': 'almacenamiento', 'activo': True
        })
        
        # Crear algunas aristas
        self.grafo.insert_edge(self.v1, self.v2, {'peso': 5.0})
        self.grafo.insert_edge(self.v2, self.v3, {'peso': 3.0})
        self.grafo.insert_edge(self.v1, self.v4, {'peso': 2.0})
    
    def test_buscar_vertice_por_nombre_existente(self):
        """Verifica la búsqueda de vértice por nombre existente"""
        resultado = ConsultorGrafo.buscar_vertice_por_nombre(self.grafo, 'nodo_2')
        
        self.assertEqual(resultado, self.v2)
        self.assertEqual(resultado.element()['nombre'], 'nodo_2')
    
    def test_buscar_vertice_por_nombre_inexistente(self):
        """Verifica la búsqueda de vértice por nombre inexistente"""
        resultado = ConsultorGrafo.buscar_vertice_por_nombre(self.grafo, 'nodo_inexistente')
        self.assertIsNone(resultado)
    
    def test_buscar_vertice_por_id_existente(self):
        """Verifica la búsqueda de vértice por ID existente"""
        resultado = ConsultorGrafo.buscar_vertice_por_id(self.grafo, 3)
        
        self.assertEqual(resultado, self.v3)
        self.assertEqual(resultado.element()['id'], 3)
    
    def test_buscar_vertice_por_id_inexistente(self):
        """Verifica la búsqueda de vértice por ID inexistente"""
        resultado = ConsultorGrafo.buscar_vertice_por_id(self.grafo, 999)
        self.assertIsNone(resultado)
    
    def test_buscar_vertices_por_atributo_rol(self):
        """Verifica la búsqueda por atributo rol"""
        resultado = ConsultorGrafo.buscar_vertices_por_atributo(self.grafo, 'rol', 'almacenamiento')
        
        self.assertEqual(len(resultado), 2)
        self.assertIn(self.v1, resultado)
        self.assertIn(self.v4, resultado)
    
    def test_buscar_vertices_por_atributo_activo(self):
        """Verifica la búsqueda por atributo booleano"""
        resultado = ConsultorGrafo.buscar_vertices_por_atributo(self.grafo, 'activo', True)
        
        self.assertEqual(len(resultado), 3)
        self.assertIn(self.v1, resultado)
        self.assertIn(self.v3, resultado)
        self.assertIn(self.v4, resultado)
    
    def test_buscar_vertices_por_atributo_inexistente(self):
        """Verifica la búsqueda por valor de atributo inexistente"""
        resultado = ConsultorGrafo.buscar_vertices_por_atributo(self.grafo, 'rol', 'inexistente')
        self.assertEqual(len(resultado), 0)
    
    def test_obtener_vecinos(self):
        """Verifica la obtención de vecinos de un vértice"""
        vecinos_v1 = ConsultorGrafo.obtener_vecinos(self.grafo, self.v1)
        vecinos_v2 = ConsultorGrafo.obtener_vecinos(self.grafo, self.v2)
        
        # v1 está conectado a v2 y v4
        self.assertEqual(len(vecinos_v1), 2)
        self.assertIn(self.v2, vecinos_v1)
        self.assertIn(self.v4, vecinos_v1)
        
        # v2 está conectado a v1 y v3
        self.assertEqual(len(vecinos_v2), 2)
        self.assertIn(self.v1, vecinos_v2)
        self.assertIn(self.v3, vecinos_v2)
    
    def test_obtener_grado(self):
        """Verifica el cálculo del grado de los vértices"""
        self.assertEqual(ConsultorGrafo.obtener_grado(self.grafo, self.v1), 2)
        self.assertEqual(ConsultorGrafo.obtener_grado(self.grafo, self.v2), 2)
        self.assertEqual(ConsultorGrafo.obtener_grado(self.grafo, self.v3), 1)
        self.assertEqual(ConsultorGrafo.obtener_grado(self.grafo, self.v4), 1)
    
    def test_obtener_aristas_incidentes(self):
        """Verifica la obtención de aristas incidentes"""
        aristas_v1 = ConsultorGrafo.obtener_aristas_incidentes(self.grafo, self.v1)
        aristas_v3 = ConsultorGrafo.obtener_aristas_incidentes(self.grafo, self.v3)
        
        self.assertEqual(len(aristas_v1), 2)  # v1 tiene 2 aristas
        self.assertEqual(len(aristas_v3), 1)  # v3 tiene 1 arista
    
    def test_validar_conectividad_grafo_conectado(self):
        """Verifica la validación de conectividad en grafo conectado"""
        # El grafo de prueba está conectado
        self.assertTrue(ConsultorGrafo.validar_conectividad(self.grafo))
    
    def test_validar_conectividad_grafo_desconectado(self):
        """Verifica la validación de conectividad en grafo desconectado"""
        # Crear un vértice aislado
        v_aislado = self.grafo.insert_vertex({'id': 5, 'nombre': 'aislado'})
        
        # Ahora el grafo no debe estar conectado
        self.assertFalse(ConsultorGrafo.validar_conectividad(self.grafo))
    
    def test_validar_conectividad_casos_especiales(self):
        """Verifica casos especiales de conectividad"""
        # Grafo con un solo vértice
        grafo_uno = Graph(directed=False)
        v_unico = grafo_uno.insert_vertex({'id': 1})
        self.assertTrue(ConsultorGrafo.validar_conectividad(grafo_uno))
        
        # Grafo vacío
        grafo_vacio = Graph(directed=False)
        self.assertTrue(ConsultorGrafo.validar_conectividad(grafo_vacio))
    
    def test_obtener_componentes_conexas_grafo_conectado(self):
        """Verifica componentes conexas en grafo conectado"""
        componentes = ConsultorGrafo.obtener_componentes_conexas(self.grafo)
        
        # Debe haber una sola componente con todos los vértices
        self.assertEqual(len(componentes), 1)
        self.assertEqual(len(componentes[0]), 4)
    
    def test_obtener_componentes_conexas_grafo_desconectado(self):
        """Verifica componentes conexas en grafo desconectado"""
        # Crear dos vértices aislados
        v5 = self.grafo.insert_vertex({'id': 5, 'nombre': 'aislado_1'})
        v6 = self.grafo.insert_vertex({'id': 6, 'nombre': 'aislado_2'})
        self.grafo.insert_edge(v5, v6, {'peso': 1.0})
        
        componentes = ConsultorGrafo.obtener_componentes_conexas(self.grafo)
        
        # Debe haber dos componentes
        self.assertEqual(len(componentes), 2)
        
        # Una componente con 4 vértices, otra con 2
        tamaños = sorted([len(comp) for comp in componentes])
        self.assertEqual(tamaños, [2, 4])


class TestCalculadorDistancias(unittest.TestCase):
    """Pruebas para la clase CalculadorDistancias"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.grafo = Graph(directed=False)
        
        # Crear un grafo de prueba más complejo
        #     v1 ---- v2
        #     |   \   |
        #     |    \  |
        #     v4 --- v3
        
        self.v1 = self.grafo.insert_vertex({'id': 1, 'nombre': 'A'})
        self.v2 = self.grafo.insert_vertex({'id': 2, 'nombre': 'B'})
        self.v3 = self.grafo.insert_vertex({'id': 3, 'nombre': 'C'})
        self.v4 = self.grafo.insert_vertex({'id': 4, 'nombre': 'D'})
        
        # Aristas con pesos específicos
        self.grafo.insert_edge(self.v1, self.v2, {'peso': 4.0})
        self.grafo.insert_edge(self.v1, self.v3, {'peso': 8.0})
        self.grafo.insert_edge(self.v1, self.v4, {'peso': 1.0})
        self.grafo.insert_edge(self.v2, self.v3, {'peso': 2.0})
        self.grafo.insert_edge(self.v3, self.v4, {'peso': 3.0})
    
    def test_dijkstra_desde_origen(self):
        """Verifica el algoritmo Dijkstra desde un vértice origen"""
        distancias, predecesores = CalculadorDistancias.dijkstra(self.grafo, self.v1)
        
        # Verificar distancias calculadas
        self.assertEqual(distancias[self.v1], 0.0)    # Distancia a sí mismo
        self.assertEqual(distancias[self.v2], 4.0)    # v1 -> v2 directamente
        self.assertEqual(distancias[self.v3], 4.0)    # v1 -> v4 -> v3 (1+3=4) es mejor que v1 -> v3 (8)
        self.assertEqual(distancias[self.v4], 1.0)    # v1 -> v4 directamente
        
        # Verificar predecesores
        self.assertIsNone(predecesores[self.v1])      # Origen no tiene predecesor
        self.assertEqual(predecesores[self.v2], self.v1)  # v2 viene de v1
        self.assertEqual(predecesores[self.v3], self.v4)  # v3 viene de v4
        self.assertEqual(predecesores[self.v4], self.v1)  # v4 viene de v1
    
    def test_dijkstra_grafo_desconectado(self):
        """Verifica Dijkstra en grafo con componentes desconectadas"""
        # Agregar un vértice aislado
        v_aislado = self.grafo.insert_vertex({'id': 5, 'nombre': 'E'})
        
        distancias, predecesores = CalculadorDistancias.dijkstra(self.grafo, self.v1)
        
        # El vértice aislado debe tener distancia infinita
        self.assertEqual(distancias[v_aislado], float('inf'))
        self.assertIsNone(predecesores[v_aislado])
    
    def test_reconstruir_camino_exitoso(self):
        """Verifica la reconstrucción exitosa de caminos"""
        distancias, predecesores = CalculadorDistancias.dijkstra(self.grafo, self.v1)
        
        # Camino de v1 a v3
        camino = CalculadorDistancias.reconstruir_camino(predecesores, self.v1, self.v3)
        
        self.assertIsNotNone(camino)
        self.assertEqual(camino[0], self.v1)  # Empieza en origen
        self.assertEqual(camino[-1], self.v3) # Termina en destino
        self.assertEqual(camino, [self.v1, self.v4, self.v3])  # Camino más corto
    
    def test_reconstruir_camino_mismo_vertice(self):
        """Verifica la reconstrucción de camino al mismo vértice"""
        distancias, predecesores = CalculadorDistancias.dijkstra(self.grafo, self.v1)
        
        camino = CalculadorDistancias.reconstruir_camino(predecesores, self.v1, self.v1)
        
        self.assertIsNotNone(camino)
        self.assertEqual(camino, [self.v1])
    
    def test_reconstruir_camino_inalcanzable(self):
        """Verifica la reconstrucción de camino a vértice inalcanzable"""
        v_aislado = self.grafo.insert_vertex({'id': 5, 'nombre': 'E'})
        
        distancias, predecesores = CalculadorDistancias.dijkstra(self.grafo, self.v1)
        
        camino = CalculadorDistancias.reconstruir_camino(predecesores, self.v1, v_aislado)
        self.assertIsNone(camino)
    
    def test_calcular_distancia_entre_vertices(self):
        """Verifica el cálculo directo de distancia entre vértices"""
        # Distancia directa
        distancia = CalculadorDistancias.calcular_distancia_entre(self.grafo, self.v1, self.v2)
        self.assertEqual(distancia, 4.0)
        
        # Distancia con camino indirecto
        distancia = CalculadorDistancias.calcular_distancia_entre(self.grafo, self.v1, self.v3)
        self.assertEqual(distancia, 4.0)  # v1 -> v4 -> v3
        
        # Distancia a sí mismo
        distancia = CalculadorDistancias.calcular_distancia_entre(self.grafo, self.v1, self.v1)
        self.assertEqual(distancia, 0.0)
    
    def test_calcular_distancia_inalcanzable(self):
        """Verifica el cálculo de distancia a vértice inalcanzable"""
        v_aislado = self.grafo.insert_vertex({'id': 5, 'nombre': 'E'})
        
        distancia = CalculadorDistancias.calcular_distancia_entre(self.grafo, self.v1, v_aislado)
        self.assertIsNone(distancia)
    
    def test_encontrar_camino_mas_corto_exitoso(self):
        """Verifica la búsqueda exitosa del camino más corto"""
        resultado = CalculadorDistancias.encontrar_camino_mas_corto(self.grafo, self.v1, self.v3)
        
        self.assertIsNotNone(resultado)
        camino, distancia = resultado
        
        self.assertEqual(camino, [self.v1, self.v4, self.v3])
        self.assertEqual(distancia, 4.0)
    
    def test_encontrar_camino_mas_corto_inalcanzable(self):
        """Verifica la búsqueda de camino a destino inalcanzable"""
        v_aislado = self.grafo.insert_vertex({'id': 5, 'nombre': 'E'})
        
        resultado = CalculadorDistancias.encontrar_camino_mas_corto(self.grafo, self.v1, v_aislado)
        self.assertIsNone(resultado)
    
    def test_dijkstra_sin_peso_en_aristas(self):
        """Verifica Dijkstra cuando las aristas no tienen peso explícito"""
        grafo_sin_peso = Graph(directed=False)
        
        va = grafo_sin_peso.insert_vertex({'id': 'A'})
        vb = grafo_sin_peso.insert_vertex({'id': 'B'})
        vc = grafo_sin_peso.insert_vertex({'id': 'C'})
        
        # Aristas sin peso explícito (debería usar peso por defecto 1.0)
        grafo_sin_peso.insert_edge(va, vb, {})
        grafo_sin_peso.insert_edge(vb, vc, {})
        
        distancias, _ = CalculadorDistancias.dijkstra(grafo_sin_peso, va)
        
        self.assertEqual(distancias[va], 0.0)
        self.assertEqual(distancias[vb], 1.0)
        self.assertEqual(distancias[vc], 2.0)


class TestBuscadorNodos(unittest.TestCase):
    """Pruebas para la clase BuscadorNodos"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear un grafo más realista usando el generador
        self.generador = GeneradorGrafoConectado(ConfiguracionRoles(0.2, 0.3, 0.5))
        self.generador.establecer_semilla(12345)  # Para resultados reproducibles
        
        self.grafo = self.generador.crear_grafo_conectado(10, 0.3)
        
        # Obtener vértices por roles para las pruebas
        self.vertices = list(self.grafo.vertices())
        self.vertices_almacenamiento = [
            v for v in self.vertices if v.element()['rol'] == RolNodo.ALMACENAMIENTO
        ]
        self.vertices_recarga = [
            v for v in self.vertices if v.element()['rol'] == RolNodo.RECARGA
        ]
        self.vertices_cliente = [
            v for v in self.vertices if v.element()['rol'] == RolNodo.CLIENTE
        ]
    
    def test_buscar_nodos_por_rol_almacenamiento(self):
        """Verifica la búsqueda de nodos por rol almacenamiento"""
        resultado = BuscadorNodos.buscar_nodos_por_rol(self.grafo, RolNodo.ALMACENAMIENTO)
        
        self.assertGreater(len(resultado), 0)
        for nodo in resultado:
            self.assertEqual(nodo.element()['rol'], RolNodo.ALMACENAMIENTO)
        
        # Verificar que coincide con nuestro cálculo manual
        self.assertEqual(set(resultado), set(self.vertices_almacenamiento))
    
    def test_buscar_nodos_por_rol_recarga(self):
        """Verifica la búsqueda de nodos por rol recarga"""
        resultado = BuscadorNodos.buscar_nodos_por_rol(self.grafo, RolNodo.RECARGA)
        
        self.assertGreater(len(resultado), 0)
        for nodo in resultado:
            self.assertEqual(nodo.element()['rol'], RolNodo.RECARGA)
        
        self.assertEqual(set(resultado), set(self.vertices_recarga))
    
    def test_buscar_nodos_por_rol_inexistente(self):
        """Verifica la búsqueda de nodos por rol inexistente"""
        resultado = BuscadorNodos.buscar_nodos_por_rol(self.grafo, 'rol_inexistente')
        self.assertEqual(len(resultado), 0)
    
    def test_buscar_nodo_mas_cercano_por_rol_exitoso(self):
        """Verifica la búsqueda exitosa del nodo más cercano por rol"""
        if self.vertices_cliente and self.vertices_almacenamiento:
            origen = self.vertices_cliente[0]
            
            resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                self.grafo, origen, RolNodo.ALMACENAMIENTO
            )
            
            self.assertIsNotNone(resultado)
            nodo_cercano, distancia = resultado
            
            # Verificar que el nodo encontrado tiene el rol correcto
            self.assertEqual(nodo_cercano.element()['rol'], RolNodo.ALMACENAMIENTO)
            
            # Verificar que la distancia sea no negativa
            self.assertGreaterEqual(distancia, 0.0)
            
            # Verificar que no hay un nodo más cercano
            for nodo_alm in self.vertices_almacenamiento:
                dist_verificacion = CalculadorDistancias.calcular_distancia_entre(
                    self.grafo, origen, nodo_alm
                )
                if dist_verificacion is not None:
                    self.assertGreaterEqual(dist_verificacion, distancia)
    
    def test_buscar_nodo_mas_cercano_mismo_rol(self):
        """Verifica la búsqueda cuando el origen ya tiene el rol buscado"""
        if self.vertices_almacenamiento:
            origen = self.vertices_almacenamiento[0]
            
            resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                self.grafo, origen, RolNodo.ALMACENAMIENTO
            )
            
            self.assertIsNotNone(resultado)
            nodo_cercano, distancia = resultado
            
            self.assertEqual(nodo_cercano, origen)
            self.assertEqual(distancia, 0.0)
    
    def test_buscar_nodo_mas_cercano_rol_inexistente(self):
        """Verifica la búsqueda de nodo más cercano para rol inexistente"""
        origen = self.vertices[0]
        
        resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
            self.grafo, origen, 'rol_inexistente'
        )
        
        self.assertIsNone(resultado)
    
    def test_buscar_k_nodos_mas_cercanos_por_rol(self):
        """Verifica la búsqueda de k nodos más cercanos por rol"""
        if self.vertices_cliente and len(self.vertices_recarga) >= 2:
            origen = self.vertices_cliente[0]
            k = min(3, len(self.vertices_recarga))
            
            resultado = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
                self.grafo, origen, RolNodo.RECARGA, k
            )
            
            self.assertLessEqual(len(resultado), k)
            self.assertGreater(len(resultado), 0)
            
            # Verificar que todos los nodos tienen el rol correcto
            for nodo, distancia in resultado:
                self.assertEqual(nodo.element()['rol'], RolNodo.RECARGA)
                self.assertGreaterEqual(distancia, 0.0)
            
            # Verificar que están ordenados por distancia
            distancias = [dist for _, dist in resultado]
            self.assertEqual(distancias, sorted(distancias))
    
    def test_buscar_k_nodos_mas_cercanos_k_mayor_que_disponibles(self):
        """Verifica k mayor que nodos disponibles"""
        if self.vertices_cliente and self.vertices_almacenamiento:
            origen = self.vertices_cliente[0]
            k = len(self.vertices_almacenamiento) + 5  # k mayor que disponibles
            
            resultado = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
                self.grafo, origen, RolNodo.ALMACENAMIENTO, k
            )
            
            # Debe devolver todos los nodos disponibles
            self.assertEqual(len(resultado), len(self.vertices_almacenamiento))
    
    def test_buscar_k_nodos_k_cero(self):
        """Verifica el comportamiento con k=0"""
        origen = self.vertices[0]
        
        resultado = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
            self.grafo, origen, RolNodo.CLIENTE, 0
        )
        
        self.assertEqual(len(resultado), 0)
    
    def test_obtener_estadisticas_roles(self):
        """Verifica la obtención de estadísticas por roles"""
        estadisticas = BuscadorNodos.obtener_estadisticas_roles(self.grafo)
        
        # Verificar estructura de estadísticas
        for rol in [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA, RolNodo.CLIENTE]:
            if rol in estadisticas:
                stats_rol = estadisticas[rol]
                
                # Verificar claves requeridas
                expected_keys = {'cantidad', 'porcentaje', 'grado_promedio', 
                               'grado_maximo', 'grado_minimo', 'nodos'}
                self.assertEqual(set(stats_rol.keys()), expected_keys)
                
                # Verificar tipos de datos
                self.assertIsInstance(stats_rol['cantidad'], int)
                self.assertIsInstance(stats_rol['porcentaje'], (int, float))
                self.assertIsInstance(stats_rol['grado_promedio'], (int, float))
                self.assertIsInstance(stats_rol['grado_maximo'], int)
                self.assertIsInstance(stats_rol['grado_minimo'], int)
                self.assertIsInstance(stats_rol['nodos'], list)
                
                # Verificar rangos válidos
                self.assertGreaterEqual(stats_rol['cantidad'], 0)
                self.assertGreaterEqual(stats_rol['porcentaje'], 0.0)
                self.assertLessEqual(stats_rol['porcentaje'], 100.0)
                self.assertGreaterEqual(stats_rol['grado_promedio'], 0.0)
                self.assertGreaterEqual(stats_rol['grado_maximo'], stats_rol['grado_minimo'])
    
    def test_estadisticas_roles_suma_porcentajes(self):
        """Verifica que los porcentajes sumen aproximadamente 100%"""
        estadisticas = BuscadorNodos.obtener_estadisticas_roles(self.grafo)
        
        suma_porcentajes = sum(stats['porcentaje'] for stats in estadisticas.values())
        
        # Permitir pequeñas diferencias por redondeo
        self.assertAlmostEqual(suma_porcentajes, 100.0, delta=0.1)
    
    def test_estadisticas_roles_cantidad_nodos(self):
        """Verifica que la cantidad de nodos coincida con el total"""
        estadisticas = BuscadorNodos.obtener_estadisticas_roles(self.grafo)
        
        suma_cantidades = sum(stats['cantidad'] for stats in estadisticas.values())
        total_vertices = len(list(self.grafo.vertices()))
        
        self.assertEqual(suma_cantidades, total_vertices)
    
    def test_estadisticas_roles_grafo_vacio(self):
        """Verifica estadísticas en grafo vacío"""
        grafo_vacio = Graph(directed=False)
        estadisticas = BuscadorNodos.obtener_estadisticas_roles(grafo_vacio)
        
        self.assertEqual(len(estadisticas), 0)


class TestIntegracionUtilidades(unittest.TestCase):
    """Pruebas de integración entre las diferentes clases de utilidades"""
    
    def setUp(self):
        """Configuración inicial para pruebas de integración"""
        self.generador = GeneradorGrafoConectado()
        self.generador.establecer_semilla(54321)
        self.grafo = self.generador.crear_grafo_conectado(15, 0.25)
    
    def test_flujo_completo_busqueda_y_navegacion(self):
        """Verifica un flujo completo de búsqueda y navegación"""
        # 1. Obtener estadísticas
        estadisticas = BuscadorNodos.obtener_estadisticas_roles(self.grafo)
        self.assertGreater(len(estadisticas), 0)
        
        # 2. Buscar un nodo específico por ID
        nodo_origen = ConsultorGrafo.buscar_vertice_por_id(self.grafo, 0)
        self.assertIsNotNone(nodo_origen)
        
        # 3. Encontrar el nodo más cercano de un rol específico
        resultado_busqueda = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
            self.grafo, nodo_origen, RolNodo.ALMACENAMIENTO
        )
        
        if resultado_busqueda:
            nodo_destino, _ = resultado_busqueda
            
            # 4. Calcular el camino más corto
            resultado_camino = CalculadorDistancias.encontrar_camino_mas_corto(
                self.grafo, nodo_origen, nodo_destino
            )
            
            self.assertIsNotNone(resultado_camino)
            camino, distancia = resultado_camino
            
            # 5. Verificar la consistencia del camino
            self.assertEqual(camino[0], nodo_origen)
            self.assertEqual(camino[-1], nodo_destino)
            self.assertGreater(len(camino), 0)
            self.assertGreaterEqual(distancia, 0.0)
    
    def test_verificacion_conectividad_y_componentes(self):
        """Verifica la consistencia entre métodos de conectividad"""
        # Verificar conectividad
        esta_conectado = ConsultorGrafo.validar_conectividad(self.grafo)
        
        # Obtener componentes conexas
        componentes = ConsultorGrafo.obtener_componentes_conexas(self.grafo)
        
        # Si está conectado, debe haber exactamente una componente
        if esta_conectado:
            self.assertEqual(len(componentes), 1)
            self.assertEqual(len(componentes[0]), len(list(self.grafo.vertices())))
        else:
            self.assertGreater(len(componentes), 1)


if __name__ == '__main__':
    # Configurar el runner de pruebas para obtener información detallada
    unittest.main(verbosity=2)

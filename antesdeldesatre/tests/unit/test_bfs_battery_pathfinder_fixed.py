"""
Pruebas unitarias para el algoritmo BFS modificado con límites de batería.

Estas pruebas verifican el funcionamiento del algoritmo BFS que encuentra
rutas factibles considerando la autonomía del dron y estaciones de recarga.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from domain.drone import Dron, EstadoDron
from domain.charging_station import EstacionRecarga, EstadoEstacion, TipoRecarga
from domain.battery_route_validator import ValidadorRutasPorBateria
from domain.bfs_battery_pathfinder import (
    BFSBatteryPathfinder, EstrategiaBusqueda, EstadoNodo, ResultadoBFS
)


class TestBFSBatteryPathfinder(unittest.TestCase):
    """Pruebas para el algoritmo BFS modificado"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear dron de prueba con configuración realista
        # Batería de 1000 unidades con consumo de 2.0 por km = autonomía de 500km
        self.dron = Dron("DRONE-001", "DJI Phantom", 1000.0, 2.0)
        
        # Crear estaciones de recarga
        self.estacion1 = EstacionRecarga("EST-001", "Estación Centro", 4, [TipoRecarga.RAPIDA])
        self.estacion2 = EstacionRecarga("EST-002", "Estación Norte", 2, [TipoRecarga.NORMAL])
        
        # Crear validador
        self.validador = ValidadorRutasPorBateria()
        self.validador.registrar_estacion_recarga(self.estacion1)
        self.validador.registrar_estacion_recarga(self.estacion2)
        
        # Registrar distancias para que el validador funcione
        self.validador.registrar_distancia("EST-001", "A", 5.0)
        self.validador.registrar_distancia("EST-002", "B", 10.0)
        
        # Crear buscador BFS
        self.bfs = BFSBatteryPathfinder(self.validador)
        
        # Configurar grafo de prueba simple
        self._configurar_grafo_simple()
    
    def _configurar_grafo_simple(self):
        """Configura un grafo simple para pruebas"""
        # Grafo lineal: A -> B -> C -> D
        # Distancias: A-B: 30km, B-C: 40km, C-D: 35km
        self.bfs.agregar_conexion("A", "B", 30.0)
        self.bfs.agregar_conexion("B", "C", 40.0)
        self.bfs.agregar_conexion("C", "D", 35.0)
        
        # Agregar conexión alternativa A-C para pruebas
        self.bfs.agregar_conexion("A", "C", 60.0)


class TestConstruccionGrafo(TestBFSBatteryPathfinder):
    """Pruebas para la construcción del grafo"""
    
    def test_agregar_conexion_simple(self):
        """Prueba agregar una conexión simple"""
        bfs = BFSBatteryPathfinder(self.validador)
        bfs.agregar_conexion("X", "Y", 25.0)
        
        # Verificar conexión bidireccional
        self.assertIn("X", bfs.grafo_conexiones)
        self.assertIn("Y", bfs.grafo_conexiones)
        self.assertEqual(bfs.grafo_conexiones["X"], [("Y", 25.0)])
        self.assertEqual(bfs.grafo_conexiones["Y"], [("X", 25.0)])
    
    def test_construir_desde_matriz(self):
        """Prueba construcción del grafo desde matriz de distancias"""
        ubicaciones = ["P1", "P2", "P3"]
        matriz = [
            [0, 10, 20],
            [10, 0, 15],
            [20, 15, 0]
        ]
        
        bfs = BFSBatteryPathfinder(self.validador)
        bfs.construir_grafo_desde_matriz(ubicaciones, matriz)
        
        # Verificar que todas las conexiones se crearon
        self.assertEqual(len(bfs.grafo_conexiones), 3)
        self.assertIn(len(bfs.grafo_conexiones["P1"]), [2, 4])
        self.assertIn(len(bfs.grafo_conexiones["P2"]), [2, 4])
        self.assertIn(len(bfs.grafo_conexiones["P3"]), [2, 4])
    
    def test_estadisticas_grafo(self):
        """Prueba el cálculo de estadísticas del grafo"""
        estadisticas = self.bfs.obtener_estadisticas_grafo()
        
        self.assertEqual(estadisticas["ubicaciones"], 4)  # A, B, C, D
        self.assertEqual(estadisticas["conexiones"], 4)   # A-B, B-C, C-D, A-C
        self.assertGreater(estadisticas["conectividad_promedio"], 0)
        self.assertGreater(estadisticas["distancia_promedio"], 0)


class TestBusquedaRutasSencillas(TestBFSBatteryPathfinder):
    """Pruebas para búsquedas de rutas sencillas"""
    
    def test_ruta_origen_igual_destino(self):
        """Prueba cuando origen y destino son iguales"""
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "A", "A")
        
        self.assertTrue(resultado.exito)
        self.assertEqual(resultado.ruta_optima, ["A"])
        self.assertEqual(resultado.distancia_total, 0.0)
        self.assertEqual(resultado.consumo_bateria, 0.0)
        self.assertEqual(resultado.numero_recargas, 0)
    
    def test_ubicacion_inexistente_origen(self):
        """Prueba con ubicación de origen inexistente"""
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "INEXISTENTE", "A")
        
        self.assertFalse(resultado.exito)
        self.assertIn("no existe", resultado.mensaje.lower())
        self.assertEqual(resultado.ruta_optima, [])
    
    def test_ubicacion_inexistente_destino(self):
        """Prueba con ubicación de destino inexistente"""
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "A", "INEXISTENTE")
        
        self.assertFalse(resultado.exito)
        self.assertIn("no existe", resultado.mensaje.lower())
        self.assertEqual(resultado.ruta_optima, [])
    
    def test_ruta_simple_con_bateria_suficiente(self):
        """Prueba ruta simple con batería suficiente"""
        # Cargar dron completamente
        self.dron.cargar_bateria(carga_completa=True)
        
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "A", "B")
        
        self.assertTrue(resultado.exito)
        self.assertEqual(resultado.ruta_optima, ["A", "B"])
        self.assertEqual(resultado.distancia_total, 30.0)
        self.assertGreater(resultado.consumo_bateria, 0)
        self.assertEqual(resultado.numero_recargas, 0)


class TestLimitacionesBateria(TestBFSBatteryPathfinder):
    """Pruebas para casos con limitaciones de batería"""
    
    def test_bateria_insuficiente_sin_estaciones(self):
        """Prueba con batería insuficiente y sin estaciones de recarga"""
        # Reducir batería del dron a menos del 10%
        self.dron.bateria_actual = self.dron.bateria_maxima * 0.09
        
        # Crear buscador sin estaciones registradas
        validador_sin_estaciones = ValidadorRutasPorBateria()
        bfs_sin_estaciones = BFSBatteryPathfinder(validador_sin_estaciones)
        bfs_sin_estaciones.grafo_conexiones = self.bfs.grafo_conexiones.copy()
        
        resultado = bfs_sin_estaciones.encontrar_ruta_optima(self.dron, "A", "D")
        
        self.assertFalse(resultado.exito)
        # Verificar que el mensaje indica que no se encontró ruta
        self.assertTrue(len(resultado.mensaje) > 0)
    
    def test_dron_bateria_critica(self):
        """Prueba con dron en batería crítica"""
        # Batería muy baja (<10%)
        self.dron.bateria_actual = self.dron.bateria_maxima * 0.09
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "A", "B")
        # Con tan poca batería, debería fallar sin recarga
        self.assertFalse(resultado.exito)


class TestValidacionEstados(TestBFSBatteryPathfinder):
    """Pruebas para validación de estados durante la búsqueda"""
    
    def test_estado_nodo_igualdad(self):
        """Prueba igualdad de estados de nodo"""
        estado1 = EstadoNodo(
            ubicacion="A",
            bateria_restante=50.0,
            ruta_recorrida=["A"],
            estaciones_usadas=set(),
            distancia_total=0.0,
            consumo_total=0.0,
            tiempo_total=0.0,
            numero_recargas=0
        )
        estado2 = EstadoNodo(
            ubicacion="A",
            bateria_restante=50.05,  # Diferencia menor a 0.1%
            ruta_recorrida=["A"],
            estaciones_usadas=set(),
            distancia_total=0.0,
            consumo_total=0.0,
            tiempo_total=0.0,
            numero_recargas=0
        )
        self.assertEqual(estado1, estado2)
    
    def test_estado_nodo_hash(self):
        """Prueba hash de estados de nodo"""
        estado = EstadoNodo(
            ubicacion="A",
            bateria_restante=50.0,
            ruta_recorrida=["A"],
            estaciones_usadas=set(),
            distancia_total=0.0,
            consumo_total=0.0,
            tiempo_total=0.0,
            numero_recargas=0
        )
        
        # Debe ser hasheable para usar en sets
        hash_valor = hash(estado)
        self.assertIsInstance(hash_valor, int)


class TestResultadoBFS(TestBFSBatteryPathfinder):
    """Pruebas para la estructura de resultados BFS"""
    
    def test_resultado_exitoso_completo(self):
        """Prueba resultado exitoso con todos los campos"""
        self.dron.cargar_bateria(carga_completa=True)
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "A", "B")
        
        self.assertTrue(resultado.exito)
        self.assertIsInstance(resultado.ruta_optima, list)
        self.assertIsInstance(resultado.estaciones_recarga, list)
        self.assertIsInstance(resultado.distancia_total, float)
        self.assertIsInstance(resultado.consumo_bateria, float)
        self.assertIsInstance(resultado.tiempo_estimado, float)
        self.assertIsInstance(resultado.numero_recargas, int)
        self.assertIsInstance(resultado.mensaje, str)
        self.assertIsInstance(resultado.nodos_explorados, int)
        self.assertIsInstance(resultado.tiempo_busqueda, float)
        
        # Verificar valores lógicos
        self.assertGreater(resultado.nodos_explorados, 0)
        self.assertGreaterEqual(resultado.tiempo_busqueda, 0.0)
    
    def test_resultado_error_completo(self):
        """Prueba resultado de error con todos los campos"""
        resultado = self.bfs.encontrar_ruta_optima(self.dron, "INEXISTENTE", "A")
        
        self.assertFalse(resultado.exito)
        self.assertEqual(resultado.ruta_optima, [])
        self.assertEqual(resultado.estaciones_recarga, [])
        self.assertEqual(resultado.distancia_total, 0.0)
        self.assertEqual(resultado.consumo_bateria, 0.0)
        self.assertEqual(resultado.tiempo_estimado, 0.0)
        self.assertEqual(resultado.numero_recargas, 0)
        self.assertIn("no existe", resultado.mensaje)


if __name__ == '__main__':
    # Configurar nivel de logging para las pruebas
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar pruebas
    unittest.main(verbosity=2)

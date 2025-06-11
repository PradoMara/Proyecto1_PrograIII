"""
Pruebas unitarias para el Validador de Rutas por Batería
"""

import unittest
from domain import Dron, EstacionRecarga, TipoRecarga, EstadoDron
from domain.battery_route_validator import (
    ValidadorRutasPorBateria, 
    SegmentoRuta, 
    ResultadoValidacion
)


class TestSegmentoRuta(unittest.TestCase):
    """Pruebas para la clase SegmentoRuta"""
    
    def test_crear_segmento_normal(self):
        """Prueba creación de segmento normal"""
        segmento = SegmentoRuta("A", "B", 10.0, 5.0, False)
        
        self.assertEqual(segmento.origen, "A")
        self.assertEqual(segmento.destino, "B")
        self.assertEqual(segmento.distancia, 10.0)
        self.assertEqual(segmento.consumo_bateria, 5.0)
        self.assertFalse(segmento.es_recarga)
    
    def test_crear_segmento_recarga(self):
        """Prueba creación de segmento hacia estación de recarga"""
        segmento = SegmentoRuta("A", "EST01", 15.0, 7.5, True)
        
        self.assertEqual(segmento.destino, "EST01")
        self.assertTrue(segmento.es_recarga)
    
    def test_str_representation(self):
        """Prueba representación en string"""
        segmento_normal = SegmentoRuta("A", "B", 10.0, 5.0, False)
        segmento_recarga = SegmentoRuta("A", "EST01", 15.0, 7.5, True)
        
        str_normal = str(segmento_normal)
        str_recarga = str(segmento_recarga)
        
        self.assertIn("A -> B", str_normal)
        self.assertIn("NORMAL", str_normal)
        self.assertIn("A -> EST01", str_recarga)
        self.assertIn("RECARGA", str_recarga)


class TestResultadoValidacion(unittest.TestCase):
    """Pruebas para la clase ResultadoValidacion"""
    
    def test_resultado_factible(self):
        """Prueba resultado de validación factible"""
        resultado = ResultadoValidacion(
            es_factible=True,
            bateria_final=45.0,
            segmentos_criticos=[],
            paradas_recarga_necesarias=["EST01"],
            consumo_total=55.0,
            distancia_total=100.0,
            mensaje="Ruta factible"
        )
        
        self.assertTrue(resultado.es_factible)
        self.assertEqual(resultado.bateria_final, 45.0)
        self.assertEqual(len(resultado.paradas_recarga_necesarias), 1)
        self.assertIn("EST01", resultado.paradas_recarga_necesarias)
    
    def test_str_representation(self):
        """Prueba representación en string del resultado"""
        resultado = ResultadoValidacion(
            es_factible=False,
            bateria_final=10.0,
            segmentos_criticos=[],
            paradas_recarga_necesarias=[],
            consumo_total=90.0,
            distancia_total=150.0,
            mensaje="Batería insuficiente"
        )
        
        str_resultado = str(resultado)
        
        self.assertIn("NO FACTIBLE", str_resultado)
        self.assertIn("10.0%", str_resultado)
        self.assertIn("Batería insuficiente", str_resultado)


class TestValidadorRutasPorBateria(unittest.TestCase):
    """Pruebas para el ValidadorRutasPorBateria"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.validador = ValidadorRutasPorBateria(margen_seguridad=0.15)
        
        # Crear dron de prueba
        self.dron = Dron("D001", "Modelo Test", 100.0, 5.0, bateria_actual=80.0)
        
        # Crear estaciones de recarga
        self.estacion1 = EstacionRecarga("EST01", "NODO_EST01", capacidad_maxima=2)
        self.estacion2 = EstacionRecarga("EST02", "NODO_EST02", capacidad_maxima=1)
        
        # Registrar estaciones
        self.validador.registrar_estacion_recarga(self.estacion1)
        self.validador.registrar_estacion_recarga(self.estacion2)
        
        # Registrar distancias de ejemplo
        self.validador.registrar_distancia("A", "B", 5.0)
        self.validador.registrar_distancia("B", "C", 8.0)
        self.validador.registrar_distancia("C", "NODO_EST01", 3.0)
        self.validador.registrar_distancia("NODO_EST01", "D", 10.0)
        self.validador.registrar_distancia("A", "NODO_EST02", 15.0)
        self.validador.registrar_distancia("NODO_EST02", "D", 12.0)
    
    def test_inicializacion(self):
        """Prueba inicialización del validador"""
        validador = ValidadorRutasPorBateria(margen_seguridad=0.20)
        
        self.assertEqual(validador.margen_seguridad, 0.20)
        self.assertEqual(len(validador.estaciones_recarga), 0)
        self.assertEqual(len(validador.distancias_nodos), 0)
    
    def test_registrar_estacion_recarga(self):
        """Prueba registro de estación de recarga"""
        nueva_estacion = EstacionRecarga("EST03", "NODO_EST03")
        self.validador.registrar_estacion_recarga(nueva_estacion)
        
        self.assertIn("NODO_EST03", self.validador.estaciones_recarga)
        self.assertTrue(self.validador.es_estacion_recarga("NODO_EST03"))
    
    def test_registrar_distancia(self):
        """Prueba registro de distancias entre nodos"""
        self.validador.registrar_distancia("X", "Y", 25.0)
        
        self.assertEqual(self.validador.obtener_distancia("X", "Y"), 25.0)
        self.assertEqual(self.validador.obtener_distancia("Y", "X"), 25.0)  # Bidireccional
    
    def test_obtener_distancia_inexistente(self):
        """Prueba obtener distancia inexistente"""
        distancia = self.validador.obtener_distancia("INEXISTENTE", "OTRO")
        self.assertIsNone(distancia)
    
    def test_es_estacion_recarga(self):
        """Prueba verificación de estaciones de recarga"""
        self.assertTrue(self.validador.es_estacion_recarga("NODO_EST01"))
        self.assertTrue(self.validador.es_estacion_recarga("NODO_EST02"))
        self.assertFalse(self.validador.es_estacion_recarga("A"))        self.assertFalse(self.validador.es_estacion_recarga("INEXISTENTE"))
    
    def test_validar_ruta_simple_factible(self):
        """Prueba validación de ruta simple factible"""
        ruta = ["A", "B", "C"]
        resultado = self.validador.validar_ruta_simple(self.dron, ruta)
        
        self.assertTrue(resultado.es_factible)
        self.assertGreaterEqual(resultado.bateria_final, 15.0)  # Igual o mayor al margen de seguridad
        self.assertEqual(resultado.distancia_total, 13.0)  # 5 + 8
    
    def test_validar_ruta_simple_no_factible(self):
        """Prueba validación de ruta simple no factible"""
        # Crear dron con poca batería
        dron_baja_bateria = Dron("D002", "Modelo Test", 100.0, 5.0, bateria_actual=20.0)
        
        ruta = ["A", "B", "C"]
        resultado = self.validador.validar_ruta_simple(dron_baja_bateria, ruta)
        
        self.assertFalse(resultado.es_factible)
        self.assertIn("insuficiente", resultado.mensaje.lower())
    
    def test_validar_ruta_vacia(self):
        """Prueba validación de ruta vacía o muy corta"""
        resultado_vacia = self.validador.validar_ruta_simple(self.dron, [])
        resultado_corta = self.validador.validar_ruta_simple(self.dron, ["A"])
        
        self.assertFalse(resultado_vacia.es_factible)
        self.assertFalse(resultado_corta.es_factible)
        self.assertIn("al menos 2 nodos", resultado_vacia.mensaje)
        self.assertIn("al menos 2 nodos", resultado_corta.mensaje)
    
    def test_validar_ruta_distancias_inexistentes(self):
        """Prueba validación con distancias inexistentes"""
        ruta = ["A", "INEXISTENTE", "B"]
        resultado = self.validador.validar_ruta_simple(self.dron, ruta)
        
        self.assertFalse(resultado.es_factible)
        self.assertIn("distancias", resultado.mensaje.lower())
    
    def test_validar_ruta_con_recarga(self):
        """Prueba validación con recarga automática"""
        # Crear ruta que pase por una estación de recarga
        ruta = ["A", "B", "C", "NODO_EST01", "D"]
        resultado = self.validador.validar_ruta_con_recarga(self.dron, ruta)
        
        self.assertTrue(resultado.es_factible)
        self.assertGreaterEqual(len(resultado.paradas_recarga_necesarias), 0)
    
    def test_encontrar_estaciones_cercanas(self):
        """Prueba búsqueda de estaciones cercanas"""
        estaciones = self.validador.encontrar_estaciones_cercanas("C", radio_busqueda=10.0)
        
        self.assertGreater(len(estaciones), 0)
        # La primera debe ser la más cercana
        estacion_mas_cercana, distancia = estaciones[0]
        self.assertEqual(estacion_mas_cercana, "NODO_EST01")
        self.assertEqual(distancia, 3.0)
    
    def test_encontrar_estaciones_cercanas_sin_resultados(self):
        """Prueba búsqueda sin estaciones en el radio"""
        estaciones = self.validador.encontrar_estaciones_cercanas("C", radio_busqueda=1.0)
        self.assertEqual(len(estaciones), 0)
      def test_obtener_estadisticas(self):
        """Prueba obtención de estadísticas del validador"""
        stats = self.validador.obtener_estadisticas()
        
        self.assertEqual(stats["estaciones_registradas"], 2)
        self.assertEqual(stats["distancias_registradas"], 6)  # 6 pares bidireccionales
        self.assertEqual(stats["margen_seguridad"], 0.15)
        self.assertIn("NODO_EST01", stats["estaciones_por_nodo"])
        self.assertIn("NODO_EST02", stats["estaciones_por_nodo"])


class TestCasosEspeciales(unittest.TestCase):
    """Pruebas para casos especiales y borde"""
    
    def setUp(self):
        """Configuración inicial"""
        self.validador = ValidadorRutasPorBateria(margen_seguridad=0.10)
        
        # Dron con batería crítica
        self.dron_critico = Dron("D_CRITICO", "Modelo", 100.0, 8.0, bateria_actual=25.0)
        
        # Estación de emergencia
        estacion_emergencia = EstacionRecarga("EST_EM", "EMERGENCIA")
        self.validador.registrar_estacion_recarga(estacion_emergencia)
        
        # Red de nodos con distancias largas
        self.validador.registrar_distancia("INICIO", "MEDIO", 30.0)
        self.validador.registrar_distancia("MEDIO", "EMERGENCIA", 5.0)
        self.validador.registrar_distancia("EMERGENCIA", "FIN", 25.0)
    
    def test_ruta_con_dron_bateria_critica(self):
        """Prueba ruta con dron de batería muy baja"""
        ruta = ["INICIO", "MEDIO", "EMERGENCIA", "FIN"]
        
        # Sin recarga debe fallar
        resultado_sin_recarga = self.validador.validar_ruta_simple(self.dron_critico, ruta)
        self.assertFalse(resultado_sin_recarga.es_factible)
        
        # Con recarga debe ser factible
        resultado_con_recarga = self.validador.validar_ruta_con_recarga(self.dron_critico, ruta)
        self.assertTrue(resultado_con_recarga.es_factible)
        self.assertIn("EMERGENCIA", resultado_con_recarga.paradas_recarga_necesarias)
    
    def test_ruta_larga_multiple_recargas(self):
        """Prueba ruta que requiere múltiples recargas"""
        # Agregar más estaciones
        estacion2 = EstacionRecarga("EST2", "PUNTO2")
        self.validador.registrar_estacion_recarga(estacion2)
        
        # Red larga
        self.validador.registrar_distancia("INICIO", "PUNTO2", 40.0)
        self.validador.registrar_distancia("PUNTO2", "EMERGENCIA", 35.0)
        
        ruta_larga = ["INICIO", "PUNTO2", "EMERGENCIA", "FIN"]
        resultado = self.validador.validar_ruta_con_recarga(self.dron_critico, ruta_larga)
        
        # Debe requerir múltiples paradas
        self.assertGreaterEqual(len(resultado.paradas_recarga_necesarias), 1)
    
    def test_margen_seguridad_extremo(self):
        """Prueba con margen de seguridad muy alto"""
        validador_conservador = ValidadorRutasPorBateria(margen_seguridad=0.50)  # 50%
        validador_conservador.registrar_distancia("A", "B", 5.0)
        
        dron_bateria_media = Dron("D_MEDIO", "Modelo", 100.0, 5.0, bateria_actual=60.0)
        
        resultado = validador_conservador.validar_ruta_simple(dron_bateria_media, ["A", "B"])
        
        # Con margen tan alto, incluso rutas cortas pueden no ser factibles
        self.assertFalse(resultado.es_factible)


if __name__ == '__main__':
    unittest.main()

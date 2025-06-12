import unittest
import sys
import os
from datetime import datetime, timedelta

# Agregar el path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.drone import Dron, EstadoDron


class TestEstadoDron(unittest.TestCase):
    """Pruebas para el enum EstadoDron"""
    
    def test_estados_disponibles(self):
        """Prueba que todos los estados estén definidos correctamente"""
        estados_esperados = ['disponible', 'en_vuelo', 'cargando', 'mantenimiento', 'fuera_de_servicio']
        estados_reales = [estado.value for estado in EstadoDron]
        
        for estado in estados_esperados:
            self.assertIn(estado, estados_reales)


class TestDron(unittest.TestCase):
    """Pruebas principales para la clase Dron"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.dron_prueba = Dron(
            dron_id="D001",
            modelo="DJI Mavic Pro",
            bateria_maxima=100.0,
            consumo_por_km=5.0,
            velocidad_promedio=25.0,
            posicion_actual="BASE",
            carga_maxima=2.5,
            tiempo_carga_completa=45.0
        )
    
    def test_inicializacion_dron(self):
        """Prueba la inicialización correcta del dron"""
        self.assertEqual(self.dron_prueba.dron_id, "D001")
        self.assertEqual(self.dron_prueba.modelo, "DJI Mavic Pro")
        self.assertEqual(self.dron_prueba.bateria_maxima, 100.0)
        self.assertEqual(self.dron_prueba.bateria_actual, 100.0)  # Debe iniciar al 100%
        self.assertEqual(self.dron_prueba.consumo_por_km, 5.0)
        self.assertEqual(self.dron_prueba.velocidad_promedio, 25.0)
        self.assertEqual(self.dron_prueba.posicion_actual, "BASE")
        self.assertEqual(self.dron_prueba.estado, EstadoDron.DISPONIBLE)
        self.assertEqual(self.dron_prueba.kilometros_volados, 0.0)
        self.assertEqual(self.dron_prueba.entregas_realizadas, 0)
    
    def test_inicializacion_bateria_personalizada(self):
        """Prueba inicialización con batería específica"""
        dron = Dron("D002", "Test Model", 100.0, 5.0, bateria_actual=75.0)
        self.assertEqual(dron.bateria_actual, 75.0)
    
    def test_inicializacion_bateria_invalida(self):
        """Prueba validación de batería inicial"""
        # Batería mayor al máximo
        dron1 = Dron("D003", "Test Model", 100.0, 5.0, bateria_actual=150.0)
        self.assertEqual(dron1.bateria_actual, 100.0)
        
        # Batería negativa
        dron2 = Dron("D004", "Test Model", 100.0, 5.0, bateria_actual=-10.0)
        self.assertEqual(dron2.bateria_actual, 0.0)
    
    def test_autonomia_actual(self):
        """Prueba cálculo de autonomía actual"""
        autonomia = self.dron_prueba.obtener_autonomia_actual()
        # 100 batería / 5 consumo por km = 20 km
        self.assertEqual(autonomia, 20.0)
        
        # Cambiar batería y verificar
        self.dron_prueba.bateria_actual = 50.0
        autonomia = self.dron_prueba.obtener_autonomia_actual()
        self.assertEqual(autonomia, 10.0)
    
    def test_autonomia_maxima(self):
        """Prueba cálculo de autonomía máxima"""
        autonomia_max = self.dron_prueba.obtener_autonomia_maxima()
        self.assertEqual(autonomia_max, 20.0)
    
    def test_autonomia_consumo_cero(self):
        """Prueba autonomía con consumo cero o negativo"""
        dron = Dron("D005", "Test Model", 100.0, 0.0)
        self.assertEqual(dron.obtener_autonomia_actual(), float('inf'))
        self.assertEqual(dron.obtener_autonomia_maxima(), float('inf'))
    
    def test_puede_volar_distancia(self):
        """Prueba verificación de capacidad de vuelo"""
        # Distancia factible
        self.assertTrue(self.dron_prueba.puede_volar_distancia(15.0))
        
        # Distancia muy larga
        self.assertFalse(self.dron_prueba.puede_volar_distancia(25.0))
        
        # Con margen de seguridad personalizado
        self.assertTrue(self.dron_prueba.puede_volar_distancia(18.0, margen_seguridad=0.0))
        self.assertFalse(self.dron_prueba.puede_volar_distancia(18.0, margen_seguridad=0.2))
    
    def test_puede_volar_estado_no_disponible(self):
        """Prueba que no puede volar si no está disponible"""
        self.dron_prueba.estado = EstadoDron.MANTENIMIENTO
        self.assertFalse(self.dron_prueba.puede_volar_distancia(5.0))
    
    def test_calcular_consumo_vuelo(self):
        """Prueba cálculo de consumo de batería"""
        consumo = self.dron_prueba.calcular_consumo_vuelo(10.0)
        # 10 km * 5 consumo por km = 50 batería
        self.assertEqual(consumo, 50.0)
    
    def test_volar_exitoso(self):
        """Prueba vuelo exitoso"""
        bateria_inicial = self.dron_prueba.bateria_actual
        kilometros_iniciales = self.dron_prueba.kilometros_volados
        
        resultado = self.dron_prueba.volar(10.0, "DESTINO1")
        
        self.assertTrue(resultado)
        self.assertEqual(self.dron_prueba.bateria_actual, bateria_inicial - 50.0)  # 10km * 5 consumo
        self.assertEqual(self.dron_prueba.kilometros_volados, kilometros_iniciales + 10.0)
        self.assertEqual(self.dron_prueba.posicion_actual, "DESTINO1")
        self.assertEqual(self.dron_prueba.estado, EstadoDron.DISPONIBLE)
        self.assertGreater(self.dron_prueba.tiempo_vuelo_total, 0)
    
    def test_volar_sin_bateria_suficiente(self):
        """Prueba vuelo sin batería suficiente"""
        self.dron_prueba.bateria_actual = 10.0
        bateria_inicial = self.dron_prueba.bateria_actual
        
        resultado = self.dron_prueba.volar(15.0)  # Necesita 75 de batería
        
        self.assertFalse(resultado)
        self.assertEqual(self.dron_prueba.bateria_actual, bateria_inicial)  # No debe cambiar
    
    def test_porcentaje_bateria(self):
        """Prueba cálculo de porcentaje de batería"""
        self.assertEqual(self.dron_prueba.obtener_porcentaje_bateria(), 100.0)
        
        self.dron_prueba.bateria_actual = 50.0
        self.assertEqual(self.dron_prueba.obtener_porcentaje_bateria(), 50.0)
        
        self.dron_prueba.bateria_actual = 0.0
        self.assertEqual(self.dron_prueba.obtener_porcentaje_bateria(), 0.0)
    
    def test_necesita_recarga(self):
        """Prueba detección de necesidad de recarga"""
        # Batería alta
        self.assertFalse(self.dron_prueba.necesita_recarga())
        
        # Batería baja
        self.dron_prueba.bateria_actual = 15.0
        self.assertTrue(self.dron_prueba.necesita_recarga())
        
        # Umbral personalizado
        self.dron_prueba.bateria_actual = 35.0
        self.assertFalse(self.dron_prueba.necesita_recarga(30.0))
        self.assertTrue(self.dron_prueba.necesita_recarga(40.0))
    
    def test_cargar_bateria_completa(self):
        """Prueba carga completa de batería"""
        self.dron_prueba.bateria_actual = 30.0
        ciclos_iniciales = self.dron_prueba.ciclos_carga
        
        cantidad_cargada = self.dron_prueba.cargar_bateria()
        
        self.assertEqual(self.dron_prueba.bateria_actual, 100.0)
        self.assertEqual(cantidad_cargada, 70.0)
        self.assertEqual(self.dron_prueba.ciclos_carga, ciclos_iniciales + 1)
    
    def test_cargar_bateria_cantidad_especifica(self):
        """Prueba carga de cantidad específica"""
        self.dron_prueba.bateria_actual = 40.0
        
        cantidad_cargada = self.dron_prueba.cargar_bateria(cantidad=30.0, carga_completa=False)
        
        self.assertEqual(self.dron_prueba.bateria_actual, 70.0)
        self.assertEqual(cantidad_cargada, 30.0)
    
    def test_cargar_bateria_exceso(self):
        """Prueba carga que excede la capacidad máxima"""
        self.dron_prueba.bateria_actual = 90.0
        
        cantidad_cargada = self.dron_prueba.cargar_bateria(cantidad=50.0, carga_completa=False)
        
        self.assertEqual(self.dron_prueba.bateria_actual, 100.0)
        self.assertEqual(cantidad_cargada, 10.0)
    
    def test_calcular_tiempo_carga_necesario(self):
        """Prueba cálculo de tiempo de carga necesario"""
        self.dron_prueba.bateria_actual = 25.0  # 25%
        
        # Carga completa (100%)
        tiempo_completo = self.dron_prueba.calcular_tiempo_carga_necesario(100.0)
        esperado = (75.0 / 100.0) * 45.0  # 75% de 45 minutos
        self.assertEqual(tiempo_completo, esperado)
        
        # Carga parcial (50%)
        tiempo_parcial = self.dron_prueba.calcular_tiempo_carga_necesario(50.0)
        esperado_parcial = (25.0 / 100.0) * 45.0  # 25% de 45 minutos
        self.assertEqual(tiempo_parcial, esperado_parcial)
        
        # Ya tiene suficiente batería
        tiempo_cero = self.dron_prueba.calcular_tiempo_carga_necesario(20.0)
        self.assertEqual(tiempo_cero, 0.0)
    
    def test_cambiar_estado_valido(self):
        """Prueba cambios de estado válidos"""
        # Disponible -> En vuelo
        self.assertTrue(self.dron_prueba.cambiar_estado(EstadoDron.EN_VUELO))
        self.assertEqual(self.dron_prueba.estado, EstadoDron.EN_VUELO)
        
        # En vuelo -> Disponible
        self.assertTrue(self.dron_prueba.cambiar_estado(EstadoDron.DISPONIBLE))
        self.assertEqual(self.dron_prueba.estado, EstadoDron.DISPONIBLE)
        
        # Disponible -> Cargando
        self.assertTrue(self.dron_prueba.cambiar_estado(EstadoDron.CARGANDO))
        self.assertEqual(self.dron_prueba.estado, EstadoDron.CARGANDO)
    
    def test_cambiar_estado_invalido(self):
        """Prueba cambios de estado inválidos"""
        # Disponible -> Fuera de servicio (no permitido directamente)
        resultado = self.dron_prueba.cambiar_estado(EstadoDron.FUERA_DE_SERVICIO)
        self.assertFalse(resultado)
        self.assertEqual(self.dron_prueba.estado, EstadoDron.DISPONIBLE)
        
        # Cargando -> En vuelo (no permitido)
        self.dron_prueba.estado = EstadoDron.CARGANDO
        resultado = self.dron_prueba.cambiar_estado(EstadoDron.EN_VUELO)
        self.assertFalse(resultado)
        self.assertEqual(self.dron_prueba.estado, EstadoDron.CARGANDO)
    
    def test_registrar_entrega(self):
        """Prueba registro de entregas"""
        entregas_iniciales = self.dron_prueba.entregas_realizadas
        
        self.dron_prueba.registrar_entrega()
        
        self.assertEqual(self.dron_prueba.entregas_realizadas, entregas_iniciales + 1)
    
    def test_obtener_metricas(self):
        """Prueba obtención de métricas completas"""
        metricas = self.dron_prueba.obtener_metricas()
        
        campos_esperados = [
            'dron_id', 'modelo', 'estado', 'bateria_actual', 'bateria_maxima',
            'porcentaje_bateria', 'autonomia_actual_km', 'autonomia_maxima_km',
            'posicion_actual', 'kilometros_volados', 'entregas_realizadas',
            'tiempo_vuelo_total_min', 'ciclos_carga', 'consumo_por_km',
            'velocidad_promedio', 'carga_maxima', 'ultima_actualizacion'
        ]
        
        for campo in campos_esperados:
            self.assertIn(campo, metricas)
        
        self.assertEqual(metricas['dron_id'], "D001")
        self.assertEqual(metricas['modelo'], "DJI Mavic Pro")
        self.assertEqual(metricas['estado'], "disponible")
    
    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        dict_dron = self.dron_prueba.to_dict()
        
        self.assertIsInstance(dict_dron, dict)
        self.assertEqual(dict_dron['dron_id'], "D001")
        self.assertEqual(dict_dron['bateria_maxima'], 100.0)
    
    def test_from_dict(self):
        """Prueba creación desde diccionario"""
        # Volar para cambiar algunas métricas
        self.dron_prueba.volar(5.0, "DESTINO_TEST")
        self.dron_prueba.registrar_entrega()
        
        dict_original = self.dron_prueba.to_dict()
        dron_restaurado = Dron.from_dict(dict_original)
        
        self.assertEqual(dron_restaurado.dron_id, self.dron_prueba.dron_id)
        self.assertEqual(dron_restaurado.modelo, self.dron_prueba.modelo)
        self.assertEqual(dron_restaurado.bateria_actual, self.dron_prueba.bateria_actual)
        self.assertEqual(dron_restaurado.kilometros_volados, self.dron_prueba.kilometros_volados)
        self.assertEqual(dron_restaurado.entregas_realizadas, self.dron_prueba.entregas_realizadas)
        self.assertEqual(dron_restaurado.estado, self.dron_prueba.estado)
    
    def test_str_representation(self):
        """Prueba representación en string"""
        str_dron = str(self.dron_prueba)
        
        self.assertIn("D001", str_dron)
        self.assertIn("DJI Mavic Pro", str_dron)
        self.assertIn("100.0%", str_dron)
        self.assertIn("disponible", str_dron)
        self.assertIn("20.0km", str_dron)


class TestCasosEspecialesDron(unittest.TestCase):
    """Pruebas para casos especiales y límite"""
    
    def test_dron_sin_posicion_inicial(self):
        """Prueba dron sin posición inicial"""
        dron = Dron("D010", "Test Model", 100.0, 5.0)
        self.assertIsNone(dron.posicion_actual)
        
        # Debe poder volar sin posición inicial
        resultado = dron.volar(5.0, "DESTINO")
        self.assertTrue(resultado)
        self.assertEqual(dron.posicion_actual, "DESTINO")
    
    def test_multiples_vuelos_consecutivos(self):
        """Prueba múltiples vuelos hasta agotar batería"""
        dron = Dron("D011", "Test Model", 100.0, 10.0)  # Autonomía de 10km
        
        # Primer vuelo (5km)
        self.assertTrue(dron.volar(5.0))
        self.assertEqual(dron.bateria_actual, 50.0)
        
        # Segundo vuelo (4km)
        self.assertTrue(dron.volar(4.0))
        self.assertEqual(dron.bateria_actual, 10.0)
        
        # Tercer vuelo (2km) - debe fallar por margen de seguridad
        self.assertFalse(dron.volar(2.0))
        self.assertEqual(dron.bateria_actual, 10.0)  # No debe cambiar
    
    def test_ciclo_carga_y_descarga(self):
        """Prueba ciclo completo de carga y descarga"""
        dron = Dron("D012", "Test Model", 100.0, 20.0)  # Autonomía de 5km
        
        # Descargar batería volando
        dron.volar(4.0)  # Queda con 20% de batería
        self.assertTrue(dron.necesita_recarga())
        
        # Cargar batería
        dron.cambiar_estado(EstadoDron.CARGANDO)
        cantidad_cargada = dron.cargar_bateria()
        
        self.assertEqual(cantidad_cargada, 80.0)
        self.assertEqual(dron.ciclos_carga, 1)
        self.assertFalse(dron.necesita_recarga())
    
    def test_transiciones_estado_completas(self):
        """Prueba flujo completo de transiciones de estado"""
        dron = Dron("D013", "Test Model", 100.0, 5.0)
        
        # Disponible -> Mantenimiento -> Fuera de servicio -> Mantenimiento -> Disponible
        self.assertTrue(dron.cambiar_estado(EstadoDron.MANTENIMIENTO))
        self.assertTrue(dron.cambiar_estado(EstadoDron.FUERA_DE_SERVICIO))
        self.assertTrue(dron.cambiar_estado(EstadoDron.MANTENIMIENTO))
        self.assertTrue(dron.cambiar_estado(EstadoDron.DISPONIBLE))
        
        self.assertEqual(dron.estado, EstadoDron.DISPONIBLE)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)

import unittest
import sys
import os
from datetime import datetime, timedelta

# Agregar el path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.charging_station import EstacionRecarga, EstadoEstacion, TipoRecarga
from domain.drone import Dron, EstadoDron


class TestEnums(unittest.TestCase):
    """Pruebas para los enums de la estación de recarga"""
    
    def test_estado_estacion(self):
        """Prueba que todos los estados de estación estén definidos"""
        estados_esperados = ['disponible', 'ocupada', 'mantenimiento', 'fuera_de_servicio']
        estados_reales = [estado.value for estado in EstadoEstacion]
        
        for estado in estados_esperados:
            self.assertIn(estado, estados_reales)
    
    def test_tipo_recarga(self):
        """Prueba que todos los tipos de recarga estén definidos"""
        tipos_esperados = ['rapida', 'normal', 'lenta']
        tipos_reales = [tipo.value for tipo in TipoRecarga]
        
        for tipo in tipos_esperados:
            self.assertIn(tipo, tipos_reales)


class TestEstacionRecarga(unittest.TestCase):
    """Pruebas principales para la clase EstacionRecarga"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.estacion = EstacionRecarga(
            estacion_id="EST001",
            nodo_id="NODO_A",
            capacidad_maxima=2,
            tipos_recarga=[TipoRecarga.NORMAL, TipoRecarga.RAPIDA],
            eficiencia_energetica=0.95,
            costo_por_kwh=0.20,
            tiempo_base_carga=60.0
        )
        
        # Crear drones de prueba
        self.dron1 = Dron("D001", "Modelo A", 100.0, 5.0, bateria_actual=50.0)
        self.dron2 = Dron("D002", "Modelo B", 120.0, 6.0, bateria_actual=30.0)
        self.dron3 = Dron("D003", "Modelo C", 80.0, 4.0, bateria_actual=20.0)
    
    def test_inicializacion_estacion(self):
        """Prueba la inicialización correcta de la estación"""
        self.assertEqual(self.estacion.estacion_id, "EST001")
        self.assertEqual(self.estacion.nodo_id, "NODO_A")
        self.assertEqual(self.estacion.capacidad_maxima, 2)
        self.assertEqual(self.estacion.eficiencia_energetica, 0.95)
        self.assertEqual(self.estacion.costo_por_kwh, 0.20)
        self.assertEqual(self.estacion.estado, EstadoEstacion.DISPONIBLE)
        self.assertEqual(len(self.estacion.drones_cargando), 0)
        self.assertEqual(len(self.estacion.cola_espera), 0)
    
    def test_inicializacion_valores_defecto(self):
        """Prueba inicialización con valores por defecto"""
        estacion_simple = EstacionRecarga("EST002", "NODO_B")
        
        self.assertEqual(estacion_simple.capacidad_maxima, 1)
        self.assertEqual(estacion_simple.tipos_recarga, [TipoRecarga.NORMAL])
        self.assertEqual(estacion_simple.eficiencia_energetica, 0.95)
        self.assertEqual(estacion_simple.costo_por_kwh, 0.15)
        self.assertTrue(estacion_simple.disponible)
    
    def test_validacion_eficiencia(self):
        """Prueba validación de eficiencia energética"""
        # Eficiencia mayor a 1.0
        estacion1 = EstacionRecarga("EST003", "NODO_C", eficiencia_energetica=1.5)
        self.assertEqual(estacion1.eficiencia_energetica, 1.0)
        
        # Eficiencia negativa
        estacion2 = EstacionRecarga("EST004", "NODO_D", eficiencia_energetica=-0.1)
        self.assertEqual(estacion2.eficiencia_energetica, 0.0)
    
    def test_esta_disponible(self):
        """Prueba verificación de disponibilidad"""
        # Estación nueva debe estar disponible
        self.assertTrue(self.estacion.esta_disponible())
        
        # Ocupar completamente la estación
        self.estacion.iniciar_carga(self.dron1)
        self.estacion.iniciar_carga(self.dron2)
        
        # Ahora no debe estar disponible
        self.assertFalse(self.estacion.esta_disponible())
    
    def test_tiene_espacio(self):
        """Prueba verificación de espacio disponible"""
        self.assertTrue(self.estacion.tiene_espacio())
        
        # Agregar un dron
        self.estacion.iniciar_carga(self.dron1)
        self.assertTrue(self.estacion.tiene_espacio())
        
        # Agregar segundo dron (llenar capacidad)
        self.estacion.iniciar_carga(self.dron2)
        self.assertFalse(self.estacion.tiene_espacio())
    
    def test_calcular_tiempo_carga(self):
        """Prueba cálculo de tiempo de carga"""
        # Carga normal
        tiempo_normal = self.estacion.calcular_tiempo_carga(self.dron1, TipoRecarga.NORMAL)
        self.assertGreater(tiempo_normal, 0)
        
        # Carga rápida debe ser más rápida
        tiempo_rapido = self.estacion.calcular_tiempo_carga(self.dron1, TipoRecarga.RAPIDA)
        self.assertLess(tiempo_rapido, tiempo_normal)
        
        # Carga lenta debe ser más lenta
        estacion_con_lenta = EstacionRecarga("EST_LENTA", "NODO_L", tipos_recarga=[TipoRecarga.LENTA])
        tiempo_lento = estacion_con_lenta.calcular_tiempo_carga(self.dron1, TipoRecarga.LENTA)
        self.assertGreater(tiempo_lento, tiempo_normal)
    
    def test_calcular_costo_carga(self):
        """Prueba cálculo de costo de carga"""
        # Carga normal
        costo_normal = self.estacion.calcular_costo_carga(self.dron1, TipoRecarga.NORMAL)
        self.assertGreater(costo_normal, 0)
          # Carga rápida debe ser más cara
        costo_rapido = self.estacion.calcular_costo_carga(self.dron1, TipoRecarga.RAPIDA)
        self.assertGreater(costo_rapido, costo_normal)
        
        # Dron con menos batería debe costar más cargar (necesita más energía)
        costo_bateria_baja = self.estacion.calcular_costo_carga(self.dron2, TipoRecarga.NORMAL)
        costo_bateria_alta = self.estacion.calcular_costo_carga(self.dron1, TipoRecarga.NORMAL)
        self.assertGreater(costo_bateria_baja, costo_bateria_alta)
    
    def test_iniciar_carga_exitosa(self):
        """Prueba inicio exitoso de carga"""
        bateria_inicial = self.dron1.bateria_actual
        estado_inicial = self.dron1.estado
        
        resultado = self.estacion.iniciar_carga(self.dron1, TipoRecarga.NORMAL, 80.0)
        
        self.assertTrue(resultado)
        self.assertEqual(self.dron1.estado, EstadoDron.CARGANDO)
        self.assertEqual(self.dron1.posicion_actual, "NODO_A")
        self.assertIn("D001", self.estacion.drones_cargando)
        self.assertEqual(len(self.estacion.drones_cargando), 1)
    
    def test_iniciar_carga_estacion_llena(self):
        """Prueba inicio de carga con estación llena"""
        # Llenar la estación
        self.estacion.iniciar_carga(self.dron1)
        self.estacion.iniciar_carga(self.dron2)
        
        # Intentar agregar tercer dron
        resultado = self.estacion.iniciar_carga(self.dron3)
        self.assertFalse(resultado)
        self.assertEqual(self.dron3.estado, EstadoDron.DISPONIBLE)
        self.assertNotIn("D003", self.estacion.drones_cargando)
    
    def test_iniciar_carga_dron_duplicado(self):
        """Prueba inicio de carga con dron ya cargando"""
        # Iniciar carga primera vez
        resultado1 = self.estacion.iniciar_carga(self.dron1)
        self.assertTrue(resultado1)
        
        # Intentar iniciar carga nuevamente
        resultado2 = self.estacion.iniciar_carga(self.dron1)
        self.assertFalse(resultado2)
        self.assertEqual(len(self.estacion.drones_cargando), 1)
    
    def test_iniciar_carga_tipo_no_disponible(self):
        """Prueba inicio de carga con tipo no disponible"""
        estacion_limitada = EstacionRecarga("EST_LIM", "NODO_L", tipos_recarga=[TipoRecarga.NORMAL])
        
        # Intentar carga rápida en estación que solo tiene normal
        resultado = estacion_limitada.iniciar_carga(self.dron1, TipoRecarga.RAPIDA)
        
        # Debe usar el tipo disponible (normal)
        self.assertTrue(resultado)
        info_carga = estacion_limitada.drones_cargando["D001"]
        self.assertEqual(info_carga['tipo_recarga'], TipoRecarga.NORMAL)
    
    def test_finalizar_carga(self):
        """Prueba finalización de carga"""
        # Iniciar carga
        self.estacion.iniciar_carga(self.dron1, TipoRecarga.NORMAL, 80.0)
        bateria_antes = self.dron1.bateria_actual
        
        # Finalizar carga
        resultado = self.estacion.finalizar_carga("D001")
        
        self.assertIsInstance(resultado, dict)
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["dron_id"], "D001")
        self.assertGreater(self.dron1.bateria_actual, bateria_antes)
        self.assertEqual(self.dron1.estado, EstadoDron.DISPONIBLE)
        self.assertNotIn("D001", self.estacion.drones_cargando)
        self.assertEqual(self.estacion.total_cargas_realizadas, 1)
    
    def test_finalizar_carga_dron_inexistente(self):
        """Prueba finalización de carga con dron inexistente"""
        resultado = self.estacion.finalizar_carga("D999")
        
        self.assertIn("error", resultado)
        self.assertEqual(self.estacion.total_cargas_realizadas, 0)
    
    def test_obtener_tiempo_espera_estimado(self):
        """Prueba cálculo de tiempo de espera estimado"""
        # Sin drones cargando
        self.assertEqual(self.estacion.obtener_tiempo_espera_estimado(), 0.0)
        
        # Con espacio disponible
        self.estacion.iniciar_carga(self.dron1)
        self.assertEqual(self.estacion.obtener_tiempo_espera_estimado(), 0.0)
        
        # Estación llena
        self.estacion.iniciar_carga(self.dron2)
        tiempo_espera = self.estacion.obtener_tiempo_espera_estimado()
        self.assertGreaterEqual(tiempo_espera, 0.0)
    
    def test_agregar_a_cola(self):
        """Prueba agregar drones a cola de espera"""
        # Agregar a cola vacía
        resultado1 = self.estacion.agregar_a_cola("D003")
        self.assertTrue(resultado1)
        self.assertIn("D003", self.estacion.cola_espera)
        
        # Intentar agregar duplicado
        resultado2 = self.estacion.agregar_a_cola("D003")
        self.assertFalse(resultado2)
        self.assertEqual(self.estacion.cola_espera.count("D003"), 1)
        
        # Intentar agregar dron que ya está cargando
        self.estacion.iniciar_carga(self.dron1)
        resultado3 = self.estacion.agregar_a_cola("D001")
        self.assertFalse(resultado3)
    
    def test_cambiar_estado_valido(self):
        """Prueba cambios de estado válidos"""
        # Disponible -> Ocupada
        self.assertTrue(self.estacion.cambiar_estado(EstadoEstacion.OCUPADA))
        self.assertEqual(self.estacion.estado, EstadoEstacion.OCUPADA)
        
        # Ocupada -> Disponible
        self.assertTrue(self.estacion.cambiar_estado(EstadoEstacion.DISPONIBLE))
        self.assertEqual(self.estacion.estado, EstadoEstacion.DISPONIBLE)
        
        # Disponible -> Mantenimiento
        self.assertTrue(self.estacion.cambiar_estado(EstadoEstacion.MANTENIMIENTO))
        self.assertEqual(self.estacion.estado, EstadoEstacion.MANTENIMIENTO)
    
    def test_cambiar_estado_invalido(self):
        """Prueba cambios de estado inválidos"""
        # Disponible -> Fuera de servicio (no permitido directamente)
        resultado = self.estacion.cambiar_estado(EstadoEstacion.FUERA_DE_SERVICIO)
        self.assertFalse(resultado)
        self.assertEqual(self.estacion.estado, EstadoEstacion.DISPONIBLE)
    
    def test_obtener_metricas(self):
        """Prueba obtención de métricas completas"""
        metricas = self.estacion.obtener_metricas()
        
        campos_esperados = [
            'estacion_id', 'nodo_id', 'estado', 'capacidad_maxima',
            'drones_cargando', 'cola_espera', 'disponible', 'tipos_recarga',
            'eficiencia_energetica', 'costo_por_kwh', 'tiempo_base_carga',
            'total_cargas_realizadas', 'energia_total_suministrada',
            'tiempo_operativo_total', 'ingresos_generados',
            'tiempo_espera_estimado', 'ultima_actualizacion'
        ]
        
        for campo in campos_esperados:
            self.assertIn(campo, metricas)
        
        self.assertEqual(metricas['estacion_id'], "EST001")
        self.assertEqual(metricas['nodo_id'], "NODO_A")
        self.assertEqual(metricas['estado'], "disponible")
        self.assertEqual(metricas['capacidad_maxima'], 2)
    
    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        dict_estacion = self.estacion.to_dict()
        
        self.assertIsInstance(dict_estacion, dict)
        self.assertEqual(dict_estacion['estacion_id'], "EST001")
        self.assertEqual(dict_estacion['nodo_id'], "NODO_A")
    
    def test_from_dict(self):
        """Prueba creación desde diccionario"""
        # Realizar algunas operaciones para cambiar métricas
        self.estacion.iniciar_carga(self.dron1)
        self.estacion.finalizar_carga("D001")
        
        dict_original = self.estacion.to_dict()
        estacion_restaurada = EstacionRecarga.from_dict(dict_original)
        
        self.assertEqual(estacion_restaurada.estacion_id, self.estacion.estacion_id)
        self.assertEqual(estacion_restaurada.nodo_id, self.estacion.nodo_id)
        self.assertEqual(estacion_restaurada.capacidad_maxima, self.estacion.capacidad_maxima)
        self.assertEqual(estacion_restaurada.eficiencia_energetica, self.estacion.eficiencia_energetica)
        self.assertEqual(estacion_restaurada.total_cargas_realizadas, self.estacion.total_cargas_realizadas)
        self.assertEqual(estacion_restaurada.estado, self.estacion.estado)
    
    def test_str_representation(self):
        """Prueba representación en string"""
        str_estacion = str(self.estacion)
        
        self.assertIn("EST001", str_estacion)
        self.assertIn("NODO_A", str_estacion)
        self.assertIn("disponible", str_estacion)
        self.assertIn("0/2", str_estacion)


class TestProcesoCargaCompleto(unittest.TestCase):
    """Pruebas para el proceso completo de carga"""
    
    def setUp(self):
        """Configuración inicial"""
        self.estacion = EstacionRecarga(
            estacion_id="EST_TEST",
            nodo_id="NODO_TEST",
            capacidad_maxima=1,
            tipos_recarga=[TipoRecarga.NORMAL, TipoRecarga.RAPIDA]
        )
        self.dron = Dron("D_TEST", "Modelo Test", 100.0, 5.0, bateria_actual=25.0)
    
    def test_ciclo_carga_completo(self):
        """Prueba un ciclo completo de carga"""
        # Estado inicial
        bateria_inicial = self.dron.bateria_actual
        posicion_inicial = self.dron.posicion_actual
        
        # Iniciar carga
        resultado_inicio = self.estacion.iniciar_carga(self.dron, TipoRecarga.NORMAL, 90.0)
        self.assertTrue(resultado_inicio)
        self.assertEqual(self.dron.estado, EstadoDron.CARGANDO)
        self.assertEqual(self.dron.posicion_actual, "NODO_TEST")
        self.assertEqual(self.estacion.estado, EstadoEstacion.OCUPADA)
        
        # Finalizar carga
        resultado_fin = self.estacion.finalizar_carga("D_TEST")
        self.assertNotIn("error", resultado_fin)
        self.assertEqual(self.dron.estado, EstadoDron.DISPONIBLE)
        self.assertGreater(self.dron.bateria_actual, bateria_inicial)
        self.assertEqual(self.estacion.estado, EstadoEstacion.DISPONIBLE)
        
        # Verificar métricas actualizadas
        self.assertEqual(self.estacion.total_cargas_realizadas, 1)
        self.assertGreater(self.estacion.energia_total_suministrada, 0)
        self.assertGreater(self.estacion.ingresos_generados, 0)
    
    def test_eficiencia_tipos_recarga(self):
        """Prueba eficiencia de diferentes tipos de recarga"""
        dron_rapida = Dron("D_RAPIDA", "Test", 100.0, 5.0, bateria_actual=50.0)
        dron_normal = Dron("D_NORMAL", "Test", 100.0, 5.0, bateria_actual=50.0)
        
        estacion_multi = EstacionRecarga(
            "EST_MULTI", "NODO_MULTI", 
            capacidad_maxima=2,
            tipos_recarga=[TipoRecarga.NORMAL, TipoRecarga.RAPIDA]
        )
        
        # Carga rápida
        tiempo_rapida = estacion_multi.calcular_tiempo_carga(dron_rapida, TipoRecarga.RAPIDA)
        costo_rapida = estacion_multi.calcular_costo_carga(dron_rapida, TipoRecarga.RAPIDA)
        
        # Carga normal
        tiempo_normal = estacion_multi.calcular_tiempo_carga(dron_normal, TipoRecarga.NORMAL)
        costo_normal = estacion_multi.calcular_costo_carga(dron_normal, TipoRecarga.NORMAL)
        
        # Verificar relaciones esperadas
        self.assertLess(tiempo_rapida, tiempo_normal)  # Rápida es más rápida
        self.assertGreater(costo_rapida, costo_normal)  # Rápida es más cara


class TestCasosEspeciales(unittest.TestCase):
    """Pruebas para casos especiales y límite"""
    
    def test_estacion_fuera_de_servicio(self):
        """Prueba estación fuera de servicio"""
        estacion = EstacionRecarga("EST_ROTA", "NODO_ROTO", disponible=False)
        dron = Dron("D_TEST", "Test", 100.0, 5.0, bateria_actual=50.0)
        
        self.assertEqual(estacion.estado, EstadoEstacion.FUERA_DE_SERVICIO)
        self.assertFalse(estacion.esta_disponible())
        
        resultado = estacion.iniciar_carga(dron)
        self.assertFalse(resultado)
    
    def test_verificar_cargas_completadas(self):
        """Prueba verificación automática de cargas completadas"""
        estacion = EstacionRecarga("EST_AUTO", "NODO_AUTO")
        dron = Dron("D_AUTO", "Test", 100.0, 5.0, bateria_actual=50.0)
        
        # Iniciar carga
        estacion.iniciar_carga(dron)
        
        # Simular tiempo transcurrido modificando manualmente
        info_carga = estacion.drones_cargando["D_AUTO"]
        info_carga['fin_estimado'] = datetime.now() - timedelta(minutes=1)  # Ya debería haber terminado
        
        # Verificar cargas completadas
        cargas_finalizadas = estacion.verificar_cargas_completadas()
        
        self.assertEqual(len(cargas_finalizadas), 1)
        self.assertEqual(cargas_finalizadas[0]["dron_id"], "D_AUTO")
        self.assertNotIn("D_AUTO", estacion.drones_cargando)
    
    def test_multiples_drones_simultaneos(self):
        """Prueba múltiples drones cargando simultáneamente"""
        estacion = EstacionRecarga("EST_MULTI", "NODO_MULTI", capacidad_maxima=3)
        drones = [
            Dron("D1", "Test", 100.0, 5.0, bateria_actual=30.0),
            Dron("D2", "Test", 100.0, 5.0, bateria_actual=40.0),
            Dron("D3", "Test", 100.0, 5.0, bateria_actual=20.0)
        ]
        
        # Iniciar carga para todos
        for dron in drones:
            resultado = estacion.iniciar_carga(dron)
            self.assertTrue(resultado)
        
        self.assertEqual(len(estacion.drones_cargando), 3)
        self.assertEqual(estacion.estado, EstadoEstacion.OCUPADA)
        
        # Finalizar una carga
        estacion.finalizar_carga("D1")
        self.assertEqual(len(estacion.drones_cargando), 2)
        self.assertEqual(estacion.estado, EstadoEstacion.DISPONIBLE)  # Tiene espacio nuevamente


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)

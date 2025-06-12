"""
Tests unitarios para el validador de simulación

Estas pruebas cubren:
- Validación de parámetros básicos
- Validación de distribución de roles
- Validación de conectividad
- Validación de rendimiento
- Validación de lógica de negocio
- Configuraciones recomendadas
"""

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sim.validador_simulacion import (
    ValidadorSimulacion, 
    ResultadoValidacion, 
    ErrorValidacion, 
    TipoError
)


class TestValidadorSimulacion(unittest.TestCase):
    """Pruebas para el ValidadorSimulacion"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_inicializacion(self):
        """Verifica la inicialización correcta del validador"""
        self.assertIsInstance(self.validador.limites, dict)
        self.assertIsInstance(self.validador.rendimiento, dict)
        
        # Verificar que los límites estén definidos
        self.assertIn('nodos', self.validador.limites)
        self.assertIn('probabilidad_arista', self.validador.limites)
        self.assertIn('porcentajes', self.validador.limites)
        self.assertIn('semilla', self.validador.limites)
    
    def test_validar_parametros_basicos_validos(self):
        """Verifica validación de parámetros básicos válidos"""
        config = {
            'num_nodos': 50,
            'prob_arista': 0.3,
            'semilla': 42
        }
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 0)
        self.assertEqual(len(resultado.informacion), 1)  # Información sobre semilla
    
    def test_validar_nodos_minimo(self):
        """Verifica validación de número mínimo de nodos"""
        config = {'num_nodos': 0}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "NODOS_MINIMO")
        self.assertEqual(resultado.errores[0].tipo, TipoError.CRITICO)
    
    def test_validar_nodos_maximo(self):
        """Verifica validación de número máximo de nodos"""
        config = {'num_nodos': 1500}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "NODOS_MAXIMO")
        self.assertEqual(resultado.errores[0].tipo, TipoError.CRITICO)
    
    def test_validar_nodos_lento(self):
        """Verifica advertencia para nodos que pueden ser lentos"""
        config = {'num_nodos': 600}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "NODOS_LENTO")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_probabilidad_arista_rango(self):
        """Verifica validación de rango de probabilidad de arista"""
        config = {'num_nodos': 10, 'prob_arista': 1.5}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertGreaterEqual(len(resultado.errores), 1)
        self.assertTrue(any(e.codigo == "PROB_ARISTA_RANGO" for e in resultado.errores))
    
    def test_validar_probabilidad_arista_baja(self):
        """Verifica advertencia para probabilidad de arista muy baja"""
        config = {'num_nodos': 10, 'prob_arista': 0.05}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "PROB_ARISTA_BAJA")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_probabilidad_arista_alta(self):
        """Verifica advertencia para probabilidad de arista muy alta"""
        config = {'num_nodos': 10, 'prob_arista': 0.9}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "PROB_ARISTA_ALTA")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_semilla_rango(self):
        """Verifica validación de rango de semilla"""
        config = {'num_nodos': 10, 'prob_arista': 0.3, 'semilla': 0}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertGreaterEqual(len(resultado.errores), 1)
        self.assertTrue(any(e.codigo == "SEMILLA_RANGO" for e in resultado.errores))
    
    def test_validar_semilla_valida(self):
        """Verifica información para semilla válida"""
        config = {'num_nodos': 10, 'prob_arista': 0.3, 'semilla': 42}
        
        resultado = self.validador._validar_parametros_basicos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.informacion), 1)
        self.assertEqual(resultado.informacion[0].codigo, "SEMILLA_CONFIGURADA")
        self.assertEqual(resultado.informacion[0].tipo, TipoError.INFORMATIVO)


class TestValidacionDistribucionRoles(unittest.TestCase):
    """Pruebas para validación de distribución de roles"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_validar_distribucion_roles_valida(self):
        """Verifica validación de distribución de roles válida"""
        config = {
            'num_nodos': 20,
            'pct_almacenamiento': 20.0,
            'pct_recarga': 30.0,
            'pct_cliente': 50.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 0)
        self.assertEqual(len(resultado.informacion), 1)  # Distribución estimada
    
    def test_validar_porcentaje_almacenamiento_rango(self):
        """Verifica validación de rango de porcentaje de almacenamiento"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 150.0,
            'pct_recarga': 30.0,
            'pct_cliente': 50.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertGreaterEqual(len(resultado.errores), 1)
        self.assertTrue(any(e.codigo == "PORCENTAJE_ALMACENAMIENTO_RANGO" for e in resultado.errores))
    
    def test_validar_porcentaje_recarga_rango(self):
        """Verifica validación de rango de porcentaje de recarga"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 20.0,
            'pct_recarga': -10.0,
            'pct_cliente': 50.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertGreaterEqual(len(resultado.errores), 1)
        self.assertTrue(any(e.codigo == "PORCENTAJE_RECARGA_RANGO" for e in resultado.errores))
    
    def test_validar_porcentaje_cliente_rango(self):
        """Verifica validación de rango de porcentaje de cliente"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 20.0,
            'pct_recarga': 30.0,
            'pct_cliente': 200.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertGreaterEqual(len(resultado.errores), 1)
        self.assertTrue(any(e.codigo == "PORCENTAJE_CLIENTE_RANGO" for e in resultado.errores))
    
    def test_validar_suma_porcentajes(self):
        """Verifica validación de suma de porcentajes"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 20.0,
            'pct_recarga': 30.0,
            'pct_cliente': 40.0  # Suma = 90%
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "PORCENTAJES_SUMA")
        self.assertEqual(resultado.errores[0].tipo, TipoError.CRITICO)
    
    def test_validar_sin_almacenamiento(self):
        """Verifica advertencia cuando no hay almacenamiento"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 0.0,
            'pct_recarga': 30.0,
            'pct_cliente': 70.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "SIN_ALMACENAMIENTO")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_sin_recarga(self):
        """Verifica advertencia cuando no hay recarga"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 20.0,
            'pct_recarga': 0.0,
            'pct_cliente': 80.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "SIN_RECARGA")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_distribucion_estimada(self):
        """Verifica información de distribución estimada"""
        config = {
            'num_nodos': 10,
            'pct_almacenamiento': 20.0,
            'pct_recarga': 30.0,
            'pct_cliente': 50.0
        }
        
        resultado = self.validador._validar_distribucion_roles(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.informacion), 1)
        self.assertEqual(resultado.informacion[0].codigo, "DISTRIBUCION_ESTIMADA")
        self.assertEqual(resultado.informacion[0].tipo, TipoError.INFORMATIVO)


class TestValidacionConectividad(unittest.TestCase):
    """Pruebas para validación de conectividad"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_validar_conectividad_valida(self):
        """Verifica validación de conectividad válida"""
        config = {
            'num_nodos': 10,
            'prob_arista': 0.3
        }
        
        resultado = self.validador._validar_conectividad(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.informacion), 1)  # Aristas estimadas
    
    def test_validar_densidad_baja(self):
        """Verifica advertencia para densidad muy baja"""
        config = {
            'num_nodos': 50,
            'prob_arista': 0.01
        }
        
        resultado = self.validador._validar_conectividad(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "DENSIDAD_BAJA")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_densidad_alta(self):
        """Verifica advertencia para densidad muy alta"""
        config = {
            'num_nodos': 10,
            'prob_arista': 0.9
        }
        
        resultado = self.validador._validar_conectividad(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "DENSIDAD_ALTA")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_aristas_estimadas(self):
        """Verifica información de aristas estimadas"""
        config = {
            'num_nodos': 5,
            'prob_arista': 0.3
        }
        
        resultado = self.validador._validar_conectividad(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.informacion), 1)
        self.assertEqual(resultado.informacion[0].codigo, "ARISTAS_ESTIMADAS")
        self.assertEqual(resultado.informacion[0].tipo, TipoError.INFORMATIVO)


class TestValidacionRendimiento(unittest.TestCase):
    """Pruebas para validación de rendimiento"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_validar_rendimiento_rapido(self):
        """Verifica información para simulación rápida"""
        config = {'num_nodos': 30}
        
        resultado = self.validador._validar_rendimiento(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 0)
        self.assertEqual(len(resultado.informacion), 1)
        self.assertEqual(resultado.informacion[0].codigo, "RENDIMIENTO_RAPIDO")
        self.assertEqual(resultado.informacion[0].tipo, TipoError.INFORMATIVO)
    
    def test_validar_rendimiento_normal(self):
        """Verifica advertencia para simulación normal"""
        config = {'num_nodos': 300}
        
        resultado = self.validador._validar_rendimiento(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "RENDIMIENTO_NORMAL")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_rendimiento_lento(self):
        """Verifica advertencia para simulación lenta"""
        config = {'num_nodos': 600}
        
        resultado = self.validador._validar_rendimiento(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "RENDIMIENTO_LENTO")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)


class TestValidacionLogicaNegocio(unittest.TestCase):
    """Pruebas para validación de lógica de negocio"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_validar_pocos_clientes(self):
        """Verifica advertencia para pocos clientes en red grande"""
        config = {
            'num_nodos': 20,
            'pct_almacenamiento': 30.0,
            'pct_recarga': 40.0,
            'pct_cliente': 30.0
        }
        
        resultado = self.validador._validar_logica_negocio(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "POCOS_CLIENTES")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_muchos_almacenes(self):
        """Verifica advertencia para muchos almacenes"""
        config = {
            'num_nodos': 20,
            'pct_almacenamiento': 40.0,
            'pct_recarga': 20.0,
            'pct_cliente': 40.0
        }
        
        resultado = self.validador._validar_logica_negocio(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "MUCHOS_ALMACENES")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)
    
    def test_validar_nodo_unico_recarga(self):
        """Verifica advertencia para nodo único de recarga"""
        config = {
            'num_nodos': 1,
            'pct_almacenamiento': 0.0,
            'pct_recarga': 100.0,
            'pct_cliente': 0.0
        }
        
        resultado = self.validador._validar_logica_negocio(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "NODO_UNICO_RECARGA")
        self.assertEqual(resultado.advertencias[0].tipo, TipoError.ADVERTENCIA)


class TestValidacionCompleta(unittest.TestCase):
    """Pruebas para validación completa de configuración"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_validacion_completa_valida(self):
        """Verifica validación completa de configuración válida"""
        config = {
            'num_nodos': 20,
            'prob_arista': 0.3,
            'pct_almacenamiento': 20.0,
            'pct_recarga': 30.0,
            'pct_cliente': 50.0,
            'semilla': 42
        }
        
        resultado = self.validador.validar_configuracion_completa(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertTrue(resultado.puede_ejecutar)
        self.assertFalse(resultado.tiene_errores_criticos)
    
    def test_validacion_completa_invalida(self):
        """Verifica validación completa de configuración inválida"""
        config = {
            'num_nodos': 0,  # Inválido
            'prob_arista': 1.5,  # Inválido
            'pct_almacenamiento': 20.0,
            'pct_recarga': 30.0,
            'pct_cliente': 50.0
        }
        
        resultado = self.validador.validar_configuracion_completa(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertFalse(resultado.puede_ejecutar)
        self.assertTrue(resultado.tiene_errores_criticos)
        self.assertGreater(len(resultado.errores), 0)
    
    def test_validacion_completa_con_advertencias(self):
        """Verifica validación completa con advertencias"""
        config = {
            'num_nodos': 600,  # Lento
            'prob_arista': 0.05,  # Muy baja
            'pct_almacenamiento': 0.0,  # Sin almacenamiento
            'pct_recarga': 30.0,
            'pct_cliente': 70.0
        }
        
        resultado = self.validador.validar_configuracion_completa(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertTrue(resultado.puede_ejecutar)
        self.assertFalse(resultado.tiene_errores_criticos)
        self.assertGreater(len(resultado.advertencias), 0)


class TestConfiguracionesRecomendadas(unittest.TestCase):
    """Pruebas para configuraciones recomendadas"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_configuracion_balanceada(self):
        """Verifica configuración recomendada balanceada"""
        config = self.validador.obtener_configuracion_recomendada(20, "balanceado")
        
        self.assertEqual(config['num_nodos'], 20)
        self.assertEqual(config['pct_almacenamiento'], 20.0)
        self.assertEqual(config['pct_recarga'], 30.0)
        self.assertEqual(config['pct_cliente'], 50.0)
        self.assertEqual(config['prob_arista'], 0.3)
        self.assertEqual(config['semilla'], 42)
    
    def test_configuracion_logistica(self):
        """Verifica configuración recomendada logística"""
        config = self.validador.obtener_configuracion_recomendada(30, "logistica")
        
        self.assertEqual(config['num_nodos'], 30)
        self.assertEqual(config['pct_almacenamiento'], 15.0)
        self.assertEqual(config['pct_recarga'], 25.0)
        self.assertEqual(config['pct_cliente'], 60.0)
        self.assertEqual(config['prob_arista'], 0.25)
    
    def test_configuracion_servicio(self):
        """Verifica configuración recomendada servicio"""
        config = self.validador.obtener_configuracion_recomendada(25, "servicio")
        
        self.assertEqual(config['num_nodos'], 25)
        self.assertEqual(config['pct_almacenamiento'], 10.0)
        self.assertEqual(config['pct_recarga'], 40.0)
        self.assertEqual(config['pct_cliente'], 50.0)
        self.assertEqual(config['prob_arista'], 0.35)
    
    def test_configuracion_escenario_invalido(self):
        """Verifica configuración con escenario inválido (debe usar balanceado)"""
        config = self.validador.obtener_configuracion_recomendada(15, "invalido")
        
        # Debe usar configuración balanceada por defecto
        self.assertEqual(config['pct_almacenamiento'], 20.0)
        self.assertEqual(config['pct_recarga'], 30.0)
        self.assertEqual(config['pct_cliente'], 50.0)
    
    def test_validar_configuracion_recomendada(self):
        """Verifica que la configuración recomendada sea válida"""
        config = self.validador.obtener_configuracion_recomendada(50, "balanceado")
        
        resultado = self.validador.validar_configuracion_completa(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertTrue(resultado.puede_ejecutar)
        self.assertFalse(resultado.tiene_errores_criticos)


class TestErrorValidacion(unittest.TestCase):
    """Pruebas para la clase ErrorValidacion"""
    
    def test_error_critico_str(self):
        """Verifica representación string de error crítico"""
        error = ErrorValidacion(
            tipo=TipoError.CRITICO,
            codigo="TEST_ERROR",
            mensaje="Error de prueba",
            parametro="test_param",
            valor_actual=10,
            valor_recomendado=20
        )
        
        self.assertEqual(str(error), "❌ Error de prueba")
    
    def test_error_advertencia_str(self):
        """Verifica representación string de advertencia"""
        error = ErrorValidacion(
            tipo=TipoError.ADVERTENCIA,
            codigo="TEST_WARNING",
            mensaje="Advertencia de prueba",
            parametro="test_param",
            valor_actual=10,
            valor_recomendado=20
        )
        
        self.assertEqual(str(error), "⚠️ Advertencia de prueba")
    
    def test_error_informativo_str(self):
        """Verifica representación string de información"""
        error = ErrorValidacion(
            tipo=TipoError.INFORMATIVO,
            codigo="TEST_INFO",
            mensaje="Información de prueba",
            parametro="test_param",
            valor_actual=10,
            valor_recomendado=20
        )
        
        self.assertEqual(str(error), "ℹ️ Información de prueba")


class TestResultadoValidacion(unittest.TestCase):
    """Pruebas para la clase ResultadoValidacion"""
    
    def test_resultado_valido_str(self):
        """Verifica representación string de resultado válido"""
        resultado = ResultadoValidacion(
            es_valida=True,
            errores=[],
            advertencias=[],
            informacion=[]
        )
        
        self.assertEqual(str(resultado), "✅ Configuración válida")
    
    def test_resultado_invalido_str(self):
        """Verifica representación string de resultado inválido"""
        errores = [
            ErrorValidacion(TipoError.CRITICO, "ERROR1", "Error 1"),
            ErrorValidacion(TipoError.CRITICO, "ERROR2", "Error 2")
        ]
        
        resultado = ResultadoValidacion(
            es_valida=False,
            errores=errores,
            advertencias=[],
            informacion=[]
        )
        
        self.assertEqual(str(resultado), "❌ Configuración inválida (2 errores)")
    
    def test_tiene_errores_criticos(self):
        """Verifica detección de errores críticos"""
        errores = [
            ErrorValidacion(TipoError.CRITICO, "ERROR1", "Error crítico"),
            ErrorValidacion(TipoError.ADVERTENCIA, "WARNING1", "Advertencia")
        ]
        
        resultado = ResultadoValidacion(
            es_valida=False,
            errores=errores,
            advertencias=[],
            informacion=[]
        )
        
        self.assertTrue(resultado.tiene_errores_criticos)
    
    def test_puede_ejecutar(self):
        """Verifica si se puede ejecutar la simulación"""
        # Caso válido sin errores críticos
        resultado_valido = ResultadoValidacion(
            es_valida=True,
            errores=[],
            advertencias=[],
            informacion=[]
        )
        self.assertTrue(resultado_valido.puede_ejecutar)
        
        # Caso inválido con errores críticos
        errores_criticos = [ErrorValidacion(TipoError.CRITICO, "ERROR1", "Error crítico")]
        resultado_invalido = ResultadoValidacion(
            es_valida=False,
            errores=errores_criticos,
            advertencias=[],
            informacion=[]
        )
        self.assertFalse(resultado_invalido.puede_ejecutar)


class TestValidacionParametrosDatos(unittest.TestCase):
    """Pruebas para validación de parámetros de datos"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_validar_clientes_por_nodo_valido(self):
        """Verifica validación de clientes por nodo válido"""
        config = {'clientes_por_nodo': 3}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
    
    def test_validar_clientes_por_nodo_invalido(self):
        """Verifica validación de clientes por nodo inválido"""
        config = {'clientes_por_nodo': 15}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "CLIENTES_POR_NODO_RANGO")
    
    def test_validar_ordenes_por_cliente_valido(self):
        """Verifica validación de órdenes por cliente válido"""
        config = {'ordenes_por_cliente': 10}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
    
    def test_validar_ordenes_por_cliente_invalido(self):
        """Verifica validación de órdenes por cliente inválido"""
        config = {'ordenes_por_cliente': 100}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "ORDENES_POR_CLIENTE_RANGO")
    
    def test_validar_bateria_dron_valido(self):
        """Verifica validación de batería de dron válida"""
        config = {'bateria_dron': 1000.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
    
    def test_validar_bateria_dron_invalido(self):
        """Verifica validación de batería de dron inválida"""
        config = {'bateria_dron': 50.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "BATERIA_DRON_RANGO")
    
    def test_validar_consumo_dron_valido(self):
        """Verifica validación de consumo de dron válido"""
        config = {'consumo_dron': 2.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
    
    def test_validar_consumo_dron_invalido(self):
        """Verifica validación de consumo de dron inválido"""
        config = {'consumo_dron': 15.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "CONSUMO_DRON_RANGO")
    
    def test_validar_capacidad_estacion_valido(self):
        """Verifica validación de capacidad de estación válida"""
        config = {'capacidad_estacion': 5}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
    
    def test_validar_capacidad_estacion_invalido(self):
        """Verifica validación de capacidad de estación inválida"""
        config = {'capacidad_estacion': 25}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "CAPACIDAD_ESTACION_RANGO")
    
    def test_validar_costo_recarga_valido(self):
        """Verifica validación de costo de recarga válido"""
        config = {'costo_recarga': 5.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 0)
    
    def test_validar_costo_recarga_invalido(self):
        """Verifica validación de costo de recarga inválido"""
        config = {'costo_recarga': 150.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertFalse(resultado.es_valida)
        self.assertEqual(len(resultado.errores), 1)
        self.assertEqual(resultado.errores[0].codigo, "COSTO_RECARGA_RANGO")
    
    def test_validar_distancia_ruta_alta(self):
        """Verifica advertencia para distancia de ruta muy alta"""
        config = {'max_distancia_ruta': 1500.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "DISTANCIA_RUTA_ALTA")
    
    def test_validar_margen_bateria_bajo(self):
        """Verifica advertencia para margen de batería muy bajo"""
        config = {'margen_bateria': 2.0}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.advertencias), 1)
        self.assertEqual(resultado.advertencias[0].codigo, "MARGEN_BATERIA_BAJO")
    
    def test_escenario_recomendado(self):
        """Verifica información de escenario recomendado"""
        config = {'num_nodos': 30, 'prob_arista': 0.3}
        
        resultado = self.validador._validar_parametros_datos(config)
        
        self.assertTrue(resultado.es_valida)
        self.assertEqual(len(resultado.informacion), 1)
        self.assertEqual(resultado.informacion[0].codigo, "ESCENARIO_RECOMENDADO")


class TestConfiguracionesEscenarios(unittest.TestCase):
    """Pruebas para configuraciones de escenarios específicos"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.validador = ValidadorSimulacion()
    
    def test_configuracion_pequena_ciudad(self):
        """Verifica configuración para pequeña ciudad"""
        config = self.validador.obtener_configuracion_recomendada(20, "pequena_ciudad")
        
        self.assertEqual(config['num_nodos'], 20)
        self.assertEqual(config['pct_almacenamiento'], 25.0)
        self.assertEqual(config['pct_recarga'], 35.0)
        self.assertEqual(config['pct_cliente'], 40.0)
        self.assertEqual(config['prob_arista'], 0.3)
        self.assertEqual(config['clientes_por_nodo'], 2)
        self.assertEqual(config['ordenes_por_cliente'], 5)
        self.assertEqual(config['bateria_dron'], 1000.0)
        self.assertEqual(config['consumo_dron'], 2.0)
        self.assertEqual(config['capacidad_estacion'], 3)
        self.assertEqual(config['costo_recarga'], 3.0)
    
    def test_configuracion_ciudad_mediana(self):
        """Verifica configuración para ciudad mediana"""
        config = self.validador.obtener_configuracion_recomendada(100, "ciudad_mediana")
        
        self.assertEqual(config['num_nodos'], 100)
        self.assertEqual(config['pct_almacenamiento'], 20.0)
        self.assertEqual(config['pct_recarga'], 30.0)
        self.assertEqual(config['pct_cliente'], 50.0)
        self.assertEqual(config['prob_arista'], 0.25)
        self.assertEqual(config['clientes_por_nodo'], 5)
        self.assertEqual(config['ordenes_por_cliente'], 10)
        self.assertEqual(config['bateria_dron'], 2000.0)
        self.assertEqual(config['consumo_dron'], 1.8)
        self.assertEqual(config['capacidad_estacion'], 5)
        self.assertEqual(config['costo_recarga'], 4.0)
    
    def test_configuracion_ciudad_grande(self):
        """Verifica configuración para ciudad grande"""
        config = self.validador.obtener_configuracion_recomendada(300, "ciudad_grande")
        
        self.assertEqual(config['num_nodos'], 300)
        self.assertEqual(config['pct_almacenamiento'], 15.0)
        self.assertEqual(config['pct_recarga'], 25.0)
        self.assertEqual(config['pct_cliente'], 60.0)
        self.assertEqual(config['prob_arista'], 0.2)
        self.assertEqual(config['clientes_por_nodo'], 10)
        self.assertEqual(config['ordenes_por_cliente'], 15)
        self.assertEqual(config['bateria_dron'], 3000.0)
        self.assertEqual(config['consumo_dron'], 1.5)
        self.assertEqual(config['capacidad_estacion'], 8)
        self.assertEqual(config['costo_recarga'], 5.0)
    
    def test_determinar_escenario_recomendado(self):
        """Verifica determinación de escenario recomendado"""
        # Pequeña ciudad
        escenario = self.validador._determinar_escenario_recomendado(30, 0.3)
        self.assertEqual(escenario, "pequena_ciudad")
        
        # Ciudad mediana
        escenario = self.validador._determinar_escenario_recomendado(100, 0.25)
        self.assertEqual(escenario, "ciudad_mediana")
        
        # Ciudad grande
        escenario = self.validador._determinar_escenario_recomendado(300, 0.2)
        self.assertEqual(escenario, "ciudad_grande")
        
        # Sin escenario específico
        escenario = self.validador._determinar_escenario_recomendado(5, 0.1)
        self.assertIsNone(escenario)


if __name__ == '__main__':
    unittest.main(verbosity=2) 
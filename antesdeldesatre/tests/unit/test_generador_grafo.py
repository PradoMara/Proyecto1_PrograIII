"""
Pruebas unitarias para el módulo generador_grafo.py

Estas pruebas cubren:
- RolNodo: Validación de roles y métodos estáticos
- ConfiguracionRoles: Validación de configuraciones y cálculos
- GeneradorGrafoConectado: Generación de grafos, validaciones y estadísticas
"""

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model.generador_grafo import RolNodo, ConfiguracionRoles, GeneradorGrafoConectado
from model.graph_base import Graph


class TestRolNodo(unittest.TestCase):
    """Pruebas para la clase RolNodo"""
    
    def test_roles_definidos(self):
        """Verifica que los roles estén correctamente definidos"""
        self.assertEqual(RolNodo.ALMACENAMIENTO, "almacenamiento")
        self.assertEqual(RolNodo.RECARGA, "recarga")
        self.assertEqual(RolNodo.CLIENTE, "cliente")
    
    def test_todos_los_roles(self):
        """Verifica que todos_los_roles devuelva todos los roles"""
        roles = RolNodo.todos_los_roles()
        expected_roles = ["almacenamiento", "recarga", "cliente"]
        
        self.assertEqual(len(roles), 3)
        for rol in expected_roles:
            self.assertIn(rol, roles)
    
    def test_roles_son_strings(self):
        """Verifica que todos los roles sean strings"""
        for rol in RolNodo.todos_los_roles():
            self.assertIsInstance(rol, str)
            self.assertTrue(len(rol) > 0)


class TestConfiguracionRoles(unittest.TestCase):
    """Pruebas para la clase ConfiguracionRoles"""
    
    def test_configuracion_por_defecto(self):
        """Verifica la configuración por defecto"""
        config = ConfiguracionRoles()
        
        self.assertEqual(config.almacenamiento, 0.2)
        self.assertEqual(config.recarga, 0.3)
        self.assertEqual(config.cliente, 0.5)
    
    def test_configuracion_personalizada_valida(self):
        """Verifica configuración personalizada válida"""
        config = ConfiguracionRoles(0.1, 0.4, 0.5)
        
        self.assertEqual(config.almacenamiento, 0.1)
        self.assertEqual(config.recarga, 0.4)
        self.assertEqual(config.cliente, 0.5)
    
    def test_configuracion_invalida_suma_incorrecta(self):
        """Verifica que se lance error si la suma no es 1.0"""
        with self.assertRaises(ValueError) as context:
            ConfiguracionRoles(0.2, 0.3, 0.4)  # Suma = 0.9
        
        self.assertIn("Los porcentajes deben sumar 1.0", str(context.exception))
    
    def test_configuracion_invalida_suma_mayor(self):
        """Verifica error cuando la suma es mayor a 1.0"""
        with self.assertRaises(ValueError):
            ConfiguracionRoles(0.4, 0.4, 0.4)  # Suma = 1.2
    
    def test_configuracion_con_tolerancia(self):
        """Verifica que se acepten pequeñas diferencias de precisión"""
        # Debería ser válido debido a la tolerancia de 0.001
        config = ConfiguracionRoles(0.333, 0.333, 0.334)  # Suma = 1.000
        self.assertIsInstance(config, ConfiguracionRoles)
    
    def test_calcular_cantidad_nodos_caso_basico(self):
        """Verifica el cálculo básico de cantidad de nodos"""
        config = ConfiguracionRoles(0.2, 0.3, 0.5)  # 20%, 30%, 50%
        resultado = config.calcular_cantidad_nodos(10)
        
        expected = {
            RolNodo.ALMACENAMIENTO: 2,  # 20% de 10 = 2
            RolNodo.RECARGA: 3,         # 30% de 10 = 3
            RolNodo.CLIENTE: 5          # 50% de 10 = 5
        }
        
        self.assertEqual(resultado, expected)
        self.assertEqual(sum(resultado.values()), 10)
    
    def test_calcular_cantidad_nodos_minimo_garantizado(self):
        """Verifica que siempre haya al menos 1 nodo de almacenamiento y recarga"""
        config = ConfiguracionRoles(0.01, 0.01, 0.98)  # 1%, 1%, 98%
        resultado = config.calcular_cantidad_nodos(5)
          # Debe garantizar al menos 1 nodo de cada tipo crítico
        self.assertGreaterEqual(resultado[RolNodo.ALMACENAMIENTO], 1)
        self.assertGreaterEqual(resultado[RolNodo.RECARGA], 1)
        self.assertGreaterEqual(resultado[RolNodo.CLIENTE], 0)
    
    def test_calcular_cantidad_nodos_caso_extremo(self):
        """Verifica el comportamiento con números pequeños"""
        config = ConfiguracionRoles(0.5, 0.3, 0.2)
        resultado = config.calcular_cantidad_nodos(2)
        
        # Con 2 nodos, debe garantizar al menos 1 almacenamiento y 1 recarga
        self.assertGreaterEqual(resultado[RolNodo.ALMACENAMIENTO], 1)
        self.assertGreaterEqual(resultado[RolNodo.RECARGA], 1)
        self.assertEqual(sum(resultado.values()), 2)
        
        # Caso especial: con 1 nodo, debe asignar solo a un rol
        resultado_uno = config.calcular_cantidad_nodos(1)
        self.assertEqual(sum(resultado_uno.values()), 1)
        # Debe asignar al rol con mayor porcentaje (almacenamiento: 0.5)
        self.assertEqual(resultado_uno[RolNodo.ALMACENAMIENTO], 1)
        self.assertEqual(resultado_uno[RolNodo.RECARGA], 0)
        self.assertEqual(resultado_uno[RolNodo.CLIENTE], 0)
    
    def test_calcular_cantidad_nodos_redondeo(self):
        """Verifica el comportamiento del redondeo"""
        config = ConfiguracionRoles(0.33, 0.33, 0.34)
        resultado = config.calcular_cantidad_nodos(9)
        
        # 33% de 9 ≈ 2.97 → 3
        # 33% de 9 ≈ 2.97 → 3  
        # Restante: 9 - 3 - 3 = 3
        expected_sum = 9
        self.assertEqual(sum(resultado.values()), expected_sum)


class TestGeneradorGrafoConectado(unittest.TestCase):
    """Pruebas para la clase GeneradorGrafoConectado"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.generador = GeneradorGrafoConectado()
    
    def test_inicializacion_por_defecto(self):
        """Verifica la inicialización por defecto"""
        generador = GeneradorGrafoConectado()
        
        self.assertIsInstance(generador.configuracion_roles, ConfiguracionRoles)
        self.assertIsNone(generador._semilla_aleatoria)
    
    def test_inicializacion_con_configuracion(self):
        """Verifica la inicialización con configuración personalizada"""
        config = ConfiguracionRoles(0.1, 0.2, 0.7)
        generador = GeneradorGrafoConectado(config)
        
        self.assertEqual(generador.configuracion_roles, config)
    
    def test_establecer_semilla(self):
        """Verifica el establecimiento de semilla aleatoria"""
        self.generador.establecer_semilla(42)
        self.assertEqual(self.generador._semilla_aleatoria, 42)
    
    def test_crear_grafo_conectado_basico(self):
        """Verifica la creación básica de un grafo conectado"""
        # Usar semilla para resultados reproducibles
        self.generador.establecer_semilla(123)
        
        grafo = self.generador.crear_grafo_conectado(5, 0.3)
        
        # Verificaciones básicas
        self.assertIsInstance(grafo, Graph)
        self.assertFalse(grafo.is_directed())
        
        vertices = list(grafo.vertices())
        self.assertEqual(len(vertices), 5)
        
        # Verificar que todos los vértices tienen los atributos requeridos
        for vertice in vertices:
            element = vertice.element()
            self.assertIn('id', element)
            self.assertIn('rol', element)
            self.assertIn('nombre', element)
            self.assertIn('propiedades', element)
    
    def test_crear_grafo_un_nodo(self):
        """Verifica la creación de grafo con un solo nodo"""
        grafo = self.generador.crear_grafo_conectado(1, 0.5)
        
        vertices = list(grafo.vertices())
        aristas = list(grafo.edges())
        
        self.assertEqual(len(vertices), 1)
        self.assertEqual(len(aristas), 0)  # Un nodo no puede tener aristas
    
    def test_crear_grafo_parametros_invalidos(self):
        """Verifica el manejo de parámetros inválidos"""
        # Número de nodos inválido
        with self.assertRaises(ValueError):
            self.generador.crear_grafo_conectado(0, 0.3)
        
        with self.assertRaises(ValueError):
            self.generador.crear_grafo_conectado(-1, 0.3)
        
        # Probabilidad inválida
        with self.assertRaises(ValueError):
            self.generador.crear_grafo_conectado(5, -0.1)
        
        with self.assertRaises(ValueError):
            self.generador.crear_grafo_conectado(5, 1.1)
    
    def test_crear_grafo_roles_distribuidos(self):
        """Verifica que los roles se distribuyan correctamente"""
        self.generador.establecer_semilla(456)
        grafo = self.generador.crear_grafo_conectado(10, 0.2)
        
        roles_encontrados = set()
        conteo_roles = {}
        
        for vertice in grafo.vertices():
            rol = vertice.element()['rol']
            roles_encontrados.add(rol)
            conteo_roles[rol] = conteo_roles.get(rol, 0) + 1
        
        # Debe haber al menos roles de almacenamiento y recarga
        expected_roles = {RolNodo.ALMACENAMIENTO, RolNodo.RECARGA}
        self.assertTrue(expected_roles.issubset(roles_encontrados))
        
        # Verificar que la suma sea correcta
        total_nodos = sum(conteo_roles.values())
        self.assertEqual(total_nodos, 10)
    
    def test_crear_grafo_con_roles_personalizados(self):
        """Verifica la creación con distribución personalizada de roles"""
        distribucion = {
            RolNodo.ALMACENAMIENTO: 2,
            RolNodo.RECARGA: 3,
            RolNodo.CLIENTE: 5
        }
        
        grafo = self.generador.crear_grafo_con_roles_personalizados(distribucion, 0.4)
        
        vertices = list(grafo.vertices())
        self.assertEqual(len(vertices), 10)
        
        # Contar roles reales
        conteo_real = {}
        for vertice in vertices:
            rol = vertice.element()['rol']
            conteo_real[rol] = conteo_real.get(rol, 0) + 1
        
        self.assertEqual(conteo_real[RolNodo.ALMACENAMIENTO], 2)
        self.assertEqual(conteo_real[RolNodo.RECARGA], 3)
        self.assertEqual(conteo_real[RolNodo.CLIENTE], 5)
    
    def test_crear_grafo_roles_personalizados_invalidos(self):
        """Verifica el manejo de distribuciones inválidas"""
        # Distribución vacía
        with self.assertRaises(ValueError):
            self.generador.crear_grafo_con_roles_personalizados({}, 0.3)
        
        # Distribución con valores negativos
        distribucion_invalida = {RolNodo.ALMACENAMIENTO: -1}
        with self.assertRaises(ValueError):
            self.generador.crear_grafo_con_roles_personalizados(distribucion_invalida, 0.3)
    
    def test_grafo_conectividad(self):
        """Verifica que el grafo generado esté conectado"""
        self.generador.establecer_semilla(789)
        
        # Probar con diferentes tamaños
        for num_nodos in [2, 5, 10, 20]:
            with self.subTest(num_nodos=num_nodos):
                grafo = self.generador.crear_grafo_conectado(num_nodos, 0.2)
                
                # Verificar conectividad usando el método del generador
                self.assertTrue(self.generador._verificar_conectividad(grafo))
    
    def test_obtener_estadisticas_grafo(self):
        """Verifica el cálculo de estadísticas del grafo"""
        self.generador.establecer_semilla(101)
        grafo = self.generador.crear_grafo_conectado(8, 0.3)
        
        stats = self.generador.obtener_estadisticas_grafo(grafo)
        
        # Verificar estructura de estadísticas
        expected_keys = {
            'numero_vertices', 'numero_aristas', 'densidad',
            'distribución_roles', 'esta_conectado', 'grado_promedio'
        }
        self.assertEqual(set(stats.keys()), expected_keys)
        
        # Verificar valores básicos
        self.assertEqual(stats['numero_vertices'], 8)
        self.assertTrue(stats['esta_conectado'])
        self.assertGreaterEqual(stats['numero_aristas'], 7)  # Al menos árbol de expansión
        self.assertIsInstance(stats['densidad'], float)
        self.assertGreaterEqual(stats['densidad'], 0.0)
        self.assertLessEqual(stats['densidad'], 1.0)
    
    def test_verificar_conectividad_casos_especiales(self):
        """Verifica la conectividad en casos especiales"""
        # Grafo con un nodo
        grafo_uno = Graph(directed=False)
        vertice = grafo_uno.insert_vertex({'id': 0})
        self.assertTrue(self.generador._verificar_conectividad(grafo_uno))
        
        # Grafo vacío
        grafo_vacio = Graph(directed=False)
        self.assertTrue(self.generador._verificar_conectividad(grafo_vacio))
    
    def test_propiedades_aristas(self):
        """Verifica las propiedades de las aristas generadas"""
        self.generador.establecer_semilla(202)
        grafo = self.generador.crear_grafo_conectado(6, 0.4)
        
        for arista in grafo.edges():
            element = arista.element()
            
            # Verificar estructura de datos de arista
            self.assertIn('peso', element)
            self.assertIn('tipo', element)
            self.assertIn('creado_en', element)
            
            # Verificar tipos de datos
            self.assertIsInstance(element['peso'], (int, float))
            self.assertIn(element['tipo'], ['expansion', 'adicional'])
            self.assertEqual(element['creado_en'], 'generacion')
            
            # Verificar rango de peso
            self.assertGreaterEqual(element['peso'], 1.0)
            self.assertLessEqual(element['peso'], 10.0)
    
    def test_reproducibilidad_con_semilla(self):
        """Verifica que los resultados sean reproducibles con la misma semilla"""
        semilla = 303
        
        # Generar dos grafos con la misma semilla
        gen1 = GeneradorGrafoConectado()
        gen1.establecer_semilla(semilla)
        grafo1 = gen1.crear_grafo_conectado(7, 0.3)
        
        gen2 = GeneradorGrafoConectado()
        gen2.establecer_semilla(semilla)
        grafo2 = gen2.crear_grafo_conectado(7, 0.3)
        
        # Comparar estadísticas
        stats1 = gen1.obtener_estadisticas_grafo(grafo1)
        stats2 = gen2.obtener_estadisticas_grafo(grafo2)
        
        self.assertEqual(stats1['numero_vertices'], stats2['numero_vertices'])
        self.assertEqual(stats1['numero_aristas'], stats2['numero_aristas'])
        self.assertEqual(stats1['distribución_roles'], stats2['distribución_roles'])
    
    def test_probabilidad_cero_aristas_adicionales(self):
        """Verifica que con probabilidad 0 solo se genere el árbol de expansión"""
        self.generador.establecer_semilla(404)
        grafo = self.generador.crear_grafo_conectado(8, 0.0)  # Probabilidad 0
        
        vertices = list(grafo.vertices())
        aristas = list(grafo.edges())
        
        # Con probabilidad 0, solo debe tener aristas del árbol de expansión
        # Para n vértices, el árbol de expansión tiene n-1 aristas
        expected_aristas = len(vertices) - 1
        self.assertEqual(len(aristas), expected_aristas)
        
        # Verificar que todas las aristas son de tipo 'expansion'
        for arista in aristas:
            self.assertEqual(arista.element()['tipo'], 'expansion')


if __name__ == '__main__':
    # Configurar el runner de pruebas para obtener información detallada
    unittest.main(verbosity=2)

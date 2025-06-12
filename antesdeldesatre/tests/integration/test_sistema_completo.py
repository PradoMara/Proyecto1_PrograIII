"""
Pruebas de integración para el sistema completo de generación y análisis de grafos

Estas pruebas verifican:
- Integración entre generador y utilidades
- Flujos completos de casos de uso reales
- Rendimiento y escalabilidad
- Consistencia entre componentes
"""

import unittest
import sys
import os
import time
from typing import List, Dict

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model.generador_grafo import GeneradorGrafoConectado, RolNodo, ConfiguracionRoles
from model.utilidades_grafo import ConsultorGrafo, CalculadorDistancias, BuscadorNodos
from model.graph_base import Graph


class TestIntegracionGeneradorUtilidades(unittest.TestCase):
    """Pruebas de integración entre generador y utilidades"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.generador = GeneradorGrafoConectado()
        self.generador.establecer_semilla(98765)
    
    def test_flujo_completo_generacion_y_analisis(self):
        """Verifica un flujo completo de generación y análisis"""
        # 1. Generar grafo
        grafo = self.generador.crear_grafo_conectado(20, 0.3)
        
        # 2. Validar conectividad
        self.assertTrue(ConsultorGrafo.validar_conectividad(grafo))
        
        # 3. Obtener estadísticas del generador
        stats_generador = self.generador.obtener_estadisticas_grafo(grafo)
        
        # 4. Obtener estadísticas de roles
        stats_roles = BuscadorNodos.obtener_estadisticas_roles(grafo)
        
        # 5. Verificar consistencia entre estadísticas
        self.assertEqual(
            stats_generador['numero_vertices'],
            sum(stats['cantidad'] for stats in stats_roles.values())
        )
        
        self.assertEqual(
            stats_generador['distribución_roles'],
            {rol: stats['cantidad'] for rol, stats in stats_roles.items()}
        )
    
    def test_busqueda_optima_servicios(self):
        """Simula la búsqueda óptima de servicios en una red"""
        # Crear una red más grande para pruebas realistas
        grafo = self.generador.crear_grafo_conectado(50, 0.2)
        
        # Buscar todos los nodos cliente
        clientes = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.CLIENTE)
        self.assertGreater(len(clientes), 0)
        
        # Para cada cliente, encontrar el servicio más cercano
        resultados_busqueda = []
        
        for cliente in clientes:
            # Buscar almacenamiento más cercano
            resultado_alm = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                grafo, cliente, RolNodo.ALMACENAMIENTO
            )
            
            # Buscar recarga más cercana
            resultado_rec = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                grafo, cliente, RolNodo.RECARGA
            )
            
            if resultado_alm and resultado_rec:
                resultados_busqueda.append({
                    'cliente': cliente,
                    'almacenamiento_cercano': resultado_alm,
                    'recarga_cercana': resultado_rec
                })
        
        # Verificar que se encontraron servicios para todos los clientes
        self.assertEqual(len(resultados_busqueda), len(clientes))
        
        # Verificar que todas las distancias son finitas
        for resultado in resultados_busqueda:
            _, dist_alm = resultado['almacenamiento_cercano']
            _, dist_rec = resultado['recarga_cercana']
            
            self.assertNotEqual(dist_alm, float('inf'))
            self.assertNotEqual(dist_rec, float('inf'))
            self.assertGreaterEqual(dist_alm, 0.0)
            self.assertGreaterEqual(dist_rec, 0.0)
    
    def test_analisis_rutas_multiples(self):
        """Verifica el análisis de múltiples rutas entre servicios"""
        grafo = self.generador.crear_grafo_conectado(30, 0.25)
        
        # Obtener nodos de diferentes roles
        almacenamientos = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.ALMACENAMIENTO)
        recargas = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.RECARGA)
        
        if len(almacenamientos) >= 2 and len(recargas) >= 2:
            # Analizar conectividad entre servicios críticos
            rutas_analizadas = []
            
            # Rutas entre almacenamientos
            for i, alm1 in enumerate(almacenamientos):
                for alm2 in almacenamientos[i+1:]:
                    resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, alm1, alm2)
                    if resultado:
                        camino, distancia = resultado
                        rutas_analizadas.append({
                            'tipo': 'almacenamiento-almacenamiento',
                            'origen': alm1,
                            'destino': alm2,
                            'camino': camino,
                            'distancia': distancia,
                            'saltos': len(camino) - 1
                        })
            
            # Rutas entre recargas
            for i, rec1 in enumerate(recargas):
                for rec2 in recargas[i+1:]:
                    resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, rec1, rec2)
                    if resultado:
                        camino, distancia = resultado
                        rutas_analizadas.append({
                            'tipo': 'recarga-recarga',
                            'origen': rec1,
                            'destino': rec2,
                            'camino': camino,
                            'distancia': distancia,
                            'saltos': len(camino) - 1
                        })
            
            # Verificar que se encontraron rutas
            self.assertGreater(len(rutas_analizadas), 0)
            
            # Analizar estadísticas de rutas
            distancias = [ruta['distancia'] for ruta in rutas_analizadas]
            saltos = [ruta['saltos'] for ruta in rutas_analizadas]
            
            # Verificar métricas básicas
            self.assertGreater(len(distancias), 0)
            self.assertTrue(all(d >= 0 for d in distancias))
            self.assertTrue(all(s >= 1 for s in saltos))
    
    def test_robustez_red_distribuida(self):
        """Verifica la robustez de una red distribuida simulando fallos"""
        # Crear red más densa para mayor robustez
        grafo = self.generador.crear_grafo_conectado(25, 0.4)
        
        # Verificar conectividad inicial
        self.assertTrue(ConsultorGrafo.validar_conectividad(grafo))
        
        # Obtener componentes conexas iniciales
        componentes_iniciales = ConsultorGrafo.obtener_componentes_conexas(grafo)
        self.assertEqual(len(componentes_iniciales), 1)
        
        # Simular "fallo" de nodos eliminando algunos vértices
        vertices = list(grafo.vertices())
        vertices_criticos = vertices[:3]  # Simular fallo de 3 nodos
        
        # Crear una copia conceptual removiendo aristas de nodos "fallidos"
        vertices_activos = [v for v in vertices if v not in vertices_criticos]
        
        # Verificar que aún hay suficientes servicios críticos
        almacenamientos_activos = [
            v for v in vertices_activos 
            if v.element()['rol'] == RolNodo.ALMACENAMIENTO
        ]
        recargas_activas = [
            v for v in vertices_activos 
            if v.element()['rol'] == RolNodo.RECARGA
        ]
        
        # Una red robusta debe mantener servicios críticos
        self.assertGreater(len(almacenamientos_activos), 0)
        self.assertGreater(len(recargas_activas), 0)
    
    def test_escalabilidad_busquedas(self):
        """Verifica la escalabilidad de las búsquedas en grafos grandes"""
        tamaños = [50, 100, 200]
        tiempos_busqueda = []
        
        for tamaño in tamaños:
            # Crear grafo del tamaño especificado
            grafo = self.generador.crear_grafo_conectado(tamaño, 0.15)
            
            # Medir tiempo de búsquedas
            inicio = time.time()
            
            # Realizar múltiples búsquedas
            vertices = list(grafo.vertices())
            origen = vertices[0]
            
            # Búsqueda de nodos por rol
            BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.ALMACENAMIENTO)
            
            # Búsqueda de nodo más cercano
            BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                grafo, origen, RolNodo.RECARGA
            )
            
            # Cálculo de distancias
            CalculadorDistancias.dijkstra(grafo, origen)
            
            fin = time.time()
            tiempo_total = fin - inicio
            tiempos_busqueda.append(tiempo_total)
        
        # Verificar que los tiempos son razonables
        for tiempo in tiempos_busqueda:
            self.assertLess(tiempo, 5.0)  # Máximo 5 segundos por prueba
        
        # Los tiempos no deben crecer exponencialmente
        # (aunque pueden crecer, no deben ser irrazonables)
        self.assertLess(max(tiempos_busqueda), min(tiempos_busqueda) * 100)


class TestCasosUsoReales(unittest.TestCase):
    """Pruebas que simulan casos de uso reales del sistema"""
    
    def setUp(self):
        """Configuración inicial para casos de uso"""
        self.generador = GeneradorGrafoConectado()
    
    def test_caso_uso_red_logistica(self):
        """Simula una red logística con centros de distribución"""
        # Configuración especializada para logística
        config_logistica = ConfiguracionRoles(
            almacenamiento=0.15,  # Pocos centros de distribución
            recarga=0.25,         # Puntos de servicio
            cliente=0.60          # Muchos puntos de entrega
        )
        
        self.generador.configuracion_roles = config_logistica
        self.generador.establecer_semilla(11111)
        
        # Crear red logística
        red_logistica = self.generador.crear_grafo_conectado(40, 0.2)
        
        # Analizar la red
        stats = self.generador.obtener_estadisticas_grafo(red_logistica)
        
        # Verificaciones específicas para logística
        self.assertTrue(stats['esta_conectado'])
        self.assertGreaterEqual(stats['distribución_roles'][RolNodo.ALMACENAMIENTO], 1)
        self.assertGreaterEqual(stats['distribución_roles'][RolNodo.RECARGA], 1)
        self.assertGreater(stats['distribución_roles'][RolNodo.CLIENTE], 
                          stats['distribución_roles'][RolNodo.ALMACENAMIENTO])
        
        # Simular planificación de rutas
        almacenamientos = BuscadorNodos.buscar_nodos_por_rol(red_logistica, RolNodo.ALMACENAMIENTO)
        clientes = BuscadorNodos.buscar_nodos_por_rol(red_logistica, RolNodo.CLIENTE)
        
        # Verificar que todos los clientes pueden alcanzar almacenes
        clientes_conectados = 0
        for cliente in clientes:
            resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                red_logistica, cliente, RolNodo.ALMACENAMIENTO
            )
            if resultado:
                clientes_conectados += 1
        
        # Todos los clientes deben poder alcanzar un almacén
        self.assertEqual(clientes_conectados, len(clientes))
    
    def test_caso_uso_red_iot(self):
        """Simula una red IoT con sensores y estaciones base"""
        # Configuración para IoT
        config_iot = ConfiguracionRoles(
            almacenamiento=0.10,  # Pocas estaciones base
            recarga=0.20,         # Repetidores/gateways
            cliente=0.70          # Muchos sensores
        )
        
        self.generador.configuracion_roles = config_iot
        self.generador.establecer_semilla(22222)
        
        # Crear red IoT
        red_iot = self.generador.crear_grafo_conectado(60, 0.15)
        
        # Verificar cobertura de red
        sensores = BuscadorNodos.buscar_nodos_por_rol(red_iot, RolNodo.CLIENTE)
        estaciones_base = BuscadorNodos.buscar_nodos_por_rol(red_iot, RolNodo.ALMACENAMIENTO)
        
        # Analizar latencia promedio desde sensores a estaciones base
        latencias = []
        for sensor in sensores[:10]:  # Muestra de sensores
            resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                red_iot, sensor, RolNodo.ALMACENAMIENTO
            )
            if resultado:
                _, distancia = resultado
                latencias.append(distancia)
        
        # Verificar métricas de red IoT
        if latencias:
            latencia_promedio = sum(latencias) / len(latencias)
            latencia_maxima = max(latencias)
            
            # Las latencias deben ser razonables para IoT
            self.assertLess(latencia_promedio, 20.0)  # Latencia promedio < 20
            self.assertLess(latencia_maxima, 50.0)    # Latencia máxima < 50
    
    def test_caso_uso_red_cdn(self):
        """Simula una red CDN (Content Delivery Network)"""
        # Configuración para CDN
        config_cdn = ConfiguracionRoles(
            almacenamiento=0.30,  # Servidores de origen
            recarga=0.40,         # Servidores edge/cache
            cliente=0.30          # Puntos de acceso
        )
        
        self.generador.configuracion_roles = config_cdn
        self.generador.establecer_semilla(33333)
        
        # Crear red CDN
        red_cdn = self.generador.crear_grafo_conectado(35, 0.35)
        
        # Analizar distribución de carga
        servidores_origen = BuscadorNodos.buscar_nodos_por_rol(red_cdn, RolNodo.ALMACENAMIENTO)
        servidores_edge = BuscadorNodos.buscar_nodos_por_rol(red_cdn, RolNodo.RECARGA)
        puntos_acceso = BuscadorNodos.buscar_nodos_por_rol(red_cdn, RolNodo.CLIENTE)
        
        # Verificar redundancia: múltiples servidores por tipo
        self.assertGreaterEqual(len(servidores_origen), 2)
        self.assertGreaterEqual(len(servidores_edge), 2)
        
        # Verificar que cada punto de acceso tiene múltiples opciones de edge
        for punto in puntos_acceso[:5]:  # Muestra de puntos de acceso
            opciones_edge = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
                red_cdn, punto, RolNodo.RECARGA, 3
            )
            
            # Debe haber al menos 2 opciones de edge cercanas
            self.assertGreaterEqual(len(opciones_edge), min(2, len(servidores_edge)))
    
    def test_optimizacion_configuracion_roles(self):
        """Verifica diferentes configuraciones de roles para optimización"""
        configuraciones = [
            ConfiguracionRoles(0.1, 0.2, 0.7),  # Pocos servicios, muchos clientes
            ConfiguracionRoles(0.2, 0.3, 0.5),  # Configuración balanceada
            ConfiguracionRoles(0.3, 0.4, 0.3),  # Muchos servicios, pocos clientes
        ]
        
        resultados_configuraciones = []
        
        for i, config in enumerate(configuraciones):
            self.generador.configuracion_roles = config
            self.generador.establecer_semilla(44444 + i)
            
            grafo = self.generador.crear_grafo_conectado(30, 0.25)
            stats = self.generador.obtener_estadisticas_grafo(grafo)
            
            # Calcular métricas de rendimiento
            clientes = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.CLIENTE)
            
            # Calcular distancia promedio a servicios
            distancias_servicio = []
            for cliente in clientes:
                for rol_servicio in [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA]:
                    resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                        grafo, cliente, rol_servicio
                    )
                    if resultado:
                        _, distancia = resultado
                        distancias_servicio.append(distancia)
            
            distancia_promedio = (
                sum(distancias_servicio) / len(distancias_servicio) 
                if distancias_servicio else float('inf')
            )
            
            resultados_configuraciones.append({
                'config': config,
                'stats': stats,
                'distancia_promedio_servicio': distancia_promedio
            })
        
        # Analizar resultados
        for resultado in resultados_configuraciones:
            # Todas las configuraciones deben producir grafos conectados
            self.assertTrue(resultado['stats']['esta_conectado'])
            
            # La distancia promedio debe ser finita
            self.assertNotEqual(resultado['distancia_promedio_servicio'], float('inf'))


class TestRendimientoYEscalabilidad(unittest.TestCase):
    """Pruebas de rendimiento y escalabilidad del sistema"""
    
    def test_rendimiento_generacion_grafos(self):
        """Verifica el rendimiento en la generación de grafos de diferentes tamaños"""
        generador = GeneradorGrafoConectado()
        generador.establecer_semilla(55555)
        
        tamaños_prueba = [10, 25, 50, 100]
        tiempos_generacion = {}
        
        for tamaño in tamaños_prueba:
            inicio = time.time()
            
            grafo = generador.crear_grafo_conectado(tamaño, 0.2)
            stats = generador.obtener_estadisticas_grafo(grafo)
            
            fin = time.time()
            tiempo_total = fin - inicio
            tiempos_generacion[tamaño] = tiempo_total
            
            # Verificaciones básicas
            self.assertEqual(stats['numero_vertices'], tamaño)
            self.assertTrue(stats['esta_conectado'])
        
        # Verificar que los tiempos son razonables
        for tamaño, tiempo in tiempos_generacion.items():
            self.assertLess(tiempo, 2.0, f"Generación de {tamaño} nodos tomó {tiempo:.2f}s")
    
    def test_escalabilidad_algoritmos_busqueda(self):
        """Verifica la escalabilidad de los algoritmos de búsqueda"""
        generador = GeneradorGrafoConectado()
        generador.establecer_semilla(66666)
        
        tamaños = [20, 40, 80]
        resultados = []
        
        for tamaño in tamaños:
            grafo = generador.crear_grafo_conectado(tamaño, 0.2)
            vertices = list(grafo.vertices())
            origen = vertices[0]
            
            # Medir tiempo de Dijkstra
            inicio = time.time()
            CalculadorDistancias.dijkstra(grafo, origen)
            tiempo_dijkstra = time.time() - inicio
            
            # Medir tiempo de búsqueda de roles
            inicio = time.time()
            BuscadorNodos.obtener_estadisticas_roles(grafo)
            tiempo_stats = time.time() - inicio
            
            resultados.append({
                'tamaño': tamaño,
                'tiempo_dijkstra': tiempo_dijkstra,
                'tiempo_stats': tiempo_stats
            })
        
        # Verificar que los tiempos crecen de manera razonable
        for resultado in resultados:
            self.assertLess(resultado['tiempo_dijkstra'], 1.0)
            self.assertLess(resultado['tiempo_stats'], 0.5)
    
    def test_consistencia_multiples_ejecuciones(self):
        """Verifica la consistencia en múltiples ejecuciones"""
        generador = GeneradorGrafoConectado()
        semilla_fija = 77777
        
        resultados_ejecuciones = []
        
        # Ejecutar múltiples veces con la misma semilla
        for _ in range(5):
            generador.establecer_semilla(semilla_fija)
            grafo = generador.crear_grafo_conectado(20, 0.3)
            stats = generador.obtener_estadisticas_grafo(grafo)
            
            resultados_ejecuciones.append(stats)
        
        # Verificar que todos los resultados son idénticos
        stats_referencia = resultados_ejecuciones[0]
        for stats in resultados_ejecuciones[1:]:
            self.assertEqual(stats['numero_vertices'], stats_referencia['numero_vertices'])
            self.assertEqual(stats['numero_aristas'], stats_referencia['numero_aristas'])
            self.assertEqual(stats['distribución_roles'], stats_referencia['distribución_roles'])
            self.assertEqual(stats['esta_conectado'], stats_referencia['esta_conectado'])


if __name__ == '__main__':
    # Configurar el runner de pruebas para obtener información detallada
    unittest.main(verbosity=2)

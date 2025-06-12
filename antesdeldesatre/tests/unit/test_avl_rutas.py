
import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from typing import List

# Importar las clases del módulo AVL
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tda.avl_rutas import AVLRutas
from domain.route import (
    RutaInfo, 
    NodoAVLRuta, 
    crear_ruta_desde_camino, 
    generar_id_ruta,
    filtrar_rutas_por_frecuencia,
    calcular_estadisticas_rutas
)


class TestRutaInfo(unittest.TestCase):
    """Pruebas para la clase RutaInfo"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.ruta_ejemplo = RutaInfo(
            ruta_id="test_r1",
            origen="A",
            destino="C",
            camino=["A", "B", "C"],
            distancia=15.5,
            frecuencia_uso=3,
            ultimo_uso=datetime(2024, 1, 1, 12, 0, 0),
            tiempo_promedio=2.5,
            metadatos={"tipo": "directa", "prioridad": "alta"}
        )
    
    def test_crear_ruta_info(self):
        """Prueba la creación correcta de RutaInfo"""
        self.assertEqual(self.ruta_ejemplo.ruta_id, "test_r1")
        self.assertEqual(self.ruta_ejemplo.origen, "A")
        self.assertEqual(self.ruta_ejemplo.destino, "C")
        self.assertEqual(self.ruta_ejemplo.camino, ["A", "B", "C"])
        self.assertEqual(self.ruta_ejemplo.distancia, 15.5)
        self.assertEqual(self.ruta_ejemplo.frecuencia_uso, 3)
        self.assertEqual(self.ruta_ejemplo.tiempo_promedio, 2.5)
        self.assertIn("tipo", self.ruta_ejemplo.metadatos)
    
    def test_to_dict(self):
        """Prueba la conversión a diccionario"""
        dict_ruta = self.ruta_ejemplo.to_dict()
        
        self.assertIsInstance(dict_ruta, dict)
        self.assertEqual(dict_ruta['ruta_id'], "test_r1")
        self.assertEqual(dict_ruta['origen'], "A")
        self.assertEqual(dict_ruta['destino'], "C")
        self.assertEqual(dict_ruta['camino'], ["A", "B", "C"])
        self.assertEqual(dict_ruta['distancia'], 15.5)
        self.assertEqual(dict_ruta['frecuencia_uso'], 3)
        self.assertIn('ultimo_uso', dict_ruta)
        self.assertEqual(dict_ruta['tiempo_promedio'], 2.5)
        self.assertEqual(dict_ruta['metadatos'], {"tipo": "directa", "prioridad": "alta"})
    
    def test_from_dict(self):
        """Prueba la creación desde diccionario"""
        dict_ruta = self.ruta_ejemplo.to_dict()
        ruta_restaurada = RutaInfo.from_dict(dict_ruta)
        
        self.assertEqual(ruta_restaurada.ruta_id, self.ruta_ejemplo.ruta_id)
        self.assertEqual(ruta_restaurada.origen, self.ruta_ejemplo.origen)
        self.assertEqual(ruta_restaurada.destino, self.ruta_ejemplo.destino)
        self.assertEqual(ruta_restaurada.camino, self.ruta_ejemplo.camino)
        self.assertEqual(ruta_restaurada.distancia, self.ruta_ejemplo.distancia)
        self.assertEqual(ruta_restaurada.frecuencia_uso, self.ruta_ejemplo.frecuencia_uso)
        self.assertEqual(ruta_restaurada.tiempo_promedio, self.ruta_ejemplo.tiempo_promedio)
        self.assertEqual(ruta_restaurada.metadatos, self.ruta_ejemplo.metadatos)


class TestNodoAVLRuta(unittest.TestCase):
    """Pruebas para la clase NodoAVLRuta"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.ruta_info = crear_ruta_desde_camino("test_nodo", ["X", "Y"], 10.0)
        self.nodo = NodoAVLRuta(self.ruta_info)
    
    def test_crear_nodo(self):
        """Prueba la creación correcta del nodo"""
        self.assertEqual(self.nodo.key, "test_nodo")
        self.assertEqual(self.nodo.ruta_info, self.ruta_info)
        self.assertIsNone(self.nodo.left)
        self.assertIsNone(self.nodo.right)
        self.assertEqual(self.nodo.height, 0)
    
    def test_str_representation(self):
        """Prueba la representación en string del nodo"""
        str_nodo = str(self.nodo)
        self.assertIn("test_nodo", str_nodo)
        self.assertIn("X→Y", str_nodo)
        self.assertIn("usos=0", str_nodo)


class TestAVLRutas(unittest.TestCase):
    """Pruebas principales para la clase AVLRutas"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.avl = AVLRutas()
        
        # Crear rutas de prueba
        self.rutas_prueba = [
            crear_ruta_desde_camino("r1", ["A", "B"], 5.0, {"tipo": "corta"}),
            crear_ruta_desde_camino("r2", ["B", "C"], 7.5, {"tipo": "media"}),
            crear_ruta_desde_camino("r3", ["A", "C"], 10.0, {"tipo": "directa"}),
            crear_ruta_desde_camino("r4", ["C", "D"], 3.2, {"tipo": "corta"}),
            crear_ruta_desde_camino("r5", ["A", "D", "E"], 15.8, {"tipo": "larga"}),
        ]
    
    def test_avl_vacio_inicial(self):
        """Prueba que el AVL inicia vacío"""
        self.assertTrue(self.avl.esta_vacio())
        self.assertEqual(self.avl.tamaño(), 0)
        self.assertEqual(self.avl.altura(), 0)
        self.assertIsNone(self.avl.buscar_ruta("cualquier_id"))
    
    def test_insertar_ruta_simple(self):
        """Prueba inserción de una sola ruta"""
        ruta = self.rutas_prueba[0]
        self.avl.insertar_ruta(ruta)
        
        self.assertFalse(self.avl.esta_vacio())
        self.assertEqual(self.avl.tamaño(), 1)
        self.assertEqual(self.avl.altura(), 1)
        
        ruta_encontrada = self.avl.buscar_ruta("r1")
        self.assertIsNotNone(ruta_encontrada)
        self.assertEqual(ruta_encontrada.ruta_id, "r1")
    
    def test_insertar_multiples_rutas(self):
        """Prueba inserción de múltiples rutas"""
        for ruta in self.rutas_prueba:
            self.avl.insertar_ruta(ruta)
        
        self.assertEqual(self.avl.tamaño(), len(self.rutas_prueba))
        
        # Verificar que todas las rutas se pueden encontrar
        for ruta in self.rutas_prueba:
            encontrada = self.avl.buscar_ruta(ruta.ruta_id)
            self.assertIsNotNone(encontrada)
            self.assertEqual(encontrada.ruta_id, ruta.ruta_id)
    
    def test_insertar_ruta_duplicada(self):
        """Prueba inserción de ruta con ID duplicado"""
        ruta_original = self.rutas_prueba[0]
        self.avl.insertar_ruta(ruta_original)
        
        # Insertar ruta con mismo ID pero diferente información
        ruta_actualizada = crear_ruta_desde_camino("r1", ["A", "X", "B"], 8.0)
        ruta_actualizada.frecuencia_uso = 5
        
        self.avl.insertar_ruta(ruta_actualizada)
        
        # Debe haber solo una ruta con el ID
        self.assertEqual(self.avl.tamaño(), 1)
        
        # La información debe estar actualizada
        ruta_encontrada = self.avl.buscar_ruta("r1")
        self.assertEqual(ruta_encontrada.distancia, 8.0)
        self.assertEqual(ruta_encontrada.camino, ["A", "X", "B"])
    
    def test_buscar_ruta_inexistente(self):
        """Prueba búsqueda de ruta que no existe"""
        for ruta in self.rutas_prueba[:3]:
            self.avl.insertar_ruta(ruta)
        
        self.assertIsNone(self.avl.buscar_ruta("ruta_inexistente"))
        self.assertIsNone(self.avl.buscar_ruta(""))
    
    def test_incrementar_uso_ruta(self):
        """Prueba incremento de uso de rutas"""
        ruta = self.rutas_prueba[0]
        self.avl.insertar_ruta(ruta)
        
        # Incrementar uso
        resultado = self.avl.incrementar_uso_ruta("r1", 3)
        self.assertTrue(resultado)
        
        # Verificar incremento
        ruta_actualizada = self.avl.buscar_ruta("r1")
        self.assertEqual(ruta_actualizada.frecuencia_uso, 3)
        
        # Incrementar nuevamente
        self.avl.incrementar_uso_ruta("r1", 2)
        ruta_actualizada = self.avl.buscar_ruta("r1")
        self.assertEqual(ruta_actualizada.frecuencia_uso, 5)
    
    def test_incrementar_uso_ruta_inexistente(self):
        """Prueba incremento de uso de ruta inexistente"""
        resultado = self.avl.incrementar_uso_ruta("ruta_inexistente", 1)
        self.assertFalse(resultado)
    
    def test_eliminar_ruta(self):
        """Prueba eliminación de rutas"""
        for ruta in self.rutas_prueba:
            self.avl.insertar_ruta(ruta)
        
        tamaño_inicial = self.avl.tamaño()
        
        # Eliminar ruta existente
        resultado = self.avl.eliminar_ruta("r3")
        self.assertTrue(resultado)
        self.assertEqual(self.avl.tamaño(), tamaño_inicial - 1)
        self.assertIsNone(self.avl.buscar_ruta("r3"))
        
        # Eliminar ruta inexistente
        resultado = self.avl.eliminar_ruta("ruta_inexistente")
        self.assertFalse(resultado)
    
    def test_balanceo_avl(self):
        """Prueba que el árbol se mantenga balanceado"""
        # Insertar rutas que podrían desbalancear el árbol
        rutas_desbalanceantes = []
        for i in range(10):
            ruta = crear_ruta_desde_camino(f"r{i:02d}", ["A", "B"], float(i))
            rutas_desbalanceantes.append(ruta)
        
        for ruta in rutas_desbalanceantes:
            self.avl.insertar_ruta(ruta)
        
        # Verificar que el árbol esté balanceado
        self.assertTrue(self.avl.es_balanceado())
        
        # La altura debe ser logarítmica respecto al número de nodos
        altura_esperada_max = int(1.44 * len(rutas_desbalanceantes)) + 2  # Factor AVL
        self.assertLessEqual(self.avl.altura(), altura_esperada_max)
    
    def test_obtener_rutas_por_frecuencia(self):
        """Prueba obtención de rutas ordenadas por frecuencia"""
        # Insertar rutas y establecer diferentes frecuencias
        for i, ruta in enumerate(self.rutas_prueba):
            self.avl.insertar_ruta(ruta)
            self.avl.incrementar_uso_ruta(ruta.ruta_id, i + 1)
        
        # Obtener rutas más usadas
        rutas_desc = self.avl.obtener_rutas_por_frecuencia()
        self.assertEqual(len(rutas_desc), len(self.rutas_prueba))
        
        # Verificar orden descendente
        for i in range(len(rutas_desc) - 1):
            self.assertGreaterEqual(rutas_desc[i].frecuencia_uso, 
                                  rutas_desc[i + 1].frecuencia_uso)
        
        # Obtener rutas menos usadas
        rutas_asc = self.avl.obtener_rutas_por_frecuencia(orden_desc=False)
        for i in range(len(rutas_asc) - 1):
            self.assertLessEqual(rutas_asc[i].frecuencia_uso, 
                               rutas_asc[i + 1].frecuencia_uso)
        
        # Obtener con límite
        rutas_limitadas = self.avl.obtener_rutas_por_frecuencia(limite=3)
        self.assertEqual(len(rutas_limitadas), 3)
    
    def test_buscar_rutas_por_origen_destino(self):
        """Prueba búsqueda por origen y destino"""
        # Agregar rutas con algunos pares origen-destino duplicados
        rutas_adicionales = [
            crear_ruta_desde_camino("r6", ["A", "C"], 12.0, {"tipo": "alternativa"}),
            crear_ruta_desde_camino("r7", ["A", "B", "C"], 9.0, {"tipo": "indirecta"}),
        ]
        
        for ruta in self.rutas_prueba + rutas_adicionales:
            self.avl.insertar_ruta(ruta)
        
        # Buscar rutas de A a C
        rutas_a_c = self.avl.buscar_rutas_por_origen_destino("A", "C")
        self.assertEqual(len(rutas_a_c), 3)  # r3, r6, r7
        
        for ruta in rutas_a_c:
            self.assertEqual(ruta.origen, "A")
            self.assertEqual(ruta.destino, "C")
        
        # Buscar rutas inexistentes
        rutas_inexistentes = self.avl.buscar_rutas_por_origen_destino("X", "Y")
        self.assertEqual(len(rutas_inexistentes), 0)
    
    def test_obtener_estadisticas_uso(self):
        """Prueba obtención de estadísticas de uso"""
        # Estadísticas de árbol vacío
        stats_vacias = self.avl.obtener_estadisticas_uso()
        self.assertEqual(stats_vacias['total_rutas'], 0)
        self.assertEqual(stats_vacias['total_usos'], 0)
        self.assertEqual(stats_vacias['uso_promedio'], 0.0)
        
        # Insertar rutas y establecer usos
        for i, ruta in enumerate(self.rutas_prueba):
            self.avl.insertar_ruta(ruta)
            self.avl.incrementar_uso_ruta(ruta.ruta_id, (i + 1) * 2)
        
        stats = self.avl.obtener_estadisticas_uso()
        
        self.assertEqual(stats['total_rutas'], len(self.rutas_prueba))
        self.assertEqual(stats['total_usos'], 2 + 4 + 6 + 8 + 10)  # 30
        self.assertEqual(stats['uso_promedio'], 6.0)
        self.assertIsNotNone(stats['ruta_mas_usada'])
        self.assertIsNotNone(stats['ruta_menos_usada'])
        self.assertEqual(stats['ruta_mas_usada'].frecuencia_uso, 10)
        self.assertEqual(stats['ruta_menos_usada'].frecuencia_uso, 2)
        self.assertGreater(stats['altura_arbol'], 0)
    
    def test_listar_todas_rutas(self):
        """Prueba listado de todas las rutas"""
        for ruta in self.rutas_prueba:
            self.avl.insertar_ruta(ruta)
        
        todas_rutas = self.avl.listar_todas_rutas()
        self.assertEqual(len(todas_rutas), len(self.rutas_prueba))
        
        # Verificar que todas las rutas estén presentes
        ids_encontrados = {ruta.ruta_id for ruta in todas_rutas}
        ids_esperados = {ruta.ruta_id for ruta in self.rutas_prueba}
        self.assertEqual(ids_encontrados, ids_esperados)


class TestSerializacionJSON(unittest.TestCase):
    """Pruebas para serialización e importación JSON"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.avl = AVLRutas()
        self.rutas_prueba = [
            crear_ruta_desde_camino("json_r1", ["A", "B"], 5.0),
            crear_ruta_desde_camino("json_r2", ["B", "C"], 7.0),
            crear_ruta_desde_camino("json_r3", ["C", "D"], 3.0),
        ]
        
        for i, ruta in enumerate(self.rutas_prueba):
            self.avl.insertar_ruta(ruta)
            self.avl.incrementar_uso_ruta(ruta.ruta_id, i + 1)
    
    def test_exportar_importar_json(self):
        """Prueba exportación e importación completa"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            archivo_temp = tmp_file.name
        
        try:
            # Exportar
            self.avl.exportar_a_json(archivo_temp)
            self.assertTrue(os.path.exists(archivo_temp))
            
            # Verificar contenido del archivo
            with open(archivo_temp, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            self.assertIn('rutas', datos)
            self.assertIn('estadisticas', datos)
            self.assertIn('exportado_en', datos)
            self.assertEqual(len(datos['rutas']), len(self.rutas_prueba))
            
            # Crear nuevo AVL e importar
            avl_nuevo = AVLRutas()
            rutas_importadas = avl_nuevo.importar_desde_json(archivo_temp)
            
            self.assertEqual(rutas_importadas, len(self.rutas_prueba))
            self.assertEqual(avl_nuevo.tamaño(), self.avl.tamaño())
            
            # Verificar que las rutas son idénticas
            for ruta_original in self.rutas_prueba:
                ruta_importada = avl_nuevo.buscar_ruta(ruta_original.ruta_id)
                self.assertIsNotNone(ruta_importada)
                self.assertEqual(ruta_importada.ruta_id, ruta_original.ruta_id)
                self.assertEqual(ruta_importada.origen, ruta_original.origen)
                self.assertEqual(ruta_importada.destino, ruta_original.destino)
        
        finally:
            # Limpiar archivo temporal
            if os.path.exists(archivo_temp):
                os.unlink(archivo_temp)


class TestFuncionesUtilidad(unittest.TestCase):
    """Pruebas para funciones de utilidad"""
    
    def test_crear_ruta_desde_camino(self):
        """Prueba creación de ruta desde camino"""
        camino = ["A", "B", "C", "D"]
        distancia = 25.5
        metadatos = {"tipo": "test", "nivel": 1}
        
        ruta = crear_ruta_desde_camino("test_id", camino, distancia, metadatos)
        
        self.assertEqual(ruta.ruta_id, "test_id")
        self.assertEqual(ruta.origen, "A")
        self.assertEqual(ruta.destino, "D")
        self.assertEqual(ruta.camino, camino)
        self.assertEqual(ruta.distancia, distancia)
        self.assertEqual(ruta.frecuencia_uso, 0)
        self.assertEqual(ruta.tiempo_promedio, 0.0)
        self.assertEqual(ruta.metadatos, metadatos)
        self.assertIsInstance(ruta.ultimo_uso, datetime)
    
    def test_crear_ruta_camino_invalido(self):
        """Prueba creación con camino inválido"""
        with self.assertRaises(ValueError):
            crear_ruta_desde_camino("test", ["A"], 10.0)  # Solo un nodo
        
        with self.assertRaises(ValueError):
            crear_ruta_desde_camino("test", [], 10.0)  # Camino vacío
    
    def test_generar_id_ruta(self):
        """Prueba generación de IDs de rutas"""
        # ID simple
        id_simple = generar_id_ruta("A", "B")
        self.assertEqual(id_simple, "ruta_A_B")
        
        # ID con índice
        id_con_indice = generar_id_ruta("A", "B", 2)
        self.assertEqual(id_con_indice, "ruta_A_B_2")
        
        # ID con índice 0 (debe ser igual al simple)
        id_cero = generar_id_ruta("X", "Y", 0)
        self.assertEqual(id_cero, "ruta_X_Y")


class TestCasosEspeciales(unittest.TestCase):
    """Pruebas para casos especiales y límite"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.avl = AVLRutas()
    
    def test_operaciones_arbol_vacio(self):
        """Prueba operaciones en árbol vacío"""
        self.assertTrue(self.avl.esta_vacio())
        self.assertTrue(self.avl.es_balanceado())
        self.assertEqual(self.avl.listar_todas_rutas(), [])
        self.assertEqual(self.avl.obtener_rutas_por_frecuencia(), [])
        self.assertEqual(self.avl.buscar_rutas_por_origen_destino("A", "B"), [])
        
        # Imprimir árbol vacío no debe causar error
        self.avl.imprimir_arbol()  # Solo verificamos que no lance excepción
    
    def test_insercion_masiva_secuencial(self):
        """Prueba inserción masiva de rutas secuenciales"""
        num_rutas = 100
        
        for i in range(num_rutas):
            ruta = crear_ruta_desde_camino(f"r{i:03d}", ["A", "B"], float(i))
            self.avl.insertar_ruta(ruta)
        
        self.assertEqual(self.avl.tamaño(), num_rutas)
        self.assertTrue(self.avl.es_balanceado())
        
        # Verificar que todas las rutas se pueden encontrar
        for i in range(0, num_rutas, 10):  # Verificar cada 10 rutas
            ruta_id = f"r{i:03d}"
            self.assertIsNotNone(self.avl.buscar_ruta(ruta_id))
    
    def test_eliminacion_todas_rutas(self):
        """Prueba eliminación de todas las rutas"""
        rutas = []
        for i in range(10):
            ruta = crear_ruta_desde_camino(f"r{i}", ["A", "B"], float(i))
            rutas.append(ruta)
            self.avl.insertar_ruta(ruta)
        
        # Eliminar todas las rutas
        for ruta in rutas:
            resultado = self.avl.eliminar_ruta(ruta.ruta_id)
            self.assertTrue(resultado)
        
        # Verificar que el árbol quedó vacío
        self.assertTrue(self.avl.esta_vacio())
        self.assertEqual(self.avl.tamaño(), 0)
        self.assertTrue(self.avl.es_balanceado())
    
    def test_frecuencias_extremas(self):
        """Prueba con frecuencias de uso extremas"""
        # Ruta con frecuencia muy alta
        ruta_alta = crear_ruta_desde_camino("alta", ["A", "B"], 10.0)
        self.avl.insertar_ruta(ruta_alta)
        self.avl.incrementar_uso_ruta("alta", 1000000)
        
        # Ruta sin uso
        ruta_sin_uso = crear_ruta_desde_camino("sin_uso", ["C", "D"], 5.0)
        self.avl.insertar_ruta(ruta_sin_uso)
        
        rutas_ordenadas = self.avl.obtener_rutas_por_frecuencia()
        self.assertEqual(rutas_ordenadas[0].frecuencia_uso, 1000000)
        self.assertEqual(rutas_ordenadas[1].frecuencia_uso, 0)
        
        stats = self.avl.obtener_estadisticas_uso()
        self.assertEqual(stats['rutas_nunca_usadas'], 1)


if __name__ == '__main__':
    # Configurar el runner de pruebas
    unittest.main(verbosity=2, buffer=True)

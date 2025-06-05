# Guía de Pruebas - Sistema de Generación de Grafos

## Introducción

Este documento explica cómo ejecutar, interpretar y extender las pruebas del sistema de generación de grafos. Las pruebas están organizadas en dos categorías principales: **unitarias** e **integración**.

## Estructura de Pruebas

```
tests/
├── __init__.py
├── run_tests.py              # Script principal de ejecución
├── unit/                     # Pruebas unitarias
│   ├── __init__.py
│   ├── test_generador_grafo.py
│   └── test_utilidades_grafo.py
└── integration/              # Pruebas de integración
    ├── __init__.py
    └── test_sistema_completo.py
```

## Ejecutar Pruebas

### Opción 1: Script Automatizado (Recomendado)

```powershell
# Ejecutar todas las pruebas
python tests\run_tests.py

# Solo pruebas unitarias
python tests\run_tests.py --unit

# Solo pruebas de integración  
python tests\run_tests.py --integration

# Con salida detallada
python tests\run_tests.py --verbose

# Ver ayuda
python tests\run_tests.py --help
```

### Opción 2: Unittest Directo

```powershell
# Desde el directorio raíz del proyecto

# Todas las pruebas
python -m unittest discover tests -v

# Solo unitarias
python -m unittest discover tests/unit -v

# Solo integración
python -m unittest discover tests/integration -v

# Prueba específica
python -m unittest tests.unit.test_generador_grafo.TestRolNodo -v
```

### Opción 3: Ejecución Individual

```powershell
# Ejecutar archivo específico
python tests\unit\test_generador_grafo.py
python tests\unit\test_utilidades_grafo.py
python tests\integration\test_sistema_completo.py
```

## Pruebas Unitarias

### test_generador_grafo.py

Cubre las siguientes clases y funcionalidades:

#### TestRolNodo
- ✅ Verificación de roles definidos
- ✅ Método `todos_los_roles()`
- ✅ Validación de tipos de datos

```python
# Ejemplo de ejecución
python -m unittest tests.unit.test_generador_grafo.TestRolNodo.test_roles_definidos -v
```

#### TestConfiguracionRoles
- ✅ Configuración por defecto
- ✅ Configuraciones personalizadas
- ✅ Validación de suma de porcentajes
- ✅ Cálculo de cantidad de nodos
- ✅ Garantía de mínimos (almacenamiento y recarga)

```python
# Verificar configuraciones
python -m unittest tests.unit.test_generador_grafo.TestConfiguracionRoles -v
```

#### TestGeneradorGrafoConectado
- ✅ Inicialización y configuración
- ✅ Establecimiento de semillas aleatorias
- ✅ Generación de grafos básicos y personalizados
- ✅ Validación de parámetros
- ✅ Distribución de roles
- ✅ Conectividad garantizada
- ✅ Estadísticas del grafo
- ✅ Propiedades de aristas
- ✅ Reproducibilidad

### test_utilidades_grafo.py

Cubre las siguientes clases:

#### TestConsultorGrafo
- ✅ Búsquedas por nombre, ID y atributos
- ✅ Navegación (vecinos, grados, aristas)
- ✅ Validación de conectividad
- ✅ Análisis de componentes conexas

#### TestCalculadorDistancias
- ✅ Algoritmo Dijkstra
- ✅ Reconstrucción de caminos
- ✅ Cálculo de distancias
- ✅ Manejo de grafos desconectados
- ✅ Aristas sin peso explícito

#### TestBuscadorNodos
- ✅ Búsquedas por rol
- ✅ Nodo más cercano por rol
- ✅ K nodos más cercanos
- ✅ Estadísticas por roles
- ✅ Casos especiales (roles inexistentes, mismo rol)

## Pruebas de Integración

### test_sistema_completo.py

#### TestIntegracionGeneradorUtilidades
- ✅ Flujo completo de generación y análisis
- ✅ Búsqueda óptima de servicios
- ✅ Análisis de rutas múltiples
- ✅ Robustez ante fallos simulados
- ✅ Escalabilidad de búsquedas

#### TestCasosUsoReales
- ✅ Simulación de red logística
- ✅ Simulación de red IoT
- ✅ Simulación de red CDN
- ✅ Optimización de configuraciones

#### TestRendimientoYEscalabilidad
- ✅ Rendimiento en generación
- ✅ Escalabilidad de algoritmos
- ✅ Consistencia en múltiples ejecuciones

## Interpretación de Resultados

### Salida Exitosa

```
======================================================================
REPORTE DE RESULTADOS
======================================================================
⏱️  Tiempo total: 2.45 segundos
🧪 Pruebas ejecutadas: 75
✅ Pruebas exitosas: 75
❌ Pruebas fallidas: 0
💥 Errores: 0
🚫 Omitidas: 0
📊 Porcentaje de éxito: 100.0%

======================================================================
🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE
======================================================================
```

### Identificar Problemas

#### Fallo de Aserción
```
❌ test_configuracion_invalida_suma_incorrecta
   Expected ValueError but none was raised
```

**Solución**: Verificar que las validaciones estén implementadas correctamente.

#### Error de Importación
```
💥 test_crear_grafo_conectado_basico
   ModuleNotFoundError: No module named 'model'
```

**Solución**: Ejecutar desde el directorio raíz del proyecto.

#### Error de Timeout/Rendimiento
```
❌ test_escalabilidad_busquedas
   AssertionError: 6.2 not less than 5.0
```

**Solución**: Optimizar algoritmos o ajustar límites de tiempo.

## Cobertura de Pruebas

### Módulos Cubiertos

| Módulo | Cobertura | Pruebas |
|--------|-----------|---------|
| `generador_grafo.py` | 95%+ | 25 pruebas |
| `utilidades_grafo.py` | 90%+ | 35 pruebas |
| Integración | 100% | 15 pruebas |

### Funcionalidades Principales

- ✅ **Generación de Grafos**: 100%
- ✅ **Algoritmos de Búsqueda**: 95%
- ✅ **Cálculo de Distancias**: 100%
- ✅ **Análisis de Conectividad**: 100%
- ✅ **Estadísticas y Métricas**: 90%
- ✅ **Casos de Uso Reales**: 100%

## Agregar Nuevas Pruebas

### Estructura de Prueba Unitaria

```python
import unittest
from model.tu_modulo import TuClase

class TestTuClase(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.objeto = TuClase()
    
    def test_funcionalidad_basica(self):
        """Descripción de la prueba"""
        # Arrange (Preparar)
        entrada = "valor_prueba"
        
        # Act (Actuar)
        resultado = self.objeto.tu_metodo(entrada)
        
        # Assert (Verificar)
        self.assertEqual(resultado, valor_esperado)
    
    def test_caso_extremo(self):
        """Prueba de caso extremo"""
        with self.assertRaises(ValueError):
            self.objeto.metodo_que_debe_fallar(entrada_invalida)
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### Estructura de Prueba de Integración

```python
class TestIntegracionCompleta(unittest.TestCase):
    
    def setUp(self):
        """Configuración para integración"""
        self.sistema = SistemaCompleto()
    
    def test_flujo_completo_caso_uso(self):
        """Prueba de flujo completo"""
        # 1. Preparar datos
        configuracion = ConfiguracionEspecifica()
        
        # 2. Ejecutar flujo
        resultado = self.sistema.ejecutar_flujo_completo(configuracion)
        
        # 3. Verificar resultados
        self.assertIsNotNone(resultado)
        self.assertTrue(resultado.es_valido())
        
        # 4. Verificar efectos secundarios
        self.assertEqual(self.sistema.estado, EstadoEsperado.COMPLETO)
```

## Pruebas de Rendimiento

### Medición de Tiempo

```python
import time

def test_rendimiento_algoritmo(self):
    """Prueba de rendimiento"""
    # Configurar datos de prueba
    grafo_grande = self.generar_grafo_grande(1000)
    
    # Medir tiempo
    inicio = time.time()
    resultado = algoritmo_bajo_prueba(grafo_grande)
    tiempo_total = time.time() - inicio
    
    # Verificar rendimiento
    self.assertLess(tiempo_total, 2.0)  # Máximo 2 segundos
    self.assertIsNotNone(resultado)
```

### Pruebas de Escalabilidad

```python
def test_escalabilidad_lineal(self):
    """Verifica escalabilidad aproximadamente lineal"""
    tamaños = [100, 200, 400]
    tiempos = []
    
    for tamaño in tamaños:
        grafo = self.generar_grafo(tamaño)
        inicio = time.time()
        procesar_grafo(grafo)
        tiempos.append(time.time() - inicio)
    
    # Verificar que el crecimiento no sea exponencial
    ratio_crecimiento = tiempos[-1] / tiempos[0]
    ratio_tamaño = tamaños[-1] / tamaños[0]
    
    self.assertLess(ratio_crecimiento, ratio_tamaño * 2)
```

## Mejores Prácticas

### 1. Nombrado de Pruebas

```python
# ✅ Bueno: Descriptivo y claro
def test_crear_grafo_conectado_con_10_nodos_debe_generar_grafo_valido(self):

# ❌ Malo: Muy genérico
def test_grafo(self):
```

### 2. Organización de Pruebas

- **Una clase** por clase bajo prueba
- **Un método** por funcionalidad específica
- **Casos separados** para diferentes escenarios

### 3. Datos de Prueba

```python
def setUp(self):
    """Usar datos consistentes"""
    self.generador = GeneradorGrafoConectado()
    self.generador.establecer_semilla(12345)  # Reproducible
    
    self.config_test = ConfiguracionRoles(0.2, 0.3, 0.5)
    self.grafo_pequeño = self.generador.crear_grafo_conectado(10, 0.3)
```

### 4. Verificaciones Completas

```python
def test_resultado_completo(self):
    resultado = operacion_bajo_prueba()
    
    # Verificar tipo
    self.assertIsInstance(resultado, TipoEsperado)
    
    # Verificar contenido
    self.assertGreater(len(resultado), 0)
    
    # Verificar propiedades específicas
    self.assertTrue(resultado.es_valido())
    
    # Verificar invariantes
    self.assertEqual(resultado.suma_total(), valor_esperado)
```

## Depuración de Pruebas

### Usar Debugger

```python
import pdb

def test_con_debug(self):
    resultado = operacion_compleja()
    pdb.set_trace()  # Pausar ejecución aquí
    self.assertEqual(resultado, valor_esperado)
```

### Salida de Depuración

```python
def test_con_prints(self):
    print(f"Estado inicial: {self.objeto.estado}")
    resultado = self.objeto.operacion()
    print(f"Resultado: {resultado}")
    print(f"Estado final: {self.objeto.estado}")
    
    self.assertEqual(resultado, valor_esperado)
```

### Configuración de Logging

```python
import logging

def setUp(self):
    logging.basicConfig(level=logging.DEBUG)
    self.logger = logging.getLogger(__name__)

def test_con_logging(self):
    self.logger.debug("Iniciando prueba")
    resultado = operacion_bajo_prueba()
    self.logger.info(f"Resultado obtenido: {resultado}")
```

## Automatización

### Integración Continua

Para integrar con sistemas de CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Ejecutar Pruebas
  run: |
    python tests/run_tests.py
    
- name: Verificar Cobertura
  run: |
    python -m coverage run tests/run_tests.py
    python -m coverage report --fail-under=90
```

### Scripts de Pre-commit

```bash
#!/bin/bash
# pre-commit-hook.sh
echo "Ejecutando pruebas antes del commit..."
python tests/run_tests.py --unit

if [ $? -eq 0 ]; then
    echo "✅ Todas las pruebas pasaron"
    exit 0
else
    echo "❌ Pruebas fallaron - commit bloqueado"
    exit 1
fi
```

Las pruebas están diseñadas para ser completas, rápidas y confiables. ¡Mantén la cobertura alta y agrega pruebas para nuevas funcionalidades!

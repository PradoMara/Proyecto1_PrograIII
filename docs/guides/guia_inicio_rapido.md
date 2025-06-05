# Guía de Inicio Rápido - Sistema de Generación de Grafos

## Introducción

Este sistema permite generar grafos conectados con roles específicos y realizar análisis avanzados sobre ellos. Es ideal para simular redes de distribución, sistemas IoT, CDN, y otros casos de uso que requieren análisis de conectividad.

## Instalación y Configuración

### Requisitos del Sistema

- Python 3.7+
- No requiere dependencias externas adicionales

### Estructura del Proyecto

```
Proyecto1_PrograIII/
├── model/                    # Módulos principales
│   ├── generador_grafo.py   # Generación de grafos
│   ├── utilidades_grafo.py  # Análisis y búsquedas
│   ├── graph_base.py        # Estructura base del grafo
│   ├── vertex_base.py       # Vértices
│   └── edge_base.py         # Aristas
├── docs/                    # Documentación
├── tests/                   # Pruebas unitarias e integración
└── examples/               # Ejemplos prácticos
```

## Primer Uso

### 1. Importar los Módulos

```python
from model.generador_grafo import GeneradorGrafoConectado, RolNodo, ConfiguracionRoles
from model.utilidades_grafo import ConsultorGrafo, CalculadorDistancias, BuscadorNodos
```

### 2. Crear tu Primer Grafo

```python
# Crear un generador con configuración por defecto
generador = GeneradorGrafoConectado()

# Generar un grafo conectado con 10 nodos
grafo = generador.crear_grafo_conectado(numero_nodos=10, probabilidad_arista=0.3)

# Ver estadísticas básicas
stats = generador.obtener_estadisticas_grafo(grafo)
print(f"Nodos: {stats['numero_vertices']}")
print(f"Aristas: {stats['numero_aristas']}")
print(f"Conectado: {stats['esta_conectado']}")
```

### 3. Explorar el Grafo

```python
# Buscar nodos por tipo
nodos_almacenamiento = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.ALMACENAMIENTO)
print(f"Nodos de almacenamiento encontrados: {len(nodos_almacenamiento)}")

# Encontrar el nodo más cercano a un servicio
if nodos_almacenamiento:
    primer_nodo = list(grafo.vertices())[0]
    resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
        grafo, primer_nodo, RolNodo.ALMACENAMIENTO
    )
    
    if resultado:
        nodo_cercano, distancia = resultado
        print(f"Nodo más cercano está a distancia: {distancia}")
```

## Conceptos Clave

### Roles de Nodos

El sistema utiliza tres tipos de roles:

- **Almacenamiento**: Nodos que almacenan datos/recursos
- **Recarga**: Nodos que proporcionan servicios de recarga/mantenimiento  
- **Cliente**: Nodos que consumen servicios

### Configuración de Roles

```python
# Configuración personalizada (porcentajes deben sumar 1.0)
config = ConfiguracionRoles(
    almacenamiento=0.2,  # 20% nodos de almacenamiento
    recarga=0.3,         # 30% nodos de recarga
    cliente=0.5          # 50% nodos cliente
)

generador = GeneradorGrafoConectado(config)
```

### Propiedades de Aristas

Cada arista contiene:
- **peso**: Costo/distancia (1.0 - 10.0)
- **tipo**: 'expansion' (árbol) o 'adicional'
- **creado_en**: 'generacion'

## Casos de Uso Típicos

### Caso 1: Red de Distribución Logística

```python
# Configuración para logística (pocos almacenes, muchos clientes)
config_logistica = ConfiguracionRoles(0.15, 0.25, 0.60)
generador = GeneradorGrafoConectado(config_logistica)

# Crear red más densa para mejor conectividad
red = generador.crear_grafo_conectado(50, 0.25)

# Analizar cobertura
clientes = BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.CLIENTE)
print(f"Red tiene {len(clientes)} puntos de entrega")
```

### Caso 2: Red IoT

```python
# Configuración para IoT (muchos sensores, pocas estaciones base)
config_iot = ConfiguracionRoles(0.10, 0.20, 0.70)
generador = GeneradorGrafoConectado(config_iot)

# Red menos densa para simular limitaciones de radio
red_iot = generador.crear_grafo_conectado(100, 0.15)

# Analizar latencia
sensores = BuscadorNodos.buscar_nodos_por_rol(red_iot, RolNodo.CLIENTE)
for sensor in sensores[:5]:  # Muestra de 5 sensores
    resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
        red_iot, sensor, RolNodo.ALMACENAMIENTO
    )
    if resultado:
        _, latencia = resultado
        print(f"Sensor {sensor.element()['id']}: latencia {latencia:.2f}")
```

### Caso 3: Análisis de Rutas

```python
# Crear red
grafo = generador.crear_grafo_conectado(20, 0.3)

# Buscar vértices específicos
origen = ConsultorGrafo.buscar_vertice_por_id(grafo, 0)
destino = ConsultorGrafo.buscar_vertice_por_id(grafo, 5)

if origen and destino:
    # Encontrar ruta más corta
    resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, origen, destino)
    
    if resultado:
        camino, distancia_total = resultado
        print(f"Ruta más corta: {len(camino)} nodos, distancia: {distancia_total:.2f}")
        
        # Mostrar el camino
        for i, nodo in enumerate(camino):
            print(f"  {i+1}. Nodo {nodo.element()['id']} ({nodo.element()['rol']})")
```

## Buenas Prácticas

### 1. Usar Semillas para Reproducibilidad

```python
generador = GeneradorGrafoConectado()
generador.establecer_semilla(12345)  # Resultados reproducibles

# Múltiples ejecuciones darán el mismo resultado
grafo1 = generador.crear_grafo_conectado(10, 0.3)
grafo2 = generador.crear_grafo_conectado(10, 0.3)
# grafo1 y grafo2 tendrán la misma estructura
```

### 2. Verificar Conectividad

```python
# Siempre verificar que el grafo esté conectado
if ConsultorGrafo.validar_conectividad(grafo):
    print("✓ Grafo está conectado")
else:
    print("⚠ Grafo desconectado - revisar parámetros")
    
    # Analizar componentes
    componentes = ConsultorGrafo.obtener_componentes_conexas(grafo)
    print(f"Número de componentes: {len(componentes)}")
```

### 3. Optimizar Probabilidad de Aristas

```python
# Para grafos pequeños (<20 nodos): probabilidad mayor
grafo_pequeño = generador.crear_grafo_conectado(10, 0.4)

# Para grafos grandes (>100 nodos): probabilidad menor
grafo_grande = generador.crear_grafo_conectado(200, 0.1)

# Verificar densidad resultante
stats = generador.obtener_estadisticas_grafo(grafo_grande)
print(f"Densidad del grafo: {stats['densidad']:.3f}")
```

### 4. Análisis de Rendimiento

```python
import time

# Medir tiempo de generación
inicio = time.time()
grafo = generador.crear_grafo_conectado(1000, 0.05)
tiempo_generacion = time.time() - inicio

print(f"Generación de 1000 nodos: {tiempo_generacion:.2f} segundos")

# Medir tiempo de búsqueda
inicio = time.time()
estadisticas = BuscadorNodos.obtener_estadisticas_roles(grafo)
tiempo_analisis = time.time() - inicio

print(f"Análisis de roles: {tiempo_analisis:.2f} segundos")
```

## Solución de Problemas Comunes

### Error: "Los porcentajes deben sumar 1.0"

```python
# ❌ Incorrecto
config = ConfiguracionRoles(0.2, 0.3, 0.4)  # Suma = 0.9

# ✅ Correcto
config = ConfiguracionRoles(0.2, 0.3, 0.5)  # Suma = 1.0
```

### Error: "El número de nodos debe ser mayor a 0"

```python
# ❌ Incorrecto
grafo = generador.crear_grafo_conectado(0, 0.3)

# ✅ Correcto
grafo = generador.crear_grafo_conectado(5, 0.3)  # Mínimo 1 nodo
```

### Problema: Grafo muy disperso

```python
# Si el grafo tiene pocas aristas, aumentar probabilidad
grafo = generador.crear_grafo_conectado(20, 0.5)  # Más denso

# O verificar la densidad
stats = generador.obtener_estadisticas_grafo(grafo)
if stats['densidad'] < 0.1:
    print("⚠ Grafo muy disperso, considerar aumentar probabilidad")
```

### Problema: Búsquedas devuelven None

```python
# Verificar que existen nodos del rol buscado
nodos_rol = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.ALMACENAMIENTO)
if not nodos_rol:
    print("⚠ No hay nodos de almacenamiento en el grafo")
    
    # Ver distribución actual
    stats = BuscadorNodos.obtener_estadisticas_roles(grafo)
    for rol, info in stats.items():
        print(f"{rol}: {info['cantidad']} nodos")
```

## Próximos Pasos

1. **Explorar Ejemplos**: Revisar `docs/examples/` para casos de uso específicos
2. **API Completa**: Consultar `docs/api/` para documentación detallada
3. **Ejecutar Pruebas**: Usar `tests/run_tests.py` para verificar funcionamiento
4. **Personalizar**: Crear configuraciones específicas para tu caso de uso

¡Listo para comenzar! El sistema está diseñado para ser intuitivo y escalable a tus necesidades específicas.

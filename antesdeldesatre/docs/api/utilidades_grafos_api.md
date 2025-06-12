# API de Utilidades de Grafos

## Descripción General

El módulo de utilidades de grafos proporciona herramientas avanzadas para consultar, analizar y buscar elementos dentro de grafos generados. Está organizado en tres clases principales que ofrecen funcionalidades específicas.

---

## Clases Principales

### `ConsultorGrafo`

**Descripción**: Proporciona métodos estáticos para consultas básicas y análisis de conectividad en grafos.

#### Métodos de Búsqueda

##### `buscar_vertice_por_nombre(grafo: Graph, nombre: str) -> Optional[Vertex]`

**Descripción**: Busca un vértice por su nombre.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar
- **`nombre`** (`str`): Nombre del vértice a buscar

**Retorna**: 
- `Optional[Vertex]`: El vértice encontrado o `None` si no existe

**Ejemplo**:
```python
vertice = ConsultorGrafo.buscar_vertice_por_nombre(grafo, "almacenamiento_0")
```

##### `buscar_vertice_por_id(grafo: Graph, id_vertice: int) -> Optional[Vertex]`

**Descripción**: Busca un vértice por su ID único.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar
- **`id_vertice`** (`int`): ID del vértice a buscar

**Retorna**: 
- `Optional[Vertex]`: El vértice encontrado o `None` si no existe

**Ejemplo**:
```python
vertice = ConsultorGrafo.buscar_vertice_por_id(grafo, 5)
```

##### `buscar_vertices_por_atributo(grafo: Graph, atributo: str, valor: Any) -> List[Vertex]`

**Descripción**: Busca todos los vértices que tienen un atributo específico con un valor determinado.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar
- **`atributo`** (`str`): Nombre del atributo a filtrar
- **`valor`** (`Any`): Valor del atributo a buscar

**Retorna**: 
- `List[Vertex]`: Lista de vértices que coinciden con el criterio

**Ejemplo**:
```python
# Buscar todos los nodos de almacenamiento
nodos_almacen = ConsultorGrafo.buscar_vertices_por_atributo(grafo, 'rol', 'almacenamiento')
```

#### Métodos de Análisis de Estructura

##### `obtener_vecinos(grafo: Graph, vertice: Vertex) -> List[Vertex]`

**Descripción**: Obtiene todos los vértices vecinos (adyacentes) a un vértice dado.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a consultar
- **`vertice`** (`Vertex`): Vértice del cual obtener los vecinos

**Retorna**: 
- `List[Vertex]`: Lista de vértices vecinos

**Ejemplo**:
```python
vecinos = ConsultorGrafo.obtener_vecinos(grafo, vertice)
print(f"El nodo tiene {len(vecinos)} vecinos")
```

##### `obtener_grado(grafo: Graph, vertice: Vertex) -> int`

**Descripción**: Calcula el grado (número de aristas incidentes) de un vértice.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a consultar
- **`vertice`** (`Vertex`): Vértice del cual calcular el grado

**Retorna**: 
- `int`: Grado del vértice

**Ejemplo**:
```python
grado = ConsultorGrafo.obtener_grado(grafo, vertice)
print(f"El nodo tiene grado {grado}")
```

##### `obtener_aristas_incidentes(grafo: Graph, vertice: Vertex) -> List[Edge]`

**Descripción**: Obtiene todas las aristas que inciden en un vértice.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a consultar
- **`vertice`** (`Vertex`): Vértice del cual obtener las aristas

**Retorna**: 
- `List[Edge]`: Lista de aristas incidentes

**Ejemplo**:
```python
aristas = ConsultorGrafo.obtener_aristas_incidentes(grafo, vertice)
for arista in aristas:
    peso = arista.element()['peso']
    print(f"Arista con peso: {peso}")
```

#### Métodos de Conectividad

##### `validar_conectividad(grafo: Graph) -> bool`

**Descripción**: Verifica si el grafo está conectado (existe un camino entre cualquier par de vértices).

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a verificar

**Retorna**: 
- `bool`: `True` si el grafo está conectado, `False` en caso contrario

**Algoritmo**: Utiliza búsqueda en profundidad (DFS) desde un vértice arbitrario

**Ejemplo**:
```python
es_conectado = ConsultorGrafo.validar_conectividad(grafo)
print(f"El grafo está conectado: {es_conectado}")
```

##### `obtener_componentes_conexas(grafo: Graph) -> List[List[Vertex]]`

**Descripción**: Encuentra todas las componentes conexas del grafo.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a analizar

**Retorna**: 
- `List[List[Vertex]]`: Lista de componentes, cada una siendo una lista de vértices

**Algoritmo**: Utiliza múltiples DFS para identificar componentes separadas

**Ejemplo**:
```python
componentes = ConsultorGrafo.obtener_componentes_conexas(grafo)
print(f"El grafo tiene {len(componentes)} componentes conexas")
for i, componente in enumerate(componentes):
    print(f"Componente {i+1}: {len(componente)} nodos")
```

---

### `CalculadorDistancias`

**Descripción**: Implementa algoritmos para calcular distancias y caminos más cortos en grafos ponderados.

#### Algoritmo de Dijkstra

##### `dijkstra(grafo: Graph, origen: Vertex) -> Tuple[Dict[Vertex, float], Dict[Vertex, Optional[Vertex]]]`

**Descripción**: Implementa el algoritmo de Dijkstra para encontrar las distancias más cortas desde un vértice origen a todos los demás.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo ponderado donde calcular distancias
- **`origen`** (`Vertex`): Vértice origen para el cálculo

**Retorna**: 
- `Tuple[Dict[Vertex, float], Dict[Vertex, Optional[Vertex]]]`: 
  - Primer elemento: Diccionario de distancias mínimas desde el origen
  - Segundo elemento: Diccionario de predecesores para reconstruir caminos

**Restricciones**:
- El grafo debe tener pesos positivos en las aristas
- Si no hay peso especificado, se asume peso 1.0

**Complejidad**: O((V + E) log V) donde V es número de vértices y E número de aristas

**Ejemplo**:
```python
distancias, predecesores = CalculadorDistancias.dijkstra(grafo, nodo_origen)
for nodo, distancia in distancias.items():
    if distancia != float('inf'):
        print(f"Distancia a {nodo.element()['nombre']}: {distancia}")
```

##### `reconstruir_camino(predecesores: Dict[Vertex, Optional[Vertex]], origen: Vertex, destino: Vertex) -> Optional[List[Vertex]]`

**Descripción**: Reconstruye el camino más corto entre dos vértices usando el resultado de Dijkstra.

**Parámetros**:
- **`predecesores`** (`Dict[Vertex, Optional[Vertex]]`): Diccionario de predecesores de Dijkstra
- **`origen`** (`Vertex`): Vértice origen del camino
- **`destino`** (`Vertex`): Vértice destino del camino

**Retorna**: 
- `Optional[List[Vertex]]`: Lista ordenada de vértices que forman el camino, o `None` si no existe

**Ejemplo**:
```python
_, predecesores = CalculadorDistancias.dijkstra(grafo, origen)
camino = CalculadorDistancias.reconstruir_camino(predecesores, origen, destino)
if camino:
    nombres = [v.element()['nombre'] for v in camino]
    print(f"Camino: {' -> '.join(nombres)}")
```

#### Métodos de Conveniencia

##### `calcular_distancia_entre(grafo: Graph, origen: Vertex, destino: Vertex) -> Optional[float]`

**Descripción**: Calcula la distancia más corta entre dos vértices específicos.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde calcular la distancia
- **`origen`** (`Vertex`): Vértice origen
- **`destino`** (`Vertex`): Vértice destino

**Retorna**: 
- `Optional[float]`: Distancia más corta, o `None` si no hay camino

**Ejemplo**:
```python
distancia = CalculadorDistancias.calcular_distancia_entre(grafo, nodo_a, nodo_b)
if distancia is not None:
    print(f"Distancia más corta: {distancia}")
```

##### `encontrar_camino_mas_corto(grafo: Graph, origen: Vertex, destino: Vertex) -> Optional[Tuple[List[Vertex], float]]`

**Descripción**: Encuentra el camino más corto entre dos vértices, incluyendo la distancia total.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar el camino
- **`origen`** (`Vertex`): Vértice origen
- **`destino`** (`Vertex`): Vértice destino

**Retorna**: 
- `Optional[Tuple[List[Vertex], float]]`: Tupla con el camino y la distancia total, o `None` si no existe

**Ejemplo**:
```python
resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, origen, destino)
if resultado:
    camino, distancia = resultado
    print(f"Camino encontrado con distancia {distancia}")
    print(f"Ruta: {[v.element()['nombre'] for v in camino]}")
```

---

### `BuscadorNodos`

**Descripción**: Proporciona métodos especializados para buscar nodos basándose en roles y calcular distancias entre ellos.

#### Búsqueda por Roles

##### `buscar_nodos_por_rol(grafo: Graph, rol: str) -> List[Vertex]`

**Descripción**: Encuentra todos los nodos que tienen un rol específico.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar
- **`rol`** (`str`): Rol a buscar (ej: RolNodo.ALMACENAMIENTO)

**Retorna**: 
- `List[Vertex]`: Lista de nodos con el rol especificado

**Ejemplo**:
```python
from model import RolNodo

nodos_recarga = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.RECARGA)
print(f"Encontrados {len(nodos_recarga)} nodos de recarga")
```

##### `buscar_nodo_mas_cercano_por_rol(grafo: Graph, origen: Vertex, rol: str) -> Optional[Tuple[Vertex, float]]`

**Descripción**: Encuentra el nodo más cercano con un rol específico desde un punto de origen.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar
- **`origen`** (`Vertex`): Vértice desde donde medir distancias
- **`rol`** (`str`): Rol del nodo a buscar

**Retorna**: 
- `Optional[Tuple[Vertex, float]]`: Tupla con el nodo más cercano y su distancia, o `None` si no hay nodos con ese rol

**Caso especial**: Si el origen ya tiene el rol buscado, retorna (origen, 0.0)

**Ejemplo**:
```python
resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(grafo, nodo_cliente, RolNodo.ALMACENAMIENTO)
if resultado:
    nodo, distancia = resultado
    print(f"Almacén más cercano: {nodo.element()['nombre']} a distancia {distancia}")
```

##### `buscar_k_nodos_mas_cercanos_por_rol(grafo: Graph, origen: Vertex, rol: str, k: int) -> List[Tuple[Vertex, float]]`

**Descripción**: Encuentra los k nodos más cercanos con un rol específico, ordenados por distancia.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo donde buscar
- **`origen`** (`Vertex`): Vértice desde donde medir distancias
- **`rol`** (`str`): Rol de los nodos a buscar
- **`k`** (`int`): Número máximo de nodos a retornar

**Retorna**: 
- `List[Tuple[Vertex, float]]`: Lista de tuplas (nodo, distancia) ordenada por distancia ascendente

**Ejemplo**:
```python
# Encontrar los 3 nodos de recarga más cercanos
cercanos = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(grafo, origen, RolNodo.RECARGA, 3)
for i, (nodo, distancia) in enumerate(cercanos, 1):
    print(f"{i}. {nodo.element()['nombre']}: distancia {distancia}")
```

#### Análisis Estadístico

##### `obtener_estadisticas_roles(grafo: Graph) -> Dict[str, Dict[str, Any]]`

**Descripción**: Calcula estadísticas detalladas para cada rol presente en el grafo.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a analizar

**Retorna**: 
- `Dict[str, Dict[str, Any]]`: Diccionario donde cada clave es un rol y el valor contiene:
  - `cantidad` (`int`): Número de nodos con este rol
  - `porcentaje` (`float`): Porcentaje que representa del total
  - `grado_promedio` (`float`): Grado promedio de nodos con este rol
  - `grado_maximo` (`int`): Grado máximo entre nodos con este rol
  - `grado_minimo` (`int`): Grado mínimo entre nodos con este rol
  - `nodos` (`List[Vertex]`): Lista de nodos con este rol

**Ejemplo**:
```python
stats = BuscadorNodos.obtener_estadisticas_roles(grafo)
for rol, info in stats.items():
    print(f"\nRol: {rol}")
    print(f"  Cantidad: {info['cantidad']} ({info['porcentaje']}%)")
    print(f"  Grado promedio: {info['grado_promedio']}")
    print(f"  Grado rango: {info['grado_minimo']}-{info['grado_maximo']}")
```

---

## Patrones de Uso Comunes

### 1. Análisis de Conectividad
```python
# Verificar si el grafo está bien conectado
if ConsultorGrafo.validar_conectividad(grafo):
    print("✅ Grafo conectado correctamente")
else:
    componentes = ConsultorGrafo.obtener_componentes_conexas(grafo)
    print(f"❌ Grafo desconectado: {len(componentes)} componentes")
```

### 2. Encontrar Servicios Más Cercanos
```python
# Desde un nodo cliente, encontrar el almacén más cercano
nodo_cliente = ConsultorGrafo.buscar_vertice_por_nombre(grafo, "cliente_0")
resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
    grafo, nodo_cliente, RolNodo.ALMACENAMIENTO
)
if resultado:
    almacen, distancia = resultado
    print(f"Almacén más cercano: {almacen.element()['nombre']} (distancia: {distancia})")
```

### 3. Análisis de Rutas
```python
# Calcular camino más corto entre dos puntos específicos
origen = ConsultorGrafo.buscar_vertice_por_id(grafo, 0)
destino = ConsultorGrafo.buscar_vertice_por_id(grafo, 5)

resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, origen, destino)
if resultado:
    camino, distancia_total = resultado
    print(f"Ruta: {[v.element()['nombre'] for v in camino]}")
    print(f"Distancia total: {distancia_total}")
```

### 4. Análisis Estadístico de Red
```python
# Obtener estadísticas completas por rol
stats = BuscadorNodos.obtener_estadisticas_roles(grafo)
print("\n📊 ESTADÍSTICAS POR ROL")
for rol, info in stats.items():
    print(f"{rol.upper()}:")
    print(f"  • {info['cantidad']} nodos ({info['porcentaje']}%)")
    print(f"  • Conectividad promedio: {info['grado_promedio']}")
```

---

## Consideraciones de Rendimiento

### Complejidad de Algoritmos

| Método | Complejidad | Notas |
|--------|-------------|-------|
| `dijkstra()` | O((V + E) log V) | Usa heap binario optimizado |
| `validar_conectividad()` | O(V + E) | DFS simple |
| `obtener_componentes_conexas()` | O(V + E) | Múltiples DFS |
| `buscar_*_por_rol()` | O(V) | Búsqueda lineal en vértices |
| `obtener_estadisticas_roles()` | O(V + E) | Calcula grados de todos los nodos |

### Optimizaciones Implementadas

1. **Dijkstra con heap**: Usa `heapq` para eficiencia en grafos grandes
2. **Contador único en heap**: Evita problemas de comparación entre vértices
3. **Detección temprana en DFS**: Para en cuanto encuentra desconexión
4. **Caché de vecinos**: Utiliza métodos optimizados del grafo base

### Limitaciones

- **Grafos muy grandes (>50,000 nodos)**: Considerar algoritmos especializados
- **Múltiples consultas de distancia**: Precalcular matriz de distancias
- **Análisis temporal**: Los métodos no conservan estado entre llamadas

---

## Manejo de Errores

### Casos de Borde Manejados

- **Grafos vacíos**: Retorna resultados apropiados (listas vacías, `False`, etc.)
- **Nodos aislados**: Se detectan correctamente en análisis de conectividad
- **Roles inexistentes**: Retorna listas vacías sin error
- **Distancias infinitas**: Se manejan apropiadamente con `float('inf')`

### Validaciones Automáticas

- Los métodos no modifican el grafo original
- Se valida que los vértices pertenezcan al grafo
- Se maneja graciosamente la ausencia de atributos en nodos

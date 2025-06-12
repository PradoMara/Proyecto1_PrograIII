# API de Generación de Grafos

## Descripción General

El módulo de generación de grafos proporciona herramientas completas para crear grafos conectados con roles específicos y funcionalidades avanzadas de consulta y análisis.

---

## Módulos Principales

### `model.generador_grafo`

Contiene las clases principales para la generación de grafos conectados.

### `model.utilidades_grafo`

Proporciona herramientas para análisis, búsqueda y consultas sobre grafos generados.

---

## Clases y Métodos

### `RolNodo`

**Descripción**: Constantes para los tipos de nodos disponibles en el sistema.

```python
class RolNodo:
    ALMACENAMIENTO = "almacenamiento"
    RECARGA = "recarga" 
    CLIENTE = "cliente"
```

#### Métodos

##### `todos_los_roles() -> List[str]`

**Descripción**: Retorna una lista con todos los roles disponibles.

**Retorna**: 
- `List[str]`: Lista de strings con los nombres de todos los roles

**Ejemplo**:
```python
roles = RolNodo.todos_los_roles()
# ['almacenamiento', 'recarga', 'cliente']
```

---

### `ConfiguracionRoles`

**Descripción**: Gestiona la configuración de distribución de roles en el grafo.

```python
class ConfiguracionRoles:
    def __init__(self, almacenamiento: float = 0.2, recarga: float = 0.3, cliente: float = 0.5)
```

#### Parámetros de Construcción

- **`almacenamiento`** (`float`, opcional): Porcentaje de nodos de almacenamiento (default: 0.2)
- **`recarga`** (`float`, opcional): Porcentaje de nodos de recarga (default: 0.3)
- **`cliente`** (`float`, opcional): Porcentaje de nodos cliente (default: 0.5)

#### Restricciones

- La suma de todos los porcentajes debe ser 1.0 (±0.001 de tolerancia)
- Todos los valores deben ser positivos

#### Métodos

##### `calcular_cantidad_nodos(total_nodos: int) -> Dict[str, int]`

**Descripción**: Calcula la cantidad exacta de nodos por rol para un total dado.

**Parámetros**:
- **`total_nodos`** (`int`): Número total de nodos a distribuir

**Retorna**: 
- `Dict[str, int]`: Diccionario con la cantidad de nodos por rol

**Garantías**:
- Siempre habrá al menos 1 nodo de almacenamiento
- Siempre habrá al menos 1 nodo de recarga
- Los nodos cliente pueden ser 0 si el total es muy pequeño

**Ejemplo**:
```python
config = ConfiguracionRoles(0.3, 0.4, 0.3)
distribucion = config.calcular_cantidad_nodos(10)
# {'almacenamiento': 3, 'recarga': 4, 'cliente': 3}
```

---

### `GeneradorGrafoConectado`

**Descripción**: Clase principal para generar grafos conectados con roles asignados.

```python
class GeneradorGrafoConectado:
    def __init__(self, configuracion_roles: Optional[ConfiguracionRoles] = None)
```

#### Parámetros de Construcción

- **`configuracion_roles`** (`ConfiguracionRoles`, opcional): Configuración de distribución de roles. Si no se proporciona, se usa la configuración por defecto.

#### Métodos

##### `establecer_semilla(semilla: int) -> None`

**Descripción**: Establece una semilla para la generación aleatoria, garantizando reproducibilidad.

**Parámetros**:
- **`semilla`** (`int`): Valor de la semilla aleatoria

**Ejemplo**:
```python
gen = GeneradorGrafoConectado()
gen.establecer_semilla(42)
```

##### `crear_grafo_conectado(numero_nodos: int, probabilidad_arista: float = 0.3) -> Graph`

**Descripción**: Crea un grafo conectado con el número especificado de nodos y roles distribuidos según la configuración.

**Parámetros**:
- **`numero_nodos`** (`int`): Número total de nodos en el grafo (mínimo 1)
- **`probabilidad_arista`** (`float`, opcional): Probabilidad de crear aristas adicionales entre cada par de nodos (default: 0.3)

**Retorna**: 
- `Graph`: Grafo conectado con roles asignados

**Restricciones**:
- `numero_nodos >= 1`
- `0.0 <= probabilidad_arista <= 1.0`

**Algoritmo**:
1. Crea nodos con roles distribuidos según la configuración
2. Construye un árbol de expansión para garantizar conectividad
3. Agrega aristas adicionales según la probabilidad especificada

**Ejemplo**:
```python
gen = GeneradorGrafoConectado()
grafo = gen.crear_grafo_conectado(10, 0.4)
```

##### `crear_grafo_con_roles_personalizados(distribución_roles: Dict[str, int], probabilidad_arista: float = 0.3) -> Graph`

**Descripción**: Crea un grafo con una distribución exacta de roles especificada por el usuario.

**Parámetros**:
- **`distribución_roles`** (`Dict[str, int]`): Diccionario especificando la cantidad exacta de nodos por rol
- **`probabilidad_arista`** (`float`, opcional): Probabilidad de aristas adicionales (default: 0.3)

**Retorna**: 
- `Graph`: Grafo conectado con la distribución exacta especificada

**Restricciones**:
- La suma de valores en `distribución_roles` debe ser >= 1
- Las claves deben ser roles válidos de `RolNodo`

**Ejemplo**:
```python
distribucion = {
    RolNodo.ALMACENAMIENTO: 2,
    RolNodo.RECARGA: 3,
    RolNodo.CLIENTE: 5
}
grafo = gen.crear_grafo_con_roles_personalizados(distribucion)
```

##### `obtener_estadisticas_grafo(grafo: Graph) -> Dict`

**Descripción**: Calcula estadísticas completas del grafo generado.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a analizar

**Retorna**: 
- `Dict`: Diccionario con las siguientes estadísticas:
  - `numero_vertices` (`int`): Número total de vértices
  - `numero_aristas` (`int`): Número total de aristas
  - `densidad` (`float`): Densidad del grafo (0.0 a 1.0)
  - `distribución_roles` (`Dict[str, int]`): Conteo de nodos por rol
  - `esta_conectado` (`bool`): Si el grafo está conectado
  - `grado_promedio` (`float`): Grado promedio de los nodos

**Ejemplo**:
```python
stats = gen.obtener_estadisticas_grafo(grafo)
print(f"Nodos: {stats['numero_vertices']}")
print(f"Aristas: {stats['numero_aristas']}")
print(f"Conectado: {stats['esta_conectado']}")
```

##### `imprimir_resumen_grafo(grafo: Graph) -> None`

**Descripción**: Imprime un resumen formateado de las estadísticas del grafo.

**Parámetros**:
- **`grafo`** (`Graph`): Grafo a resumir

**Salida**: Imprime directamente en la consola un resumen detallado

**Ejemplo**:
```python
gen.imprimir_resumen_grafo(grafo)
# ========================================
# RESUMEN DEL GRAFO GENERADO
# ========================================
# Número de vértices: 10
# Número de aristas: 15
# ...
```

---

## Estructura de Datos de Elementos

### Estructura de Vértice

Cada vértice generado contiene la siguiente información:

```python
datos_vertice = {
    'id': int,                    # Identificador único
    'rol': str,                   # Rol del nodo (ALMACENAMIENTO, RECARGA, CLIENTE)
    'nombre': str,                # Nombre descriptivo (ej: "almacenamiento_0")
    'propiedades': dict          # Propiedades adicionales (extensible)
}
```

### Estructura de Arista

Cada arista generada contiene la siguiente información:

```python
datos_arista = {
    'peso': float,               # Peso de la arista (1.0-10.0)
    'tipo': str,                 # Tipo: 'expansion' o 'adicional'
    'creado_en': str            # Fase de creación: 'generacion'
}
```

---

## Excepciones

### `ValueError`

Se lanza en los siguientes casos:

- **Configuración de roles inválida**: Los porcentajes no suman 1.0
- **Número de nodos inválido**: Menor a 1
- **Probabilidad de arista inválida**: Fuera del rango [0.0, 1.0]
- **Distribución de roles vacía**: Suma total de nodos es 0

---

## Notas de Implementación

### Algoritmo de Conectividad

El generador garantiza conectividad mediante:

1. **Árbol de Expansión**: Primero se crea un árbol de expansión que conecta todos los nodos
2. **Aristas Adicionales**: Luego se agregan aristas adicionales según la probabilidad especificada

### Distribución de Roles

- Los roles se asignan de manera aleatoria pero respetando las proporciones especificadas
- Siempre se garantiza al menos 1 nodo de almacenamiento y 1 de recarga
- Los nodos cliente pueden ser 0 solo en grafos muy pequeños

### Pesos de Aristas

- Todos los pesos se generan aleatoriamente entre 1.0 y 10.0
- Los pesos se redondean a 2 decimales para evitar problemas de precisión
- No hay correlación entre el peso y el tipo de arista

---

## Consideraciones de Rendimiento

### Complejidad Temporal

- **Creación de nodos**: O(n)
- **Árbol de expansión**: O(n)
- **Aristas adicionales**: O(n²)
- **Verificación de conectividad**: O(n + m)

**Total**: O(n²) donde n es el número de nodos

### Limitaciones

- Para grafos con más de 10,000 nodos, considerar optimizaciones
- La memoria utilizada es O(n²) en el peor caso (grafo completo)
- La generación de números aleatorios puede ser el cuello de botella en grafos muy grandes

---

## Casos de Uso Recomendados

### Simulaciones de Red
- Redes de distribución de contenido
- Sistemas de almacenamiento distribuido
- Arquitecturas cliente-servidor

### Investigación y Testing
- Benchmarking de algoritmos de grafos
- Estudios de conectividad y robustez
- Generación de datasets para machine learning

### Desarrollo de Software
- Testing de algoritmos de ruteo
- Validación de sistemas distribuidos
- Prototipado rápido de topologías de red

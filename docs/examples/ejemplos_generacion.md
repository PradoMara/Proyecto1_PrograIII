# Ejemplos Prácticos - Generación de Grafos

## Descripción

Esta colección de ejemplos muestra cómo usar el sistema de generación de grafos para diferentes casos de uso comunes. Cada ejemplo está completamente documentado y listo para ejecutar.

---

## Ejemplo 1: Generación Básica de Red

```python
# Generar una red básica con configuración por defecto
from model import GeneradorGrafoConectado, RolNodo

# Crear generador con configuración por defecto (20% almacén, 30% recarga, 50% cliente)
generador = GeneradorGrafoConectado()

# Generar red de 10 nodos con probabilidad de conexión 0.3
red = generador.crear_grafo_conectado(numero_nodos=10, probabilidad_arista=0.3)

# Mostrar estadísticas
print("🌐 RED GENERADA")
generador.imprimir_resumen_grafo(red)

# Resultado esperado:
# - 10 nodos total
# - ~2 nodos de almacenamiento
# - ~3 nodos de recarga  
# - ~5 nodos cliente
# - Red garantizadamente conectada
```

---

## Ejemplo 2: Configuración Personalizada de Roles

```python
from model import GeneradorGrafoConectado, ConfiguracionRoles, RolNodo

# Crear configuración personalizada para un data center
# 40% almacenamiento, 30% recarga, 30% cliente
config_datacenter = ConfiguracionRoles(
    almacenamiento=0.4,
    recarga=0.3, 
    cliente=0.3
)

# Crear generador con la configuración personalizada
generador = GeneradorGrafoConectado(config_datacenter)

# Generar red de data center con alta conectividad
red_datacenter = generador.crear_grafo_conectado(
    numero_nodos=20, 
    probabilidad_arista=0.6
)

print("🏢 DATA CENTER GENERADO")
stats = generador.obtener_estadisticas_grafo(red_datacenter)
print(f"Nodos: {stats['numero_vertices']}")
print(f"Aristas: {stats['numero_aristas']}")
print(f"Densidad: {stats['densidad']}")
print(f"Distribución: {stats['distribución_roles']}")
```

---

## Ejemplo 3: Red con Distribución Exacta

```python
from model import GeneradorGrafoConectado, RolNodo

# Definir distribución exacta para una red específica
distribucion_custom = {
    RolNodo.ALMACENAMIENTO: 3,  # Exactamente 3 nodos de almacén
    RolNodo.RECARGA: 5,         # Exactamente 5 nodos de recarga
    RolNodo.CLIENTE: 12         # Exactamente 12 nodos cliente
}

generador = GeneradorGrafoConectado()

# Crear red con distribución exacta
red_custom = generador.crear_grafo_con_roles_personalizados(
    distribución_roles=distribucion_custom,
    probabilidad_arista=0.4
)

print("🎯 RED CON DISTRIBUCIÓN EXACTA")
generador.imprimir_resumen_grafo(red_custom)

# Verificar que la distribución es exacta
stats = generador.obtener_estadisticas_grafo(red_custom)
distribucion_real = stats['distribución_roles']
print(f"✅ Almacenamiento: {distribucion_real[RolNodo.ALMACENAMIENTO]}/3")
print(f"✅ Recarga: {distribucion_real[RolNodo.RECARGA]}/5") 
print(f"✅ Cliente: {distribucion_real[RolNodo.CLIENTE]}/12")
```

---

## Ejemplo 4: Generación Reproducible con Semilla

```python
from model import GeneradorGrafoConectado

def generar_red_reproducible(semilla=42):
    """Genera una red que siempre será idéntica con la misma semilla"""
    generador = GeneradorGrafoConectado()
    
    # Establecer semilla para reproducibilidad
    generador.establecer_semilla(semilla)
    
    # Generar red
    red = generador.crear_grafo_conectado(numero_nodos=8, probabilidad_arista=0.5)
    
    return red, generador.obtener_estadisticas_grafo(red)

# Generar la misma red dos veces
print("🎲 GENERACIÓN REPRODUCIBLE")
red1, stats1 = generar_red_reproducible(semilla=123)
red2, stats2 = generar_red_reproducible(semilla=123)

print(f"Red 1: {stats1['numero_vertices']} nodos, {stats1['numero_aristas']} aristas")
print(f"Red 2: {stats2['numero_vertices']} nodos, {stats2['numero_aristas']} aristas")
print(f"¿Son idénticas? {stats1 == stats2}")  # Debería ser True
```

---

## Ejemplo 5: Análisis Completo de Red Generada

```python
from model import GeneradorGrafoConectado, ConsultorGrafo, BuscadorNodos, RolNodo

# Generar red para análisis
generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=15, probabilidad_arista=0.4)

print("📊 ANÁLISIS COMPLETO DE RED")
print("=" * 50)

# 1. Estadísticas básicas
stats = generador.obtener_estadisticas_grafo(red)
print(f"Nodos: {stats['numero_vertices']}")
print(f"Aristas: {stats['numero_aristas']}")
print(f"Densidad: {stats['densidad']}")
print(f"Grado promedio: {stats['grado_promedio']}")
print(f"Conectado: {'✅' if stats['esta_conectado'] else '❌'}")

# 2. Análisis por roles
print("\n🏷️ ANÁLISIS POR ROLES")
estadisticas_roles = BuscadorNodos.obtener_estadisticas_roles(red)
for rol, info in estadisticas_roles.items():
    print(f"{rol.upper()}:")
    print(f"  • Cantidad: {info['cantidad']} ({info['porcentaje']}%)")
    print(f"  • Grado promedio: {info['grado_promedio']}")
    print(f"  • Rango de grados: {info['grado_minimo']}-{info['grado_maximo']}")

# 3. Verificar conectividad detallada
if ConsultorGrafo.validar_conectividad(red):
    print("\n✅ Red completamente conectada")
else:
    componentes = ConsultorGrafo.obtener_componentes_conexas(red)
    print(f"\n❌ Red desconectada: {len(componentes)} componentes")
    for i, comp in enumerate(componentes):
        print(f"  Componente {i+1}: {len(comp)} nodos")

print("=" * 50)
```

---

## Ejemplo 6: Simulación de Diferentes Topologías

```python
from model import GeneradorGrafoConectado, ConfiguracionRoles

def simular_topologia(nombre, config, nodos, probabilidad):
    """Simula una topología específica y retorna métricas"""
    generador = GeneradorGrafoConectado(config)
    red = generador.crear_grafo_conectado(nodos, probabilidad)
    stats = generador.obtener_estadisticas_grafo(red)
    
    return {
        'nombre': nombre,
        'nodos': stats['numero_vertices'],
        'aristas': stats['numero_aristas'],
        'densidad': stats['densidad'],
        'grado_promedio': stats['grado_promedio'],
        'roles': stats['distribución_roles']
    }

# Definir diferentes configuraciones
configs = {
    'Red P2P': ConfiguracionRoles(0.1, 0.1, 0.8),      # Muchos clientes
    'Data Center': ConfiguracionRoles(0.5, 0.3, 0.2),   # Mucho almacenamiento
    'Red Híbrida': ConfiguracionRoles(0.25, 0.35, 0.4), # Balanceada con énfasis en recarga
    'Red Distribuida': ConfiguracionRoles(0.33, 0.33, 0.34) # Completamente balanceada
}

print("🌍 COMPARACIÓN DE TOPOLOGÍAS")
print("=" * 70)
print(f"{'Topología':<15} {'Nodos':<6} {'Aristas':<8} {'Densidad':<10} {'Grado Prom':<12}")
print("-" * 70)

resultados = []
for nombre, config in configs.items():
    resultado = simular_topologia(nombre, config, nodos=20, probabilidad=0.3)
    resultados.append(resultado)
    
    print(f"{resultado['nombre']:<15} "
          f"{resultado['nodos']:<6} "
          f"{resultado['aristas']:<8} "
          f"{resultado['densidad']:<10.3f} "
          f"{resultado['grado_promedio']:<12.2f}")

print("=" * 70)

# Mostrar distribución de roles
print("\n📋 DISTRIBUCIÓN DE ROLES")
for resultado in resultados:
    print(f"\n{resultado['nombre']}:")
    roles = resultado['roles']
    total = sum(roles.values())
    for rol, cantidad in roles.items():
        porcentaje = (cantidad / total) * 100
        print(f"  • {rol}: {cantidad} ({porcentaje:.1f}%)")
```

---

## Ejemplo 7: Generación Escalable para Pruebas

```python
import time
from model import GeneradorGrafoConectado

def benchmark_generacion(tamaños_red):
    """Benchmark de generación para diferentes tamaños de red"""
    generador = GeneradorGrafoConectado()
    resultados = []
    
    print("⚡ BENCHMARK DE GENERACIÓN")
    print("=" * 50)
    print(f"{'Nodos':<8} {'Tiempo (s)':<12} {'Aristas':<10} {'Densidad':<10}")
    print("-" * 50)
    
    for tamaño in tamaños_red:
        inicio = time.time()
        
        # Generar red
        red = generador.crear_grafo_conectado(
            numero_nodos=tamaño, 
            probabilidad_arista=0.3
        )
        
        fin = time.time()
        tiempo = fin - inicio
        
        # Obtener estadísticas
        stats = generador.obtener_estadisticas_grafo(red)
        
        resultado = {
            'nodos': tamaño,
            'tiempo': tiempo,
            'aristas': stats['numero_aristas'],
            'densidad': stats['densidad']
        }
        resultados.append(resultado)
        
        print(f"{resultado['nodos']:<8} "
              f"{resultado['tiempo']:<12.4f} "
              f"{resultado['aristas']:<10} "
              f"{resultado['densidad']:<10.3f}")
    
    print("=" * 50)
    return resultados

# Ejecutar benchmark
tamaños = [10, 25, 50, 100, 200]
resultados = benchmark_generacion(tamaños)

# Análisis de escalabilidad
print("\n📈 ANÁLISIS DE ESCALABILIDAD")
for i in range(1, len(resultados)):
    factor_nodos = resultados[i]['nodos'] / resultados[i-1]['nodos']
    factor_tiempo = resultados[i]['tiempo'] / resultados[i-1]['tiempo']
    print(f"{resultados[i-1]['nodos']} → {resultados[i]['nodos']} nodos: "
          f"tiempo x{factor_tiempo:.2f} (factor nodos: x{factor_nodos:.1f})")
```

---

## Ejemplo 8: Validación y Testing

```python
from model import GeneradorGrafoConectado, ConfiguracionRoles, RolNodo, ConsultorGrafo

def validar_red_generada(red, generador, config_esperada=None):
    """Valida que una red cumple con todos los requisitos"""
    errores = []
    
    # 1. Verificar conectividad
    if not ConsultorGrafo.validar_conectividad(red):
        errores.append("❌ Red no está conectada")
    else:
        print("✅ Red está conectada")
    
    # 2. Verificar que todos los nodos tienen roles válidos
    nodos_sin_rol = 0
    for vertice in red.vertices():
        rol = vertice.element().get('rol')
        if rol not in RolNodo.todos_los_roles():
            nodos_sin_rol += 1
    
    if nodos_sin_rol > 0:
        errores.append(f"❌ {nodos_sin_rol} nodos sin rol válido")
    else:
        print("✅ Todos los nodos tienen roles válidos")
    
    # 3. Verificar estructura de datos
    stats = generador.obtener_estadisticas_grafo(red)
    if stats['numero_vertices'] < 1:
        errores.append("❌ Red vacía")
    else:
        print(f"✅ Red tiene {stats['numero_vertices']} nodos")
    
    # 4. Verificar que hay al menos un nodo de cada rol crítico
    roles = stats['distribución_roles']
    if roles.get(RolNodo.ALMACENAMIENTO, 0) < 1:
        errores.append("❌ No hay nodos de almacenamiento")
    if roles.get(RolNodo.RECARGA, 0) < 1:
        errores.append("❌ No hay nodos de recarga")
    
    if not errores:
        print("✅ Todos los roles críticos están presentes")
    
    # 5. Verificar integridad de aristas
    aristas_validas = True
    for arista in red.edges():
        peso = arista.element().get('peso')
        if peso is None or peso <= 0:
            aristas_validas = False
            break
    
    if aristas_validas:
        print("✅ Todas las aristas tienen pesos válidos")
    else:
        errores.append("❌ Algunas aristas tienen pesos inválidos")
    
    return len(errores) == 0, errores

# Ejecutar validación completa
print("🔍 VALIDACIÓN COMPLETA DE RED")
print("=" * 40)

generador = GeneradorGrafoConectado()
red_test = generador.crear_grafo_conectado(numero_nodos=12, probabilidad_arista=0.4)

es_valida, errores = validar_red_generada(red_test, generador)

print("\n📋 RESULTADO DE VALIDACIÓN")
if es_valida:
    print("🎉 ¡Red válida y lista para usar!")
else:
    print("⚠️ Errores encontrados:")
    for error in errores:
        print(f"  {error}")

print("=" * 40)
```

---

## Ejemplo 9: Exportación y Análisis de Datos

```python
import json
from model import GeneradorGrafoConectado, BuscadorNodos

def exportar_red_a_dict(red, generador):
    """Exporta una red a un diccionario serializable"""
    stats = generador.obtener_estadisticas_grafo(red)
    stats_roles = BuscadorNodos.obtener_estadisticas_roles(red)
    
    # Exportar estructura básica
    datos_red = {
        'metadata': {
            'timestamp': '2025-06-04',
            'generador': 'GeneradorGrafoConectado v1.0',
            'total_nodos': stats['numero_vertices'],
            'total_aristas': stats['numero_aristas']
        },
        'estadisticas': {
            'densidad': stats['densidad'],
            'grado_promedio': stats['grado_promedio'],
            'conectado': stats['esta_conectado'],
            'distribucion_roles': stats['distribución_roles']
        },
        'nodos': [],
        'aristas': []
    }
    
    # Exportar nodos
    for vertice in red.vertices():
        elemento = vertice.element()
        datos_red['nodos'].append({
            'id': elemento.get('id'),
            'nombre': elemento.get('nombre'),
            'rol': elemento.get('rol'),
            'grado': red.degree(vertice)
        })
    
    # Exportar aristas
    for i, arista in enumerate(red.edges()):
        endpoints = arista.endpoints()
        v1_id = endpoints[0].element().get('id')
        v2_id = endpoints[1].element().get('id')
        elemento = arista.element()
        
        datos_red['aristas'].append({
            'id': i,
            'origen': v1_id,
            'destino': v2_id,
            'peso': elemento.get('peso'),
            'tipo': elemento.get('tipo')
        })
    
    return datos_red

# Generar y exportar red
print("💾 EXPORTACIÓN DE RED")
print("=" * 30)

generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=8, probabilidad_arista=0.5)

datos_exportados = exportar_red_a_dict(red, generador)

# Mostrar resumen de exportación
print(f"✅ Red exportada exitosamente")
print(f"📊 Nodos: {len(datos_exportados['nodos'])}")
print(f"🔗 Aristas: {len(datos_exportados['aristas'])}")
print(f"🎯 Densidad: {datos_exportados['estadisticas']['densidad']}")

# Ejemplo de serialización JSON
json_data = json.dumps(datos_exportados, indent=2, ensure_ascii=False)
print(f"\n📄 Tamaño JSON: {len(json_data)} caracteres")

# Mostrar muestra de los datos
print("\n🔍 MUESTRA DE DATOS EXPORTADOS:")
print("Primeros 3 nodos:")
for nodo in datos_exportados['nodos'][:3]:
    print(f"  • {nodo['nombre']} (ID: {nodo['id']}, Rol: {nodo['rol']}, Grado: {nodo['grado']})")

print("\nPrimeras 3 aristas:")
for arista in datos_exportados['aristas'][:3]:
    print(f"  • {arista['origen']} → {arista['destino']} (Peso: {arista['peso']}, Tipo: {arista['tipo']})")

print("=" * 30)
```

---

## Ejemplo 10: Casos de Uso Avanzados

```python
from model import GeneradorGrafoConectado, ConfiguracionRoles, RolNodo

class GeneradorRedEspecializada:
    """Generador especializado para casos de uso específicos"""
    
    @staticmethod
    def crear_red_cdn():
        """Crea una red optimizada para CDN (Content Delivery Network)"""
        # Configuración CDN: muchos nodos de almacenamiento
        config_cdn = ConfiguracionRoles(
            almacenamiento=0.6,  # 60% servidores de contenido
            recarga=0.2,         # 20% servidores de origen
            cliente=0.2          # 20% puntos de acceso
        )
        
        generador = GeneradorGrafoConectado(config_cdn)
        return generador.crear_grafo_conectado(
            numero_nodos=25,
            probabilidad_arista=0.4  # Conectividad moderada
        )
    
    @staticmethod
    def crear_red_iot():
        """Crea una red IoT con muchos dispositivos cliente"""
        config_iot = ConfiguracionRoles(
            almacenamiento=0.1,  # 10% gateways principales
            recarga=0.15,        # 15% nodos de procesamiento
            cliente=0.75         # 75% sensores/dispositivos
        )
        
        generador = GeneradorGrafoConectado(config_iot)
        return generador.crear_grafo_conectado(
            numero_nodos=30,
            probabilidad_arista=0.25  # Conectividad baja (ahorro energía)
        )
    
    @staticmethod
    def crear_red_blockchain():
        """Crea una red blockchain con nodos equilibrados"""
        config_blockchain = ConfiguracionRoles(
            almacenamiento=0.4,  # 40% nodos de almacenamiento
            recarga=0.4,         # 40% nodos de minería/validación
            cliente=0.2          # 20% nodos ligeros
        )
        
        generador = GeneradorGrafoConectado(config_blockchain)
        return generador.crear_grafo_conectado(
            numero_nodos=20,
            probabilidad_arista=0.7  # Alta conectividad para consenso
        )

# Demostración de redes especializadas
print("🚀 REDES ESPECIALIZADAS")
print("=" * 50)

casos_uso = [
    ('CDN', GeneradorRedEspecializada.crear_red_cdn),
    ('IoT', GeneradorRedEspecializada.crear_red_iot),
    ('Blockchain', GeneradorRedEspecializada.crear_red_blockchain)
]

generador_base = GeneradorGrafoConectado()

for nombre, crear_red in casos_uso:
    print(f"\n🌐 RED {nombre}")
    print("-" * 30)
    
    red = crear_red()
    stats = generador_base.obtener_estadisticas_grafo(red)
    
    print(f"Nodos: {stats['numero_vertices']}")
    print(f"Aristas: {stats['numero_aristas']}")
    print(f"Densidad: {stats['densidad']:.3f}")
    print(f"Grado promedio: {stats['grado_promedio']:.2f}")
    
    print("Distribución de roles:")
    total = stats['numero_vertices']
    for rol, cantidad in stats['distribución_roles'].items():
        porcentaje = (cantidad / total) * 100
        print(f"  • {rol}: {cantidad} ({porcentaje:.1f}%)")

print("=" * 50)
```

---

## Notas de Implementación

### Mejores Prácticas

1. **Siempre verificar conectividad** después de generar una red
2. **Usar semillas** para testing y debugging reproducibles
3. **Validar configuraciones** antes de generar redes grandes
4. **Monitorear rendimiento** en redes con más de 100 nodos

### Patrones Comunes

- **Generación → Análisis → Validación**: Flujo estándar recomendado
- **Configuración personalizada**: Para casos de uso específicos
- **Batch generation**: Para comparar múltiples topologías
- **Exportación de datos**: Para análisis externos o persistencia

### Consideraciones de Rendimiento

- Redes pequeñas (≤50 nodos): Tiempo negligible
- Redes medianas (51-200 nodos): < 1 segundo
- Redes grandes (201-1000 nodos): 1-10 segundos
- Redes muy grandes (>1000 nodos): Considerar optimizaciones

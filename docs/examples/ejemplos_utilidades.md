# Ejemplos Prácticos - Utilidades de Grafos

## Descripción

Esta colección muestra cómo usar las utilidades de grafos para análisis, búsquedas y cálculos de distancias en redes generadas. Incluye casos de uso comunes y patrones de implementación.

---

## Ejemplo 1: Análisis Básico de Red

```python
from model import GeneradorGrafoConectado, ConsultorGrafo, BuscadorNodos, RolNodo

# Generar una red para análisis
generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=12, probabilidad_arista=0.4)

print("🔍 ANÁLISIS BÁSICO DE RED")
print("=" * 40)

# 1. Verificar conectividad básica
conectada = ConsultorGrafo.validar_conectividad(red)
print(f"Red conectada: {'✅' if conectada else '❌'}")

# 2. Buscar nodos por rol
nodos_almacen = BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.ALMACENAMIENTO)
nodos_recarga = BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.RECARGA)
nodos_cliente = BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.CLIENTE)

print(f"\n📊 Distribución encontrada:")
print(f"  • Almacenamiento: {len(nodos_almacen)} nodos")
print(f"  • Recarga: {len(nodos_recarga)} nodos")
print(f"  • Cliente: {len(nodos_cliente)} nodos")

# 3. Analizar conectividad de cada tipo
print(f"\n🔗 Análisis de conectividad:")
for tipo, nodos in [
    ("Almacenamiento", nodos_almacen),
    ("Recarga", nodos_recarga),
    ("Cliente", nodos_cliente)
]:
    if nodos:
        nodo_ejemplo = nodos[0]
        grado = ConsultorGrafo.obtener_grado(red, nodo_ejemplo)
        vecinos = ConsultorGrafo.obtener_vecinos(red, nodo_ejemplo)
        print(f"  • {tipo}: grado promedio ejemplo = {grado}")
        print(f"    Vecinos de {nodo_ejemplo.element()['nombre']}: {len(vecinos)}")

print("=" * 40)
```

---

## Ejemplo 2: Búsqueda de Servicios Más Cercanos

```python
from model import (GeneradorGrafoConectado, BuscadorNodos, CalculadorDistancias, 
                   ConsultorGrafo, RolNodo)

# Generar red de ejemplo
generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=15, probabilidad_arista=0.3)

print("🎯 BÚSQUEDA DE SERVICIOS MÁS CERCANOS")
print("=" * 45)

# Encontrar un nodo cliente para el ejemplo
nodos_cliente = BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.CLIENTE)
if not nodos_cliente:
    print("❌ No hay nodos cliente en la red")
    exit()

cliente_origen = nodos_cliente[0]
print(f"📍 Origen: {cliente_origen.element()['nombre']}")

# 1. Encontrar el almacén más cercano
resultado_almacen = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
    red, cliente_origen, RolNodo.ALMACENAMIENTO
)

if resultado_almacen:
    almacen, distancia = resultado_almacen
    print(f"\n🏪 Almacén más cercano:")
    print(f"  • Nodo: {almacen.element()['nombre']}")
    print(f"  • Distancia: {distancia:.2f}")
    
    # Obtener el camino completo
    camino_resultado = CalculadorDistancias.encontrar_camino_mas_corto(
        red, cliente_origen, almacen
    )
    if camino_resultado:
        camino, _ = camino_resultado
        nombres_camino = [v.element()['nombre'] for v in camino]
        print(f"  • Ruta: {' → '.join(nombres_camino)}")
else:
    print("❌ No se encontró almacén accesible")

# 2. Encontrar los 3 nodos de recarga más cercanos
recargas_cercanas = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
    red, cliente_origen, RolNodo.RECARGA, k=3
)

print(f"\n🔋 Top 3 nodos de recarga más cercanos:")
for i, (nodo_recarga, distancia) in enumerate(recargas_cercanas, 1):
    print(f"  {i}. {nodo_recarga.element()['nombre']}: distancia {distancia:.2f}")

# 3. Análisis de cobertura
print(f"\n📡 Análisis de cobertura desde {cliente_origen.element()['nombre']}:")
distancias, _ = CalculadorDistancias.dijkstra(red, cliente_origen)

nodos_accesibles = 0
distancia_maxima = 0
distancia_promedio = 0

for nodo, dist in distancias.items():
    if dist != float('inf'):
        nodos_accesibles += 1
        distancia_maxima = max(distancia_maxima, dist)
        distancia_promedio += dist

if nodos_accesibles > 0:
    distancia_promedio /= nodos_accesibles
    print(f"  • Nodos accesibles: {nodos_accesibles}/{len(list(red.vertices()))}")
    print(f"  • Distancia máxima: {distancia_maxima:.2f}")
    print(f"  • Distancia promedio: {distancia_promedio:.2f}")

print("=" * 45)
```

---

## Ejemplo 3: Análisis de Rutas y Caminos

```python
from model import (GeneradorGrafoConectado, CalculadorDistancias, ConsultorGrafo, 
                   BuscadorNodos, RolNodo)

# Generar red con alta conectividad para análisis de rutas
generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=10, probabilidad_arista=0.6)

print("🛤️ ANÁLISIS DE RUTAS Y CAMINOS")
print("=" * 40)

# Seleccionar dos nodos para análisis detallado
nodos = list(red.vertices())
if len(nodos) >= 2:
    origen = nodos[0]
    destino = nodos[-1]  # Último nodo
    
    print(f"📍 Análisis de ruta:")
    print(f"  Origen: {origen.element()['nombre']} (rol: {origen.element()['rol']})")
    print(f"  Destino: {destino.element()['nombre']} (rol: {destino.element()['rol']})")
    
    # 1. Calcular camino más corto
    resultado_camino = CalculadorDistancias.encontrar_camino_mas_corto(red, origen, destino)
    
    if resultado_camino:
        camino, distancia_total = resultado_camino
        print(f"\n🎯 Camino más corto encontrado:")
        print(f"  • Distancia total: {distancia_total:.2f}")
        print(f"  • Número de saltos: {len(camino) - 1}")
        
        # Mostrar ruta detallada
        print(f"  • Ruta detallada:")
        for i, nodo in enumerate(camino):
            elemento = nodo.element()
            if i == 0:
                print(f"    {i+1}. 🚀 {elemento['nombre']} ({elemento['rol']})")
            elif i == len(camino) - 1:
                print(f"    {i+1}. 🏁 {elemento['nombre']} ({elemento['rol']})")
            else:
                print(f"    {i+1}. ⚡ {elemento['nombre']} ({elemento['rol']})")
        
        # Calcular distancias intermedias
        print(f"\n📏 Distancias acumuladas:")
        distancias_desde_origen, _ = CalculadorDistancias.dijkstra(red, origen)
        for i, nodo in enumerate(camino):
            dist_acum = distancias_desde_origen[nodo]
            print(f"    Hasta {nodo.element()['nombre']}: {dist_acum:.2f}")
    
    else:
        print("❌ No existe camino entre los nodos seleccionados")
    
    # 2. Análisis de rutas alternativas por roles
    print(f"\n🔀 Análisis de rutas por roles:")
    
    for rol_intermedio in RolNodo.todos_los_roles():
        nodos_intermedios = BuscadorNodos.buscar_nodos_por_rol(red, rol_intermedio)
        
        if nodos_intermedios:
            mejor_ruta_via_rol = None
            mejor_distancia = float('inf')
            
            for nodo_intermedio in nodos_intermedios:
                if nodo_intermedio != origen and nodo_intermedio != destino:
                    # Calcular ruta: origen → intermedio → destino
                    dist1 = CalculadorDistancias.calcular_distancia_entre(red, origen, nodo_intermedio)
                    dist2 = CalculadorDistancias.calcular_distancia_entre(red, nodo_intermedio, destino)
                    
                    if dist1 is not None and dist2 is not None:
                        distancia_total = dist1 + dist2
                        if distancia_total < mejor_distancia:
                            mejor_distancia = distancia_total
                            mejor_ruta_via_rol = nodo_intermedio
            
            if mejor_ruta_via_rol:
                print(f"  • Vía {rol_intermedio}: {mejor_distancia:.2f} "
                      f"(a través de {mejor_ruta_via_rol.element()['nombre']})")
            else:
                print(f"  • Vía {rol_intermedio}: no disponible")

print("=" * 40)
```

---

## Ejemplo 4: Análisis de Conectividad Avanzado

```python
from model import GeneradorGrafoConectado, ConsultorGrafo, BuscadorNodos

# Generar red para análisis de conectividad
generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=20, probabilidad_arista=0.25)

print("🕸️ ANÁLISIS DE CONECTIVIDAD AVANZADO")
print("=" * 45)

# 1. Análisis de componentes conexas
componentes = ConsultorGrafo.obtener_componentes_conexas(red)
print(f"📊 Componentes conexas: {len(componentes)}")

if len(componentes) == 1:
    print("✅ Red completamente conectada")
    componente_principal = componentes[0]
    
    # Análisis de la componente principal
    print(f"   • Nodos en componente principal: {len(componente_principal)}")
    
    # Encontrar nodos más conectados
    nodos_por_grado = []
    for nodo in componente_principal:
        grado = ConsultorGrafo.obtener_grado(red, nodo)
        nodos_por_grado.append((nodo, grado))
    
    # Ordenar por grado (más conectados primero)
    nodos_por_grado.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🌟 Top 5 nodos más conectados:")
    for i, (nodo, grado) in enumerate(nodos_por_grado[:5], 1):
        elemento = nodo.element()
        vecinos = ConsultorGrafo.obtener_vecinos(red, nodo)
        roles_vecinos = {}
        for vecino in vecinos:
            rol = vecino.element()['rol']
            roles_vecinos[rol] = roles_vecinos.get(rol, 0) + 1
        
        print(f"   {i}. {elemento['nombre']} ({elemento['rol']}): grado {grado}")
        print(f"      Conecta con: {dict(roles_vecinos)}")

else:
    print("⚠️ Red fragmentada en múltiples componentes")
    for i, componente in enumerate(componentes, 1):
        print(f"   • Componente {i}: {len(componente)} nodos")
        
        # Analizar cada componente
        roles_en_componente = {}
        for nodo in componente:
            rol = nodo.element()['rol']
            roles_en_componente[rol] = roles_en_componente.get(rol, 0) + 1
        
        print(f"     Roles: {dict(roles_en_componente)}")

# 2. Análisis de puntos críticos (nodos de alta conectividad)
print(f"\n🔗 Análisis de puntos críticos:")

estadisticas_roles = BuscadorNodos.obtener_estadisticas_roles(red)
for rol, stats in estadisticas_roles.items():
    print(f"\n{rol.upper()}:")
    print(f"   • Cantidad: {stats['cantidad']}")
    print(f"   • Grado promedio: {stats['grado_promedio']}")
    print(f"   • Rango de grados: {stats['grado_minimo']} - {stats['grado_maximo']}")
    
    # Identificar nodos críticos (grado > promedio)
    nodos_criticos = []
    for nodo in stats['nodos']:
        grado = ConsultorGrafo.obtener_grado(red, nodo)
        if grado > stats['grado_promedio']:
            nodos_criticos.append((nodo, grado))
    
    if nodos_criticos:
        nodos_criticos.sort(key=lambda x: x[1], reverse=True)
        print(f"   • Nodos críticos: {len(nodos_criticos)}")
        for nodo, grado in nodos_criticos[:3]:  # Top 3
            print(f"     - {nodo.element()['nombre']}: grado {grado}")

# 3. Análisis de robustez
print(f"\n🛡️ Análisis de robustez:")
total_nodos = len(list(red.vertices()))
total_aristas = len(list(red.edges()))

# Calcular métricas de robustez
grados = [ConsultorGrafo.obtener_grado(red, nodo) for nodo in red.vertices()]
grado_promedio = sum(grados) / len(grados) if grados else 0
grado_maximo = max(grados) if grados else 0

print(f"   • Nodos totales: {total_nodos}")
print(f"   • Aristas totales: {total_aristas}")
print(f"   • Grado promedio: {grado_promedio:.2f}")
print(f"   • Grado máximo: {grado_maximo}")
print(f"   • Densidad de conexión: {(2 * total_aristas) / (total_nodos * (total_nodos - 1)):.3f}")

# Estimación de robustez
if grado_promedio > 3:
    print(f"   ✅ Red robusta (grado promedio alto)")
elif grado_promedio > 2:
    print(f"   ⚠️ Red moderadamente robusta")
else:
    print(f"   ❌ Red frágil (baja conectividad)")

print("=" * 45)
```

---

## Ejemplo 5: Optimización de Rutas por Roles

```python
from model import (GeneradorGrafoConectado, BuscadorNodos, CalculadorDistancias, 
                   ConsultorGrafo, RolNodo)

# Generar red especializada para análisis de rutas
generador = GeneradorGrafoConectado()
red = generador.crear_grafo_conectado(numero_nodos=18, probabilidad_arista=0.4)

print("⚡ OPTIMIZACIÓN DE RUTAS POR ROLES")
print("=" * 42)

# Seleccionar un nodo cliente como punto de partida
nodos_cliente = BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.CLIENTE)
if not nodos_cliente:
    print("❌ No hay nodos cliente para análisis")
    exit()

cliente_origen = nodos_cliente[0]
print(f"📱 Cliente origen: {cliente_origen.element()['nombre']}")

# Función para encontrar la mejor ruta multi-servicio
def encontrar_ruta_multi_servicio(red, origen, servicios_requeridos):
    """
    Encuentra la ruta más eficiente para visitar diferentes tipos de servicios
    """
    mejor_ruta = None
    mejor_distancia = float('inf')
    
    # Para cada permutación de servicios, encontrar la mejor ruta
    from itertools import permutations
    
    for orden_servicios in permutations(servicios_requeridos):
        nodo_actual = origen
        distancia_total = 0
        ruta_actual = [origen]
        ruta_valida = True
        
        for rol_servicio in orden_servicios:
            # Encontrar el nodo más cercano del tipo requerido
            resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                red, nodo_actual, rol_servicio
            )
            
            if resultado is None:
                ruta_valida = False
                break
                
            siguiente_nodo, distancia = resultado
            distancia_total += distancia
            
            # Obtener el camino detallado
            camino_resultado = CalculadorDistancias.encontrar_camino_mas_corto(
                red, nodo_actual, siguiente_nodo
            )
            
            if camino_resultado is None:
                ruta_valida = False
                break
                
            camino, _ = camino_resultado
            # Agregar nodos del camino (excluyendo el actual que ya está)
            ruta_actual.extend(camino[1:])
            nodo_actual = siguiente_nodo
        
        if ruta_valida and distancia_total < mejor_distancia:
            mejor_distancia = distancia_total
            mejor_ruta = {
                'ruta': ruta_actual,
                'distancia': distancia_total,
                'orden_servicios': orden_servicios
            }
    
    return mejor_ruta

# 1. Encontrar ruta óptima para servicios específicos
servicios_necesarios = [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA]
print(f"\n🎯 Optimizando ruta para servicios: {servicios_necesarios}")

ruta_optima = encontrar_ruta_multi_servicio(red, cliente_origen, servicios_necesarios)

if ruta_optima:
    print(f"\n✅ Ruta óptima encontrada:")
    print(f"   • Distancia total: {ruta_optima['distancia']:.2f}")
    print(f"   • Orden de servicios: {list(ruta_optima['orden_servicios'])}")
    print(f"   • Número de saltos: {len(ruta_optima['ruta']) - 1}")
    
    print(f"   • Ruta detallada:")
    for i, nodo in enumerate(ruta_optima['ruta']):
        elemento = nodo.element()
        if i == 0:
            print(f"     {i+1}. 🚀 INICIO: {elemento['nombre']} ({elemento['rol']})")
        else:
            # Verificar si este nodo proporciona un servicio requerido
            es_servicio = elemento['rol'] in servicios_necesarios
            icono = "🎯" if es_servicio else "⚡"
            tipo = "SERVICIO" if es_servicio else "TRÁNSITO"
            print(f"     {i+1}. {icono} {tipo}: {elemento['nombre']} ({elemento['rol']})")

# 2. Comparar con rutas directas
print(f"\n📊 Comparación con rutas directas:")

for rol_servicio in servicios_necesarios:
    resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
        red, cliente_origen, rol_servicio
    )
    
    if resultado:
        nodo, distancia = resultado
        print(f"   • Ruta directa a {rol_servicio}: {distancia:.2f}")
        print(f"     Nodo: {nodo.element()['nombre']}")

# 3. Análisis de alternativas
print(f"\n🔀 Análisis de alternativas:")

# Encontrar múltiples opciones para cada servicio
for rol_servicio in servicios_necesarios:
    opciones = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
        red, cliente_origen, rol_servicio, k=3
    )
    
    print(f"\n   {rol_servicio.upper()} - Top 3 opciones:")
    for i, (nodo, distancia) in enumerate(opciones, 1):
        elemento = nodo.element()
        print(f"     {i}. {elemento['nombre']}: distancia {distancia:.2f}")
        
        # Verificar conectividad con otros servicios
        conectividad_servicios = {}
        for otro_rol in servicios_necesarios:
            if otro_rol != rol_servicio:
                resultado_conectividad = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                    red, nodo, otro_rol
                )
                if resultado_conectividad:
                    _, dist_conectividad = resultado_conectividad
                    conectividad_servicios[otro_rol] = dist_conectividad
        
        if conectividad_servicios:
            print(f"        Conectividad: {conectividad_servicios}")

# 4. Métricas de eficiencia de la red
print(f"\n📈 Métricas de eficiencia:")

# Calcular distancia promedio entre todos los pares de nodos
distancias_promedio_por_rol = {}
for rol in RolNodo.todos_los_roles():
    nodos_rol = BuscadorNodos.buscar_nodos_por_rol(red, rol)
    if len(nodos_rol) > 0:
        distancias_desde_rol = []
        
        for nodo in nodos_rol:
            distancias, _ = CalculadorDistancias.dijkstra(red, nodo)
            distancias_validas = [d for d in distancias.values() if d != float('inf')]
            if distancias_validas:
                distancia_promedio = sum(distancias_validas) / len(distancias_validas)
                distancias_desde_rol.append(distancia_promedio)
        
        if distancias_desde_rol:
            promedio_rol = sum(distancias_desde_rol) / len(distancias_desde_rol)
            distancias_promedio_por_rol[rol] = promedio_rol

print(f"   Distancia promedio desde cada tipo de nodo:")
for rol, dist_prom in distancias_promedio_por_rol.items():
    print(f"     • {rol}: {dist_prom:.2f}")

# Identificar el rol más central
if distancias_promedio_por_rol:
    rol_mas_central = min(distancias_promedio_por_rol.items(), key=lambda x: x[1])
    print(f"   🎯 Rol más central: {rol_mas_central[0]} (distancia promedio: {rol_mas_central[1]:.2f})")

print("=" * 42)
```

---

## Ejemplo 6: Monitor de Red en Tiempo Real

```python
from model import (GeneradorGrafoConectado, ConsultorGrafo, BuscadorNodos, 
                   CalculadorDistancias, RolNodo)
import time
import random

class MonitorRed:
    """Simulador de monitoreo de red en tiempo real"""
    
    def __init__(self, red, generador):
        self.red = red
        self.generador = generador
        self.metricas_historicas = []
        self.alertas_activas = []
    
    def capturar_metricas(self):
        """Captura métricas actuales de la red"""
        timestamp = time.time()
        stats = self.generador.obtener_estadisticas_grafo(self.red)
        stats_roles = BuscadorNodos.obtener_estadisticas_roles(self.red)
        
        metricas = {
            'timestamp': timestamp,
            'conectividad': ConsultorGrafo.validar_conectividad(self.red),
            'total_nodos': stats['numero_vertices'],
            'total_aristas': stats['numero_aristas'],
            'densidad': stats['densidad'],
            'grado_promedio': stats['grado_promedio'],
            'estadisticas_roles': stats_roles
        }
        
        self.metricas_historicas.append(metricas)
        return metricas
    
    def verificar_salud_red(self, metricas):
        """Verifica la salud de la red y genera alertas"""
        alertas = []
        
        # Verificar conectividad
        if not metricas['conectividad']:
            alertas.append({
                'tipo': 'CRÍTICO',
                'mensaje': 'Red desconectada detectada',
                'timestamp': metricas['timestamp']
            })
        
        # Verificar densidad mínima
        if metricas['densidad'] < 0.1:
            alertas.append({
                'tipo': 'ADVERTENCIA',
                'mensaje': f'Densidad baja: {metricas["densidad"]:.3f}',
                'timestamp': metricas['timestamp']
            })
        
        # Verificar balance de roles
        stats_roles = metricas['estadisticas_roles']
        for rol, stats in stats_roles.items():
            if stats['cantidad'] == 0:
                alertas.append({
                    'tipo': 'CRÍTICO',
                    'mensaje': f'No hay nodos de tipo {rol}',
                    'timestamp': metricas['timestamp']
                })
            elif stats['grado_promedio'] < 1.0:
                alertas.append({
                    'tipo': 'ADVERTENCIA',
                    'mensaje': f'Conectividad baja en nodos {rol}: {stats["grado_promedio"]:.2f}',
                    'timestamp': metricas['timestamp']
                })
        
        return alertas
    
    def simular_fallo_nodo(self):
        """Simula el fallo de un nodo aleatorio"""
        nodos = list(self.red.vertices())
        if len(nodos) > 1:
            nodo_fallo = random.choice(nodos)
            nombre_nodo = nodo_fallo.element()['nombre']
            
            # Remover todas las aristas del nodo (simular desconexión)
            aristas_incidentes = list(self.red.incident_edges(nodo_fallo))
            for arista in aristas_incidentes:
                self.red.remove_edge(arista)
            
            return f"Nodo {nombre_nodo} desconectado"
        return None
    
    def generar_reporte(self):
        """Genera un reporte de estado de la red"""
        if not self.metricas_historicas:
            return "No hay métricas disponibles"
        
        metricas_actuales = self.metricas_historicas[-1]
        
        reporte = []
        reporte.append("📊 REPORTE DE ESTADO DE RED")
        reporte.append("=" * 40)
        reporte.append(f"Timestamp: {time.ctime(metricas_actuales['timestamp'])}")
        reporte.append(f"Estado: {'🟢 Conectada' if metricas_actuales['conectividad'] else '🔴 Desconectada'}")
        reporte.append(f"Nodos activos: {metricas_actuales['total_nodos']}")
        reporte.append(f"Aristas: {metricas_actuales['total_aristas']}")
        reporte.append(f"Densidad: {metricas_actuales['densidad']:.3f}")
        reporte.append(f"Grado promedio: {metricas_actuales['grado_promedio']:.2f}")
        
        reporte.append("\n🏷️ Estado por roles:")
        for rol, stats in metricas_actuales['estadisticas_roles'].items():
            estado = "🟢" if stats['cantidad'] > 0 and stats['grado_promedio'] > 1.0 else "🟡"
            reporte.append(f"  {estado} {rol}: {stats['cantidad']} nodos, "
                          f"grado prom: {stats['grado_promedio']:.2f}")
        
        if len(self.metricas_historicas) > 1:
            metricas_previas = self.metricas_historicas[-2]
            cambio_nodos = metricas_actuales['total_nodos'] - metricas_previas['total_nodos']
            cambio_aristas = metricas_actuales['total_aristas'] - metricas_previas['total_aristas']
            
            reporte.append("\n📈 Cambios desde última medición:")
            reporte.append(f"  Nodos: {cambio_nodos:+d}")
            reporte.append(f"  Aristas: {cambio_aristas:+d}")
        
        return "\n".join(reporte)

# Demostración del monitor
print("🔍 SIMULACIÓN DE MONITOREO DE RED")
print("=" * 45)

# Crear red inicial
generador = GeneradorGrafoConectado()
red_monitoreada = generador.crear_grafo_conectado(numero_nodos=15, probabilidad_arista=0.4)

# Inicializar monitor
monitor = MonitorRed(red_monitoreada, generador)

# Simular monitoreo en múltiples intervalos
for ciclo in range(4):
    print(f"\n🔄 CICLO DE MONITOREO {ciclo + 1}")
    print("-" * 30)
    
    # Capturar métricas
    metricas = monitor.capturar_metricas()
    
    # Verificar salud
    alertas = monitor.verificar_salud_red(metricas)
    
    # Mostrar alertas si las hay
    if alertas:
        print("🚨 ALERTAS DETECTADAS:")
        for alerta in alertas:
            print(f"  [{alerta['tipo']}] {alerta['mensaje']}")
    else:
        print("✅ Red operando normalmente")
    
    # Generar reporte
    reporte = monitor.generar_reporte()
    print(f"\n{reporte}")
    
    # Simular fallo en algunos ciclos
    if ciclo == 2:
        print(f"\n⚠️ SIMULANDO FALLO...")
        fallo = monitor.simular_fallo_nodo()
        if fallo:
            print(f"  {fallo}")
    
    if ciclo < 3:
        print("\n⏳ Esperando siguiente ciclo...")
        time.sleep(1)  # Pausa breve para simular tiempo real

print("\n🏁 Monitoreo completado")
print("=" * 45)
```

---

## Ejemplo 7: Análisis de Rendimiento y Escalabilidad

```python
import time
import statistics
from model import (GeneradorGrafoConectado, ConsultorGrafo, BuscadorNodos, 
                   CalculadorDistancias, RolNodo)

def benchmark_utilidades(tamaños_red):
    """Benchmark de utilidades para diferentes tamaños de red"""
    
    resultados = []
    
    print("⚡ BENCHMARK DE UTILIDADES DE GRAFOS")
    print("=" * 60)
    print(f"{'Nodos':<8} {'Conectividad':<12} {'Búsqueda':<10} {'Dijkstra':<10} {'Stats':<8}")
    print("-" * 60)
    
    for tamaño in tamaños_red:
        # Generar red
        generador = GeneradorGrafoConectado()
        red = generador.crear_grafo_conectado(numero_nodos=tamaño, probabilidad_arista=0.3)
        
        # Seleccionar nodo para pruebas
        nodos = list(red.vertices())
        nodo_origen = nodos[0] if nodos else None
        
        tiempos = {}
        
        # 1. Benchmark verificación de conectividad
        inicio = time.time()
        for _ in range(5):  # Ejecutar 5 veces para promedio
            ConsultorGrafo.validar_conectividad(red)
        tiempos['conectividad'] = (time.time() - inicio) / 5
        
        # 2. Benchmark búsqueda por rol
        inicio = time.time()
        for _ in range(10):
            BuscadorNodos.buscar_nodos_por_rol(red, RolNodo.ALMACENAMIENTO)
        tiempos['busqueda'] = (time.time() - inicio) / 10
        
        # 3. Benchmark Dijkstra
        if nodo_origen:
            inicio = time.time()
            for _ in range(3):
                CalculadorDistancias.dijkstra(red, nodo_origen)
            tiempos['dijkstra'] = (time.time() - inicio) / 3
        else:
            tiempos['dijkstra'] = 0
        
        # 4. Benchmark estadísticas
        inicio = time.time()
        for _ in range(5):
            BuscadorNodos.obtener_estadisticas_roles(red)
        tiempos['estadisticas'] = (time.time() - inicio) / 5
        
        # Guardar resultados
        resultado = {
            'tamaño': tamaño,
            'tiempos': tiempos
        }
        resultados.append(resultado)
        
        # Mostrar resultados
        print(f"{tamaño:<8} "
              f"{tiempos['conectividad']:<12.4f} "
              f"{tiempos['busqueda']:<10.4f} "
              f"{tiempos['dijkstra']:<10.4f} "
              f"{tiempos['estadisticas']:<8.4f}")
    
    print("=" * 60)
    
    # Análisis de escalabilidad
    print("\n📈 ANÁLISIS DE ESCALABILIDAD")
    for i in range(1, len(resultados)):
        anterior = resultados[i-1]
        actual = resultados[i]
        
        factor_tamaño = actual['tamaño'] / anterior['tamaño']
        
        print(f"\n{anterior['tamaño']} → {actual['tamaño']} nodos (factor {factor_tamaño:.1f}x):")
        
        for operacion in ['conectividad', 'busqueda', 'dijkstra', 'estadisticas']:
            if anterior['tiempos'][operacion] > 0:
                factor_tiempo = actual['tiempos'][operacion] / anterior['tiempos'][operacion]
                eficiencia = factor_tamaño / factor_tiempo
                print(f"  • {operacion}: {factor_tiempo:.2f}x tiempo "
                      f"(eficiencia: {eficiencia:.2f})")
    
    return resultados

def analizar_patron_busqueda(red):
    """Analiza patrones de búsqueda en una red"""
    
    print("\n🔍 ANÁLISIS DE PATRONES DE BÚSQUEDA")
    print("=" * 45)
    
    # Obtener todos los nodos por rol
    nodos_por_rol = {}
    for rol in RolNodo.todos_los_roles():
        nodos_por_rol[rol] = BuscadorNodos.buscar_nodos_por_rol(red, rol)
    
    print(f"Distribución de nodos:")
    for rol, nodos in nodos_por_rol.items():
        print(f"  • {rol}: {len(nodos)} nodos")
    
    # Análisis de accesibilidad
    print(f"\n📊 Análisis de accesibilidad:")
    
    for rol_origen in RolNodo.todos_los_roles():
        nodos_origen = nodos_por_rol[rol_origen]
        if not nodos_origen:
            continue
            
        print(f"\nDesde nodos {rol_origen}:")
        
        for rol_destino in RolNodo.todos_los_roles():
            if rol_destino == rol_origen:
                continue
                
            distancias_encontradas = []
            
            # Muestrar algunos ejemplos
            for i, nodo_origen in enumerate(nodos_origen[:3]):  # Solo primeros 3
                resultado = BuscadorNodos.buscar_nodo_mas_cercano_por_rol(
                    red, nodo_origen, rol_destino
                )
                
                if resultado:
                    _, distancia = resultado
                    distancias_encontradas.append(distancia)
            
            if distancias_encontradas:
                dist_promedio = statistics.mean(distancias_encontradas)
                dist_min = min(distancias_encontradas)
                dist_max = max(distancias_encontradas)
                
                print(f"  → {rol_destino}: "
                      f"distancia promedio {dist_promedio:.2f} "
                      f"(rango: {dist_min:.2f}-{dist_max:.2f})")
            else:
                print(f"  → {rol_destino}: no accesible")

def test_casos_extremos():
    """Prueba el comportamiento en casos extremos"""
    
    print("\n🧪 PRUEBAS DE CASOS EXTREMOS")
    print("=" * 40)
    
    # Caso 1: Red muy pequeña (1 nodo)
    print("🔬 Caso 1: Red de 1 nodo")
    generador = GeneradorGrafoConectado()
    red_minima = generador.crear_grafo_conectado(numero_nodos=1)
    
    nodo_unico = list(red_minima.vertices())[0]
    conectada = ConsultorGrafo.validar_conectividad(red_minima)
    componentes = ConsultorGrafo.obtener_componentes_conexas(red_minima)
    
    print(f"  • Conectada: {conectada}")
    print(f"  • Componentes: {len(componentes)}")
    print(f"  • Rol del nodo: {nodo_unico.element()['rol']}")
    
    # Caso 2: Red lineal (muy baja conectividad)
    print("\n🔬 Caso 2: Red con baja conectividad")
    red_baja = generador.crear_grafo_conectado(numero_nodos=10, probabilidad_arista=0.0)
    
    stats = generador.obtener_estadisticas_grafo(red_baja)
    print(f"  • Nodos: {stats['numero_vertices']}")
    print(f"  • Aristas: {stats['numero_aristas']}")
    print(f"  • Densidad: {stats['densidad']}")
    
    # Probar búsquedas en red de baja conectividad
    nodos = list(red_baja.vertices())
    if len(nodos) >= 2:
        nodo_origen = nodos[0]
        nodo_destino = nodos[-1]
        
        resultado = CalculadorDistancias.encontrar_camino_mas_corto(
            red_baja, nodo_origen, nodo_destino
        )
        
        if resultado:
            camino, distancia = resultado
            print(f"  • Camino más largo en red mínima: {distancia:.2f} "
                  f"({len(camino)} saltos)")
        else:
            print(f"  • No hay camino entre extremos")
    
    # Caso 3: Red muy densa
    print("\n🔬 Caso 3: Red muy densa")
    red_densa = generador.crear_grafo_conectado(numero_nodos=8, probabilidad_arista=0.9)
    
    stats_densa = generador.obtener_estadisticas_grafo(red_densa)
    print(f"  • Densidad: {stats_densa['densidad']}")
    print(f"  • Grado promedio: {stats_densa['grado_promedio']}")
    
    # Medir tiempo de Dijkstra en red densa
    nodo_test = list(red_densa.vertices())[0]
    inicio = time.time()
    distancias, _ = CalculadorDistancias.dijkstra(red_densa, nodo_test)
    tiempo_dijkstra = time.time() - inicio
    
    distancias_validas = [d for d in distancias.values() if d != float('inf')]
    if distancias_validas:
        dist_promedio = statistics.mean(distancias_validas)
        print(f"  • Distancia promedio: {dist_promedio:.2f}")
        print(f"  • Tiempo Dijkstra: {tiempo_dijkstra:.4f}s")

# Ejecutar análisis completo
if __name__ == "__main__":
    # Benchmark de rendimiento
    tamaños_test = [10, 20, 50, 100]
    resultados_benchmark = benchmark_utilidades(tamaños_test)
    
    # Análisis de una red específica
    generador = GeneradorGrafoConectado()
    red_analisis = generador.crear_grafo_conectado(numero_nodos=25, probabilidad_arista=0.4)
    analizar_patron_busqueda(red_analisis)
    
    # Casos extremos
    test_casos_extremos()
    
    print("\n🏁 Análisis completado")
```

---

## Notas de Implementación

### Patrones de Uso Recomendados

1. **Siempre verificar conectividad** antes de realizar búsquedas complejas
2. **Usar análisis estadístico** para entender la topología de la red
3. **Implementar caché** para consultas repetidas en redes grandes
4. **Monitorear rendimiento** en operaciones sobre redes de más de 100 nodos

### Optimizaciones Aplicadas

- **Dijkstra optimizado**: Usa heap binario para eficiencia O((V+E) log V)
- **Búsquedas por rol**: Filtrado directo sobre vértices sin recorridos innecesarios
- **Verificación de conectividad**: DFS temprana que se detiene al encontrar desconexión
- **Estadísticas incrementales**: Calcula múltiples métricas en una sola pasada

### Consideraciones de Escalabilidad

| Operación | Complejidad | Recomendación para redes grandes |
|-----------|-------------|----------------------------------|
| Validar conectividad | O(V + E) | Usar para validación periódica |
| Búsqueda por rol | O(V) | Considerar índices para múltiples consultas |
| Dijkstra | O((V + E) log V) | Cachear resultados para orígenes frecuentes |
| Estadísticas de roles | O(V + E) | Recalcular solo cuando la red cambie |

### Casos de Uso Principales

1. **Simulación de redes**: Validación y análisis de topologías generadas
2. **Optimización de rutas**: Encontrar caminos eficientes entre servicios
3. **Monitoreo de infraestructura**: Detectar problemas de conectividad
4. **Análisis de rendimiento**: Evaluación de eficiencia de red
5. **Research y testing**: Generación de datasets para investigación

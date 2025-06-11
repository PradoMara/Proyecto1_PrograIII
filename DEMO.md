# 🚁 Simulación Logística de Drones - Correos Chile

## ✅ Estado del Proyecto: COMPLETADO

### 📋 Características Implementadas

✅ **Gestión dinámica de rutas**
- Algoritmos BFS, DFS y Topological Sort
- Consideración de limitaciones de batería (50 unidades)
- Recarga automática en estaciones de carga
- Validación de conectividad del grafo

✅ **Simulación funcional**
- Soporte de 10-150 nodos
- Hasta 300 aristas y 500 órdenes
- Generación de grafos conexos garantizada
- Distribución automática: 20% almacenamiento, 20% recarga, 60% clientes

✅ **Análisis estadístico**
- Árbol AVL para registro de rutas
- Análisis de frecuencia de uso
- Estadísticas de nodos más visitados
- Métricas de rendimiento del sistema

✅ **Garantía de conectividad**
- Algoritmo de árbol de expansión mínima
- Verificación de conectividad con BFS
- Prevención de nodos aislados

✅ **Visualización y Dashboard completo**
- **🔄 Run Simulation**: Configuración e inicio de simulación
- **🌍 Explore Network**: Visualización de red y cálculo de rutas
- **🌐 Clients & Orders**: Gestión de clientes y órdenes
- **📋 Route Analytics**: Análisis AVL y rutas frecuentes
- **📈 General Statistics**: Estadísticas generales y métricas

### 🛠️ Tecnologías Utilizadas

- **Python 3.12+**
- **Streamlit**: Interfaz web interactiva
- **NetworkX**: Manipulación y visualización de grafos
- **Matplotlib**: Gráficos y visualizaciones
- **Plotly**: Gráficos interactivos
- **Pandas**: Manipulación de datos

### 🗂️ Estructura del Proyecto

```
📁 testeo/
├── 📄 app.py                 # Aplicación principal Streamlit
├── 📄 run.py                 # Script de ejecución automática
├── 📄 start.sh               # Script bash alternativo
├── 📄 requirements.txt       # Dependencias
├── 📄 README.md              # Documentación
├── 📄 DEMO.md                # Este archivo de demostración
├── 📁 models/                # Modelos de datos
│   ├── 📄 node.py           # Clases Node, Order, Client
│   └── 📄 graph.py          # Clase Graph principal
├── 📁 algorithms/            # Algoritmos de búsqueda
│   └── 📄 pathfinding.py    # BFS, DFS, Topological Sort
├── 📁 data_structures/       # Estructuras de datos
│   └── 📄 avl_tree.py       # Implementación de árbol AVL
└── 📁 utils/                 # Utilidades
    ├── 📄 simulation.py     # Sistema de simulación
    └── 📄 visualization.py  # Herramientas de visualización
```

### 🚀 Cómo Ejecutar

1. **Instalación de dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación:**
   ```bash
   python run.py
   ```

3. **Abrir en el navegador:** La aplicación se abrirá automáticamente o ir a la URL mostrada

### 📊 Funcionalidades Principales

#### 1. Simulación de Red
- Configuración de nodos (10-150)
- Configuración de aristas (mínimo para conectividad)
- Generación de órdenes aleatorias
- Validación de parámetros en tiempo real

#### 2. Exploración de Red
- Visualización gráfica de la red
- Cálculo de rutas entre nodos
- Consideración automática de recarga
- Múltiples algoritmos de búsqueda

#### 3. Gestión de Órdenes
- Registro automático de clientes
- Seguimiento de órdenes en tiempo real
- Estados de entrega
- Historial completo

#### 4. Análisis Avanzado
- Árbol AVL para rutas frecuentes
- Visualización de estructura balanceada
- Análisis de frecuencia de uso
- Optimización basada en historial

#### 5. Estadísticas Completas
- Métricas de rendimiento
- Análisis de visitas por tipo de nodo
- Gráficos interactivos
- Tableros de control

### 🔋 Sistema de Batería

- **Autonomía máxima:** 50 unidades
- **Recarga automática:** En estaciones de carga
- **Validación de rutas:** Considera limitaciones energéticas
- **Rutas alternativas:** Inclusión automática de estaciones de recarga

### 🎯 Algoritmos Implementados

1. **BFS (Breadth-First Search)**
   - Búsqueda en anchura con consideración de batería
   - Encuentra rutas más cortas

2. **DFS (Depth-First Search)**
   - Búsqueda en profundidad optimizada
   - Exploración exhaustiva de rutas

3. **Topological Sort Modificado**
   - Priorización por tipos de nodos
   - Optimización de orden de visita

### 📈 Características Técnicas

- **Escalabilidad:** Hasta 150 nodos, 300 aristas, 500 órdenes
- **Rendimiento:** Estructuras optimizadas (AVL, grafos, mapas)
- **Robustez:** Validación completa de entrada
- **Usabilidad:** Interfaz intuitiva y responsiva

### 🎨 Interfaz de Usuario

- **Diseño moderno:** Interface limpia y profesional
- **Navegación intuitiva:** Pestañas organizadas funcionalmente
- **Visualizaciones ricas:** Gráficos interactivos y mapas de red
- **Feedback en tiempo real:** Mensajes de estado y progreso

---

## 🏆 Proyecto Completo y Funcional

Este proyecto implementa completamente todos los requerimientos especificados para la simulación logística de drones de Correos Chile, proporcionando una solución robusta, escalable y fácil de usar.

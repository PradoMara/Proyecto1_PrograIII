# Simulación Logística de Drones - Correos Chile

Este proyecto implementa una simulación completa de una red de drones autónomos para Correos Chile, incluyendo centros de distribución, estaciones de carga y optimización de rutas.

## Características

- Gestión dinámica de rutas con consideración de batería
- Análisis estadístico usando estructuras AVL
- Visualización interactiva con Streamlit
- Soporte para hasta 150 nodos y 500 órdenes
- Algoritmos BFS, DFS y Topological Sort para búsqueda de caminos

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

Tienes tres formas de ejecutar la aplicación:

### Opción 1: Usar el script Python (Recomendado)
```bash
python run.py
```

### Opción 2: Usar el script bash
```bash
./start.sh
```

### Opción 3: Ejecutar Streamlit directamente
```bash
streamlit run app.py
```

## Estructura del Proyecto

- `app.py` - Aplicación principal Streamlit
- `models/` - Clases principales (Graph, Node, Order, etc.)
- `algorithms/` - Implementaciones de algoritmos de búsqueda
- `utils/` - Utilidades y helpers
- `data_structures/` - Implementación del árbol AVL

## Parámetros de Simulación

- Nodos máximos: 150
- Roles: 20% Almacenamiento, 20% Recarga, 60% Cliente
- Autonomía máxima del dron: 50 unidades

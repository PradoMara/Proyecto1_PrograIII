# Proyecto 1 - Programación III
## Generador de Grafos Conectados - Sistema Base

Este proyecto implementa un **sistema base** de generación de grafos aleatorios conectados con roles asignados. El sistema está diseñado para ser modular y extensible, permitiendo que otros desarrolladores implementen sus propias simulaciones específicas.


### Estructura del Proyecto

```
Proyecto1_PrograIII/
├── model/           # 🏗️ Implementación principal
│   ├── graph_base.py         # TDA Grafo base
│   ├── vertex_base.py        # TDA Vértice
│   ├── edge_base.py          # TDA Arista
│   ├── generador_grafo.py    # ⭐ Generador principal
│   └── utilidades_grafo.py   # ⭐ Utilidades de análisis
├── tests/           # 🧪 Suite de pruebas completa
│   ├── unit/                 # Pruebas unitarias (55 tests)
│   ├── integration/          # Pruebas de integración (24 tests)
│   └── run_tests.py          # Script de ejecución
├── docs/            # 📚 Documentación completa
│   ├── guides/               # Guías de usuario
│   ├── examples/             # Ejemplos de uso
│   └── api/                  # Documentación de API
├── domain/          # Entidades de dominio (para extensiones futuras)
├── sim/             # Módulo de simulación base
├── tda/             # Tipos de datos abstractos adicionales
└── visual/          # Visualización (por implementar)
```

### 🚀 Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
python tests/run_tests.py

# Solo pruebas unitarias
python tests/run_tests.py --unit

# Solo pruebas de integracion  
python tests/run_tests.py --integration

# Con salida detallada
python tests/run_tests.py --verbose
```

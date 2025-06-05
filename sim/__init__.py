
# Re-exportar desde model para compatibilidad temporal
from model import GeneradorGrafoConectado, RolNodo, ConfiguracionRoles
from model import ConsultorGrafo, CalculadorDistancias, BuscadorNodos

__all__ = [
    # Clases principales (ahora en model/)
    'GeneradorGrafoConectado',
    'RolNodo', 
    'ConfiguracionRoles',
    'ConsultorGrafo',
    'CalculadorDistancias', 
    'BuscadorNodos'
]

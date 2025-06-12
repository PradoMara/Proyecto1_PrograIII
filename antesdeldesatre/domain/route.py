from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class RutaInfo:
    ruta_id: str
    origen: str
    destino: str
    camino: List[str]  # Lista de nodos en el camino
    distancia: float
    frecuencia_uso: int
    ultimo_uso: datetime
    tiempo_promedio: float
    metadatos: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
            return {
            'ruta_id': self.ruta_id,
            'origen': self.origen,
            'destino': self.destino,
            'camino': self.camino,
            'distancia': self.distancia,
            'frecuencia_uso': self.frecuencia_uso,
            'ultimo_uso': self.ultimo_uso.isoformat(),
            'tiempo_promedio': self.tiempo_promedio,
            'metadatos': self.metadatos
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RutaInfo':
            return cls(
            ruta_id=data['ruta_id'],
            origen=data['origen'],
            destino=data['destino'],
            camino=data['camino'],
            distancia=data['distancia'],
            frecuencia_uso=data['frecuencia_uso'],
            ultimo_uso=datetime.fromisoformat(data['ultimo_uso']),
            tiempo_promedio=data['tiempo_promedio'],
            metadatos=data.get('metadatos', {})
        )
    
    def incrementar_uso(self, incremento: int = 1) -> None:
        
        self.frecuencia_uso += incremento
        self.ultimo_uso = datetime.now()
    
    def actualizar_tiempo_promedio(self, nuevo_tiempo: float) -> None:
        
        if self.frecuencia_uso == 1:
            self.tiempo_promedio = nuevo_tiempo
        else:
            # Media móvil simple
            factor = 1.0 / self.frecuencia_uso
            self.tiempo_promedio = (self.tiempo_promedio * (1 - factor) + 
                                  nuevo_tiempo * factor)
    
    def agregar_metadato(self, clave: str, valor: Any) -> None:
        
        self.metadatos[clave] = valor
    
    def __str__(self) -> str:
        
        return (f"Ruta({self.ruta_id}: {self.origen}→{self.destino}, "
                f"dist={self.distancia:.2f}, usos={self.frecuencia_uso})")
    
    def __repr__(self) -> str:
        
        return self.__str__()


class NodoAVLRuta:
   
    def __init__(self, ruta_info: RutaInfo):
       
        self.ruta_info = ruta_info
        self.key = ruta_info.ruta_id  # Clave para búsqueda
        self.left: Optional['NodoAVLRuta'] = None
        self.right: Optional['NodoAVLRuta'] = None
        self.height = 0
    
    def actualizar_altura(self) -> None:
        # Actualiza la altura del nodo basada en sus hijos
        left_height = -1 if self.left is None else self.left.height
        right_height = -1 if self.right is None else self.right.height
        self.height = 1 + max(left_height, right_height)
    
    def factor_balance(self) -> int:
      
        left_height = -1 if self.left is None else self.left.height
        right_height = -1 if self.right is None else self.right.height
        return left_height - right_height
    
    def es_hoja(self) -> bool:
       
        return self.left is None and self.right is None
    
    def tiene_un_hijo(self) -> bool:
       
        return (self.left is None) != (self.right is None)
    
    def tiene_dos_hijos(self) -> bool:
        
        return self.left is not None and self.right is not None
    
    def __str__(self) -> str:
        
        return (f"NodoAVL({self.key}: {self.ruta_info.origen}→"
                f"{self.ruta_info.destino}, usos={self.ruta_info.frecuencia_uso}, "
                f"h={self.height})")
    
    def __repr__(self) -> str:
      
        return self.__str__()


# ==================== FUNCIONES DE UTILIDAD PARA RUTAS ====================

def crear_ruta_desde_camino(ruta_id: str, camino: List[str], distancia: float,
                           metadatos: Optional[Dict[str, Any]] = None) -> RutaInfo:

    if len(camino) < 2:
        raise ValueError("El camino debe tener al menos 2 nodos (origen y destino)")
    
    return RutaInfo(
        ruta_id=ruta_id,
        origen=camino[0],
        destino=camino[-1],
        camino=camino,
        distancia=distancia,
        frecuencia_uso=0,
        ultimo_uso=datetime.now(),
        tiempo_promedio=0.0,
        metadatos=metadatos or {}
    )


def generar_id_ruta(origen: str, destino: str, indice: int = 0) -> str:
    
    if indice == 0:
        return f"ruta_{origen}_{destino}"
    else:
        return f"ruta_{origen}_{destino}_{indice}"


def crear_ruta_desde_vertices(vertices: List[Any], distancia: float,
                             metadatos: Optional[Dict[str, Any]] = None) -> RutaInfo:
    
    if not vertices or len(vertices) < 2:
        raise ValueError("Se requieren al menos 2 vertices para crear una ruta")
    
    # Extraer IDs de los vertices (asumiendo que tienen atributo 'id')
    camino = [str(vertex.id) for vertex in vertices]
    origen = camino[0]
    destino = camino[-1]
    
    # Generar ID único para la ruta
    ruta_id = generar_id_ruta(origen, destino)
    
    return crear_ruta_desde_camino(ruta_id, camino, distancia, metadatos)


def filtrar_rutas_por_frecuencia(rutas: List[RutaInfo], 
                                min_frecuencia: int = 1) -> List[RutaInfo]:
   
    return [ruta for ruta in rutas if ruta.frecuencia_uso >= min_frecuencia]


def agrupar_rutas_por_origen_destino(rutas: List[RutaInfo]) -> Dict[Tuple[str, str], List[RutaInfo]]:
   
    grupos = {}
    for ruta in rutas:
        clave = (ruta.origen, ruta.destino)
        if clave not in grupos:
            grupos[clave] = []
        grupos[clave].append(ruta)
    return grupos


def calcular_estadisticas_rutas(rutas: List[RutaInfo]) -> Dict[str, Any]:
    
    if not rutas:
        return {
            'total_rutas': 0,
            'total_usos': 0,
            'distancia_promedio': 0.0,
            'frecuencia_promedio': 0.0,
            'tiempo_promedio': 0.0
        }
    
    total_rutas = len(rutas)
    total_usos = sum(ruta.frecuencia_uso for ruta in rutas)
    distancia_promedio = sum(ruta.distancia for ruta in rutas) / total_rutas
    frecuencia_promedio = total_usos / total_rutas
    tiempo_promedio = sum(ruta.tiempo_promedio for ruta in rutas) / total_rutas
    
    return {
        'total_rutas': total_rutas,
        'total_usos': total_usos,
        'distancia_promedio': distancia_promedio,
        'frecuencia_promedio': frecuencia_promedio,
        'tiempo_promedio': tiempo_promedio,
        'distancia_minima': min(ruta.distancia for ruta in rutas),
        'distancia_maxima': max(ruta.distancia for ruta in rutas),
        'frecuencia_maxima': max(ruta.frecuencia_uso for ruta in rutas)
    }

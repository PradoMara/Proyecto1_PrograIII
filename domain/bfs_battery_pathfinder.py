from typing import List, Tuple, Dict, Set, Optional, Deque
from collections import deque
from dataclasses import dataclass
from enum import Enum

from .drone import Dron
from .charging_station import EstacionRecarga, TipoRecarga
from .battery_route_validator import ValidadorRutasPorBateria, ResultadoValidacion


class EstrategiaBusqueda(Enum):
    RUTA_MAS_CORTA = "ruta_mas_corta"           # Prioriza distancia mínima
    MENOR_CONSUMO = "menor_consumo"             # Prioriza menor consumo de batería
    MENOS_RECARGAS = "menos_recargas"           # Minimiza paradas de recarga
    TIEMPO_MINIMO = "tiempo_minimo"             # Minimiza tiempo total incluyendo recargas


@dataclass
class EstadoNodo:
    ubicacion: str                              # Ubicación actual
    bateria_restante: float                     # Batería restante (porcentaje)
    ruta_recorrida: List[str]                   # Camino seguido hasta aquí
    estaciones_usadas: Set[str]                 # Estaciones de recarga utilizadas
    distancia_total: float                      # Distancia total recorrida
    consumo_total: float                        # Consumo total de batería
    tiempo_total: float                         # Tiempo total incluyendo recargas
    numero_recargas: int                        # Número de recargas realizadas
    
    def __hash__(self):
        # Hash para permitir uso en sets
        return hash((self.ubicacion, round(self.bateria_restante, 1)))
    
    def __eq__(self, other):
        # Igualdad para evitar estados duplicados
        if not isinstance(other, EstadoNodo):
            return False
        return (self.ubicacion == other.ubicacion and 
                abs(self.bateria_restante - other.bateria_restante) < 0.1)


@dataclass
class ResultadoBFS:
    exito: bool                                 # Si se encontró una ruta factible
    ruta_optima: List[str]                     # Ruta encontrada (vacía si no hay)
    estaciones_recarga: List[str]              # Estaciones de recarga necesarias
    distancia_total: float                     # Distancia total de la ruta
    consumo_bateria: float                     # Consumo total de batería
    tiempo_estimado: float                     # Tiempo total estimado
    numero_recargas: int                       # Número de recargas necesarias
    mensaje: str                               # Mensaje descriptivo del resultado
    nodos_explorados: int                      # Número de nodos explorados
    tiempo_busqueda: float                     # Tiempo de cómputo (segundos)


class BFSBatteryPathfinder:
    # Algoritmo BFS modificado para búsqueda de rutas con límite de batería.
    def __init__(self, validador: ValidadorRutasPorBateria):
        self.validador = validador
        self.grafo_conexiones: Dict[str, List[Tuple[str, float]]] = {}
        self.velocidad_promedio = 50.0  # km/h para cálculos de tiempo
        
    def agregar_conexion(self, origen: str, destino: str, distancia: float):
        if origen not in self.grafo_conexiones:
            self.grafo_conexiones[origen] = []
        if destino not in self.grafo_conexiones:
            self.grafo_conexiones[destino] = []
            
        self.grafo_conexiones[origen].append((destino, distancia))
        self.grafo_conexiones[destino].append((origen, distancia))
    
    def construir_grafo_desde_matriz(self, ubicaciones: List[str], 
                                   matriz_distancias: List[List[float]]):
        self.grafo_conexiones.clear()
        
        for i, origen in enumerate(ubicaciones):
            for j, destino in enumerate(ubicaciones):
                if i != j and matriz_distancias[i][j] > 0:
                    self.agregar_conexion(origen, destino, matriz_distancias[i][j])
    
    def encontrar_ruta_optima(self, dron: Dron, origen: str, destino: str,
                            estrategia: EstrategiaBusqueda = EstrategiaBusqueda.RUTA_MAS_CORTA,
                            max_nodos: int = 10000) -> ResultadoBFS:

        import time
        inicio_tiempo = time.time()
        margen_seguridad = 10.0
        # Validaciones iniciales
        if origen not in self.grafo_conexiones:
            return self._crear_resultado_error(
                f"Ubicación de origen '{origen}' no existe en el grafo", 0, 0.0
            )
        if destino not in self.grafo_conexiones:
            return self._crear_resultado_error(
                f"Ubicación de destino '{destino}' no existe en el grafo", 0, 0.0
            )
        if dron.obtener_porcentaje_bateria() < margen_seguridad:
            return self._crear_resultado_error(
                "La batería inicial del dron es insuficiente para iniciar el vuelo.", 0, 0.0
            )
        if origen == destino:
            return ResultadoBFS(
                exito=True,
                ruta_optima=[origen],
                estaciones_recarga=[],
                distancia_total=0.0,
                consumo_bateria=0.0,
                tiempo_estimado=0.0,
                numero_recargas=0,
                mensaje="Origen y destino son iguales",
                nodos_explorados=1,
                tiempo_busqueda=0.0
            )
        
        # Inicializar BFS
        estado_inicial = EstadoNodo(
            ubicacion=origen,
            bateria_restante=dron.obtener_porcentaje_bateria(),
            ruta_recorrida=[origen],
            estaciones_usadas=set(),
            distancia_total=0.0,
            consumo_total=0.0,
            tiempo_total=0.0,
            numero_recargas=0
        )
        
        cola: Deque[EstadoNodo] = deque([estado_inicial])
        visitados: Set[Tuple[str, int]] = set()
        mejor_resultado: Optional[EstadoNodo] = None
        nodos_explorados = 0
        
        while cola and nodos_explorados < max_nodos:
            estado_actual = cola.popleft()
            nodos_explorados += 1
            
            # Crear clave para evitar revisar estados similares
            clave_estado = (estado_actual.ubicacion, int(estado_actual.bateria_restante))
            if clave_estado in visitados:
                continue
            visitados.add(clave_estado)
            
            # ¿Llegamos al destino?
            if estado_actual.ubicacion == destino:
                if mejor_resultado is None or self._es_mejor_solucion(estado_actual, mejor_resultado, estrategia):
                    mejor_resultado = estado_actual
                continue
            
            # Explorar conexiones desde ubicación actual
            if estado_actual.ubicacion in self.grafo_conexiones:
                for ubicacion_vecina, distancia in self.grafo_conexiones[estado_actual.ubicacion]:
                    nuevo_estado = self._generar_nuevo_estado(
                        dron, estado_actual, ubicacion_vecina, distancia
                    )
                    
                    if nuevo_estado and self._es_estado_valido(nuevo_estado):
                        cola.append(nuevo_estado)
        
        tiempo_busqueda = time.time() - inicio_tiempo
        
        if mejor_resultado:
            return self._crear_resultado_exitoso(mejor_resultado, nodos_explorados, tiempo_busqueda)
        else:
            return self._crear_resultado_error(
                "No se encontró ruta factible con la batería disponible", 
                nodos_explorados, tiempo_busqueda            )
    
    def _generar_nuevo_estado(self, dron: Dron, estado_actual: EstadoNodo, 
                            destino_vecino: str, distancia: float) -> Optional[EstadoNodo]:
        """
        Genera un nuevo estado explorando una conexión vecina.
        Maneja automáticamente las recargas cuando sea necesario.
        """
        # Calcular consumo de batería para este segmento
        consumo_vuelo = dron.calcular_consumo_vuelo(distancia)
        consumo_porcentaje = (consumo_vuelo / dron.bateria_maxima) * 100
        
        # Verificar si necesita recarga antes de este segmento
        bateria_tras_vuelo = estado_actual.bateria_restante - consumo_porcentaje
        margen_seguridad = 10.0  # 10% de margen mínimo
        
        # Si la batería inicial ya es menor al margen y no hay estaciones, no es válido
        if estado_actual.bateria_restante < margen_seguridad:
            estacion_cercana = self._encontrar_estacion_mas_cercana(estado_actual.ubicacion)
            es_estacion_destino = self._es_estacion_recarga(destino_vecino)
            if not estacion_cercana and not es_estacion_destino:
                return None
        
        nueva_bateria = estado_actual.bateria_restante
        nuevo_tiempo = estado_actual.tiempo_total
        nuevas_recargas = estado_actual.numero_recargas
        nuevas_estaciones = estado_actual.estaciones_usadas.copy()
        
        # Verificar si el destino es una estación de recarga
        es_estacion_destino = self._es_estacion_recarga(destino_vecino)
        
        # Si la batería no es suficiente para el vuelo
        if bateria_tras_vuelo < margen_seguridad:
            # Opción 1: Si el destino es una estación, podemos llegar y recargar ahí
            if es_estacion_destino and estado_actual.bateria_restante >= consumo_porcentaje:
                # Podemos llegar a la estación y recargar
                nueva_bateria = 100.0  # Recarga completa en el destino
                nuevo_tiempo += 0.5  # 30 minutos de recarga
                nuevas_recargas += 1
                nuevas_estaciones.add(destino_vecino)
            else:
                # Opción 2: Buscar estación cercana en la ubicación actual
                estacion_cercana = self._encontrar_estacion_mas_cercana(estado_actual.ubicacion)
                if estacion_cercana and estacion_cercana not in nuevas_estaciones:
                    # Recargar en la estación cercana antes del vuelo
                    nueva_bateria = 100.0
                    nuevo_tiempo += 0.5  # 30 minutos de recarga
                    nuevas_recargas += 1
                    nuevas_estaciones.add(estacion_cercana)
                    # Verificar si ahora puede hacer el vuelo
                    if nueva_bateria - consumo_porcentaje < margen_seguridad:
                        return None  # Aún no es factible
                else:
                    # No hay estaciones disponibles
                    return None
        
        # Calcular batería final después del vuelo
        bateria_final = nueva_bateria - consumo_porcentaje
        
        # Si llegamos a una estación y tenemos batería baja, recargar
        if (es_estacion_destino and bateria_final < 80.0 and 
            destino_vecino not in nuevas_estaciones):
            bateria_final = 100.0
            nuevo_tiempo += 0.5  # 30 minutos de recarga
            nuevas_recargas += 1
            nuevas_estaciones.add(destino_vecino)
        
        # Calcular tiempo de vuelo
        tiempo_vuelo = distancia / self.velocidad_promedio  # horas
        
        # Crear nuevo estado
        return EstadoNodo(
            ubicacion=destino_vecino,
            bateria_restante=bateria_final,
            ruta_recorrida=estado_actual.ruta_recorrida + [destino_vecino],
            estaciones_usadas=nuevas_estaciones,
            distancia_total=estado_actual.distancia_total + distancia,
            consumo_total=estado_actual.consumo_total + consumo_porcentaje,
            tiempo_total=nuevo_tiempo + tiempo_vuelo,
            numero_recargas=nuevas_recargas        )
    
    def _es_estacion_recarga(self, ubicacion: str) -> bool:
        """
        Verifica si una ubicación es una estación de recarga.
        """
        if hasattr(self.validador, 'estaciones_recarga'):
            return ubicacion in self.validador.estaciones_recarga
        return False
    
    def _encontrar_estacion_mas_cercana(self, ubicacion: str) -> Optional[str]:
        """
        Encuentra la estación de recarga más cercana a una ubicación.
        Implementación robusta que no depende del validador.
        """
        try:
            # Intentar usar el validador si tiene el método implementado
            if hasattr(self.validador, 'encontrar_estaciones_cercanas'):
                estaciones_cercanas = self.validador.encontrar_estaciones_cercanas(ubicacion, 50.0)
                if estaciones_cercanas:
                    return estaciones_cercanas[0][0]
        except Exception:
            pass
        
        # Método alternativo: buscar en el grafo las estaciones registradas
        min_distancia = float('inf')
        estacion_mas_cercana = None
        
        # Obtener estaciones del validador
        if hasattr(self.validador, 'estaciones_recarga'):
            for estacion_nodo in self.validador.estaciones_recarga.keys():
                # Buscar distancia en el grafo
                if (ubicacion in self.grafo_conexiones and 
                    any(destino == estacion_nodo for destino, _ in self.grafo_conexiones[ubicacion])):
                    # Estación conectada directamente
                    for destino, distancia in self.grafo_conexiones[ubicacion]:
                        if destino == estacion_nodo and distancia < min_distancia:
                            min_distancia = distancia
                            estacion_mas_cercana = estacion_nodo
        
        return estacion_mas_cercana
    
    def _es_estado_valido(self, estado: EstadoNodo) -> bool:
        # Verificar que la batería sea suficiente
        if estado.bateria_restante < 10.0:  # Mínimo 10%
            return False
        
        # Verificar que no haya bucles en la ruta
        if len(set(estado.ruta_recorrida)) != len(estado.ruta_recorrida):
            return False
        
        # Limitar longitud de ruta para evitar búsquedas infinitas
        if len(estado.ruta_recorrida) > 20:
            return False
        
        return True
    
    def _es_mejor_solucion(self, nuevo_estado: EstadoNodo, mejor_actual: EstadoNodo, 
                          estrategia: EstrategiaBusqueda) -> bool:

        if estrategia == EstrategiaBusqueda.RUTA_MAS_CORTA:
            return nuevo_estado.distancia_total < mejor_actual.distancia_total
        
        elif estrategia == EstrategiaBusqueda.MENOR_CONSUMO:
            return nuevo_estado.consumo_total < mejor_actual.consumo_total
        
        elif estrategia == EstrategiaBusqueda.MENOS_RECARGAS:
            if nuevo_estado.numero_recargas != mejor_actual.numero_recargas:
                return nuevo_estado.numero_recargas < mejor_actual.numero_recargas
            # En caso de empate, usar distancia como criterio secundario
            return nuevo_estado.distancia_total < mejor_actual.distancia_total
        
        elif estrategia == EstrategiaBusqueda.TIEMPO_MINIMO:
            return nuevo_estado.tiempo_total < mejor_actual.tiempo_total
        
        # Por defecto, usar distancia
        return nuevo_estado.distancia_total < mejor_actual.distancia_total
    
    def _crear_resultado_exitoso(self, estado: EstadoNodo, nodos_explorados: int, 
                               tiempo_busqueda: float) -> ResultadoBFS:
        return ResultadoBFS(
            exito=True,
            ruta_optima=estado.ruta_recorrida,
            estaciones_recarga=list(estado.estaciones_usadas),
            distancia_total=estado.distancia_total,
            consumo_bateria=estado.consumo_total,
            tiempo_estimado=estado.tiempo_total,
            numero_recargas=estado.numero_recargas,
            mensaje=f"Ruta encontrada con {len(estado.ruta_recorrida)} paradas",
            nodos_explorados=nodos_explorados,
            tiempo_busqueda=tiempo_busqueda
        )
    
    def _crear_resultado_error(self, mensaje: str, nodos_explorados: int, 
                             tiempo_busqueda: float) -> ResultadoBFS:
        return ResultadoBFS(
            exito=False,
            ruta_optima=[],
            estaciones_recarga=[],
            distancia_total=0.0,
            consumo_bateria=0.0,
            tiempo_estimado=0.0,
            numero_recargas=0,
            mensaje=mensaje,
            nodos_explorados=nodos_explorados,
            tiempo_busqueda=tiempo_busqueda
        )
    
    def obtener_estadisticas_grafo(self) -> Dict[str, any]:
        total_ubicaciones = len(self.grafo_conexiones)
        total_conexiones = sum(len(conexiones) for conexiones in self.grafo_conexiones.values()) // 2
        
        if total_ubicaciones == 0:
            return {
                "ubicaciones": 0,
                "conexiones": 0,
                "conectividad_promedio": 0.0,
                "distancia_promedio": 0.0
            }
        
        # Calcular conectividad promedio
        conectividad_promedio = total_conexiones * 2 / total_ubicaciones
        
        # Calcular distancia promedio
        distancias = []
        for conexiones in self.grafo_conexiones.values():
            distancias.extend([dist for _, dist in conexiones])
        
        distancia_promedio = sum(distancias) / len(distancias) if distancias else 0.0
        
        return {
            "ubicaciones": total_ubicaciones,
            "conexiones": total_conexiones,
            "conectividad_promedio": conectividad_promedio,
            "distancia_promedio": distancia_promedio
        }

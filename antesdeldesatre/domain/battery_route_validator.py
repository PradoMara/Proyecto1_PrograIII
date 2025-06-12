from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from .drone import Dron
from .charging_station import EstacionRecarga, TipoRecarga


@dataclass
class SegmentoRuta:
    """Representa un segmento de ruta entre dos nodos"""
    origen: str
    destino: str
    distancia: float
    consumo_bateria: float
    es_recarga: bool = False  # True si el destino es una estación de recarga
    
    def __str__(self) -> str:
        tipo = "RECARGA" if self.es_recarga else "NORMAL"
        return f"{self.origen} -> {self.destino} ({self.distancia:.1f}km, {self.consumo_bateria:.1f}%, {tipo})"


@dataclass
class ResultadoValidacion:
    """Resultado de la validación de una ruta"""
    es_factible: bool
    bateria_final: float
    segmentos_criticos: List[SegmentoRuta]  # Segmentos donde la batería está muy baja
    paradas_recarga_necesarias: List[str]   # Estaciones donde se debe recargar
    consumo_total: float
    distancia_total: float
    mensaje: str
    
    def __str__(self) -> str:
        estado = "FACTIBLE" if self.es_factible else "NO FACTIBLE"
        return (f"Validación: {estado}\n"
                f"Batería final: {self.bateria_final:.1f}%\n"
                f"Consumo total: {self.consumo_total:.1f}%\n"
                f"Distancia total: {self.distancia_total:.1f}km\n"
                f"Paradas de recarga: {len(self.paradas_recarga_necesarias)}\n"
                f"Mensaje: {self.mensaje}")


class ValidadorRutasPorBateria:
    """
    Validador de rutas considerando la batería del dron y estaciones de recarga
    """
    
    def __init__(self, margen_seguridad: float = 0.15):
        """
        Inicializa el validador
        
        Args:
            margen_seguridad: Porcentaje de batería que se debe mantener como reserva (0.15 = 15%)
        """
        self.margen_seguridad = margen_seguridad
        self.estaciones_recarga: Dict[str, EstacionRecarga] = {}
        self.distancias_nodos: Dict[Tuple[str, str], float] = {}
    
    def registrar_estacion_recarga(self, estacion: EstacionRecarga) -> None:
        """Registra una estación de recarga en el validador"""
        self.estaciones_recarga[estacion.nodo_id] = estacion
    
    def registrar_distancia(self, nodo_a: str, nodo_b: str, distancia: float) -> None:
        """Registra la distancia entre dos nodos"""
        self.distancias_nodos[(nodo_a, nodo_b)] = distancia
        self.distancias_nodos[(nodo_b, nodo_a)] = distancia  # Grafo no dirigido
    
    def obtener_distancia(self, nodo_a: str, nodo_b: str) -> Optional[float]:
        """Obtiene la distancia entre dos nodos"""
        return self.distancias_nodos.get((nodo_a, nodo_b))
    
    def es_estacion_recarga(self, nodo_id: str) -> bool:
        """Verifica si un nodo es una estación de recarga"""
        return nodo_id in self.estaciones_recarga
    
    def validar_ruta_simple(self, dron: Dron, ruta: List[str]) -> ResultadoValidacion:
        """
        Valida una ruta sin considerar recargas obligatorias
        
        Args:
            dron: El dron que realizará el viaje
            ruta: Lista de nodos que conforman la ruta
            
        Returns:
            ResultadoValidacion con el análisis de factibilidad
        """
        if len(ruta) < 2:
            return ResultadoValidacion(
                es_factible=False,
                bateria_final=dron.obtener_porcentaje_bateria(),
                segmentos_criticos=[],
                paradas_recarga_necesarias=[],
                consumo_total=0.0,
                distancia_total=0.0,
                mensaje="La ruta debe tener al menos 2 nodos"
            )
        
        segmentos = self._crear_segmentos_ruta(ruta)
        if not segmentos:
            return ResultadoValidacion(
                es_factible=False,
                bateria_final=dron.obtener_porcentaje_bateria(),
                segmentos_criticos=[],
                paradas_recarga_necesarias=[],
                consumo_total=0.0,
                distancia_total=0.0,
                mensaje="No se pudieron calcular las distancias de la ruta"
            )
        
        return self._simular_viaje(dron, segmentos, permitir_recarga=False)
    
    def validar_ruta_con_recarga(self, dron: Dron, ruta: List[str], 
                                tipo_recarga: TipoRecarga = TipoRecarga.NORMAL) -> ResultadoValidacion:
        """
        Valida una ruta considerando paradas de recarga cuando sea necesario
        
        Args:
            dron: El dron que realizará el viaje
            ruta: Lista de nodos que conforman la ruta
            tipo_recarga: Tipo de recarga a utilizar en las estaciones
            
        Returns:
            ResultadoValidacion con el análisis de factibilidad incluyendo recargas
        """
        if len(ruta) < 2:
            return ResultadoValidacion(
                es_factible=False,
                bateria_final=dron.obtener_porcentaje_bateria(),
                segmentos_criticos=[],
                paradas_recarga_necesarias=[],
                consumo_total=0.0,
                distancia_total=0.0,
                mensaje="La ruta debe tener al menos 2 nodos"
            )
        
        segmentos = self._crear_segmentos_ruta(ruta)
        if not segmentos:
            return ResultadoValidacion(
                es_factible=False,
                bateria_final=dron.obtener_porcentaje_bateria(),
                segmentos_criticos=[],
                paradas_recarga_necesarias=[],
                consumo_total=0.0,
                distancia_total=0.0,
                mensaje="No se pudieron calcular las distancias de la ruta"
            )
        
        return self._simular_viaje(dron, segmentos, permitir_recarga=True, tipo_recarga=tipo_recarga)
    
    def encontrar_estaciones_cercanas(self, nodo_id: str, radio_busqueda: float = 50.0) -> List[Tuple[str, float]]:
        """
        Encuentra estaciones de recarga cercanas a un nodo
        
        Args:
            nodo_id: ID del nodo de referencia
            radio_busqueda: Radio de búsqueda en kilómetros
            
        Returns:
            Lista de tuplas (estacion_id, distancia) ordenadas por distancia
        """
        estaciones_cercanas = []
        
        for estacion_id in self.estaciones_recarga:
            distancia = self.obtener_distancia(nodo_id, estacion_id)
            if distancia is not None and distancia <= radio_busqueda:
                estaciones_cercanas.append((estacion_id, distancia))
        
        # Ordenar por distancia
        estaciones_cercanas.sort(key=lambda x: x[1])
        return estaciones_cercanas
    
    def _crear_segmentos_ruta(self, ruta: List[str]) -> List[SegmentoRuta]:
        """Crea los segmentos de una ruta con las distancias correspondientes"""
        segmentos = []
        
        for i in range(len(ruta) - 1):
            origen = ruta[i]
            destino = ruta[i + 1]
            distancia = self.obtener_distancia(origen, destino)
            
            if distancia is None:
                return []  # No se puede calcular la ruta
            
            # Estimamos el consumo como 5% por kilómetro (valor por defecto)
            # En una implementación real, esto vendría del dron específico
            consumo_bateria = distancia * 5.0  # Porcentaje
            es_recarga = self.es_estacion_recarga(destino)
            
            segmentos.append(SegmentoRuta(
                origen=origen,
                destino=destino,
                distancia=distancia,
                consumo_bateria=consumo_bateria,
                es_recarga=es_recarga            ))
        
        return segmentos
    
    def _simular_viaje(self, dron: Dron, segmentos: List[SegmentoRuta], 
                      permitir_recarga: bool = True, 
                      tipo_recarga: TipoRecarga = TipoRecarga.NORMAL) -> ResultadoValidacion:
        """Simula el viaje del dron por los segmentos de la ruta"""
        bateria_actual = dron.obtener_porcentaje_bateria()
        bateria_minima_requerida = self.margen_seguridad * 100
        
        segmentos_criticos = []
        paradas_recarga = []
        consumo_total = 0.0
        distancia_total = 0.0
        
        for i, segmento in enumerate(segmentos):
            distancia_total += segmento.distancia
            
            # Calcular consumo real basado en el dron específico
            consumo_real = dron.calcular_consumo_vuelo(segmento.distancia)
            consumo_porcentaje = (consumo_real / dron.bateria_maxima) * 100
            
            # Verificar si se puede realizar este segmento
            if bateria_actual - consumo_porcentaje < bateria_minima_requerida:
                if not permitir_recarga:
                    # Sin recarga permitida, falla
                    return ResultadoValidacion(
                        es_factible=False,
                        bateria_final=bateria_actual,
                        segmentos_criticos=segmentos_criticos + [segmento],
                        paradas_recarga_necesarias=paradas_recarga,
                        consumo_total=consumo_total,
                        distancia_total=distancia_total,
                        mensaje=f"Batería insuficiente para el segmento {segmento.origen} -> {segmento.destino}"
                    )
                
                # Con recarga permitida, buscar estación cercana al origen
                estaciones_cercanas = self.encontrar_estaciones_cercanas(segmento.origen, radio_busqueda=50.0)
                
                if not estaciones_cercanas:
                    # No hay estaciones cercanas disponibles
                    return ResultadoValidacion(
                        es_factible=False,
                        bateria_final=bateria_actual,
                        segmentos_criticos=segmentos_criticos + [segmento],
                        paradas_recarga_necesarias=paradas_recarga,
                        consumo_total=consumo_total,
                        distancia_total=distancia_total,
                        mensaje=f"Sin estaciones de recarga disponibles cerca de {segmento.origen}"
                    )
                
                # Usar la estación más cercana para recargar
                estacion_id, distancia_estacion = estaciones_cercanas[0]
                paradas_recarga.append(estacion_id)
                bateria_actual = 100.0  # Recargar completamente
                
                # Ahora verificar si puede hacer el segmento después de recargar
                if bateria_actual - consumo_porcentaje < bateria_minima_requerida:
                    # Incluso con recarga completa no puede hacer el segmento
                    return ResultadoValidacion(
                        es_factible=False,
                        bateria_final=bateria_actual,
                        segmentos_criticos=segmentos_criticos + [segmento],
                        paradas_recarga_necesarias=paradas_recarga,
                        consumo_total=consumo_total,
                        distancia_total=distancia_total,
                        mensaje=f"Segmento {segmento.origen} -> {segmento.destino} imposible incluso con batería completa"
                    )
            
            # Realizar el segmento
            bateria_actual -= consumo_porcentaje
            consumo_total += consumo_porcentaje
            
            # Verificar si es un segmento crítico (batería baja)
            if bateria_actual < bateria_minima_requerida + 10:  # Dentro del 10% del margen
                segmentos_criticos.append(segmento)
            
            # Si llegamos a una estación de recarga y tenemos batería baja, recargar
            if (permitir_recarga and segmento.es_recarga and 
                bateria_actual < 80.0):  # Recargar si está por debajo del 80%
                
                if segmento.destino not in paradas_recarga:  # Evitar duplicados
                    paradas_recarga.append(segmento.destino)
                bateria_actual = 100.0  # Asumir recarga completa por simplicidad
        
        # Determinar el resultado final
        es_factible = bateria_actual >= bateria_minima_requerida
        mensaje = "Ruta factible"
        
        if not es_factible:
            mensaje = f"Batería final ({bateria_actual:.1f}%) por debajo del margen de seguridad"
        elif segmentos_criticos:
            mensaje = f"Ruta factible pero con {len(segmentos_criticos)} segmentos críticos"
        
        return ResultadoValidacion(
            es_factible=es_factible,
            bateria_final=bateria_actual,
            segmentos_criticos=segmentos_criticos,
            paradas_recarga_necesarias=paradas_recarga,
            consumo_total=consumo_total,
            distancia_total=distancia_total,
            mensaje=mensaje
        )
    
    def obtener_estadisticas(self) -> Dict[str, any]:
        """Obtiene estadísticas del validador"""
        return {
            "estaciones_registradas": len(self.estaciones_recarga),
            "distancias_registradas": len(self.distancias_nodos) // 2,  # Dividir por 2 porque son bidireccionales
            "margen_seguridad": self.margen_seguridad,
            "estaciones_por_nodo": list(self.estaciones_recarga.keys())
        }

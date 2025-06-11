from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EstadoDron(Enum):
    DISPONIBLE = "disponible"
    EN_VUELO = "en_vuelo"
    CARGANDO = "cargando"
    MANTENIMIENTO = "mantenimiento"
    FUERA_DE_SERVICIO = "fuera_de_servicio"


class Dron:
    def __init__(
        self,
        dron_id: str,
        modelo: str,
        bateria_maxima: float,
        consumo_por_km: float,
        velocidad_promedio: float = 30.0,
        bateria_actual: Optional[float] = None,
        posicion_actual: Optional[str] = None,
        carga_maxima: float = 5.0,
        tiempo_carga_completa: float = 60.0
    ):
        
        self.dron_id = dron_id
        self.modelo = modelo
        self.bateria_maxima = bateria_maxima
        self.consumo_por_km = consumo_por_km
        self.velocidad_promedio = velocidad_promedio
        self.bateria_actual = bateria_actual if bateria_actual is not None else bateria_maxima
        self.posicion_actual = posicion_actual
        self.carga_maxima = carga_maxima
        self.tiempo_carga_completa = tiempo_carga_completa
        
        self.estado = EstadoDron.DISPONIBLE
        self.kilometros_volados = 0.0
        self.entregas_realizadas = 0
        self.tiempo_vuelo_total = 0.0  # en minutos
        self.ciclos_carga = 0
        self.ultima_actualizacion = datetime.now()

        if self.bateria_actual > self.bateria_maxima:
            self.bateria_actual = self.bateria_maxima
        if self.bateria_actual < 0:
            self.bateria_actual = 0
    
    def obtener_autonomia_actual(self) -> float:
        # Calcula la autonomía actual en kilómetros basada en la batería disponible.
        if self.consumo_por_km <= 0:
            return float('inf')
        return self.bateria_actual / self.consumo_por_km
    
    def obtener_autonomia_maxima(self) -> float:
     
            # Autonomía máxima en kilómetros

        if self.consumo_por_km <= 0:
            return float('inf')
        return self.bateria_maxima / self.consumo_por_km
    
    def puede_volar_distancia(self, distancia_km: float, margen_seguridad: float = 0.1) -> bool:
      
        # Verifica si el dron puede volar una distancia específica.
        
        if self.estado != EstadoDron.DISPONIBLE:
            return False
        
        consumo_necesario = distancia_km * self.consumo_por_km
        consumo_con_margen = consumo_necesario * (1 + margen_seguridad)
        
        return self.bateria_actual >= consumo_con_margen
    
    def calcular_consumo_vuelo(self, distancia_km: float) -> float:

        # Calcula el consumo de batería para una distancia específica.
        return distancia_km * self.consumo_por_km
    
    def volar(self, distancia_km: float, destino: Optional[str] = None) -> bool:
     
        # Ejecuta un vuelo consumiendo batería y actualizando métricas.
        
        if not self.puede_volar_distancia(distancia_km):
            return False
        
        # Calcular consumo y tiempo
        consumo = self.calcular_consumo_vuelo(distancia_km)
        tiempo_vuelo = (distancia_km / self.velocidad_promedio) * 60  # en minutos
        
        # Actualizar estado del dron
        self.estado = EstadoDron.EN_VUELO
        self.bateria_actual -= consumo
        self.kilometros_volados += distancia_km
        self.tiempo_vuelo_total += tiempo_vuelo
        
        if destino:
            self.posicion_actual = destino
        
        # Volver a disponible después del vuelo
        self.estado = EstadoDron.DISPONIBLE
        self.ultima_actualizacion = datetime.now()
        
        return True
    
    def obtener_porcentaje_bateria(self) -> float:
        # Obtiene el porcentaje actual de batería.
    
        if self.bateria_maxima <= 0:
            return 0.0
        return (self.bateria_actual / self.bateria_maxima) * 100
    
    def necesita_recarga(self, umbral_porcentaje: float = 20.0) -> bool:
        
        # Verifica si el dron necesita recarga basado en un umbral.
        return self.obtener_porcentaje_bateria() <= umbral_porcentaje
    
    def cargar_bateria(self, cantidad: Optional[float] = None, carga_completa: bool = True) -> float:
        # Carga la batería del dron.
        bateria_inicial = self.bateria_actual
        
        if carga_completa or cantidad is None:
            self.bateria_actual = self.bateria_maxima
            if bateria_inicial < self.bateria_maxima:
                self.ciclos_carga += 1
        else:
            nueva_bateria = min(self.bateria_actual + cantidad, self.bateria_maxima)
            self.bateria_actual = nueva_bateria
            if cantidad > 0:
                self.ciclos_carga += 1
        
        self.ultima_actualizacion = datetime.now()
        return self.bateria_actual - bateria_inicial
    
    def calcular_tiempo_carga_necesario(self, objetivo_porcentaje: float = 100.0) -> float:
        # Calcula el tiempo necesario para cargar hasta un porcentaje objetivo.
        porcentaje_actual = self.obtener_porcentaje_bateria()
        
        if porcentaje_actual >= objetivo_porcentaje:
            return 0.0
        
        porcentaje_a_cargar = objetivo_porcentaje - porcentaje_actual
        tiempo_proporcional = (porcentaje_a_cargar / 100.0) * self.tiempo_carga_completa
        
        return tiempo_proporcional
    
    def cambiar_estado(self, nuevo_estado: EstadoDron) -> bool:
   # Validaciones de transiciones de estado
        estados_validos = {
            EstadoDron.DISPONIBLE: [EstadoDron.EN_VUELO, EstadoDron.CARGANDO, EstadoDron.MANTENIMIENTO],
            EstadoDron.EN_VUELO: [EstadoDron.DISPONIBLE, EstadoDron.CARGANDO],
            EstadoDron.CARGANDO: [EstadoDron.DISPONIBLE],
            EstadoDron.MANTENIMIENTO: [EstadoDron.DISPONIBLE, EstadoDron.FUERA_DE_SERVICIO],
            EstadoDron.FUERA_DE_SERVICIO: [EstadoDron.MANTENIMIENTO]
        }
        
        if nuevo_estado in estados_validos.get(self.estado, []):
            self.estado = nuevo_estado
            self.ultima_actualizacion = datetime.now()
            return True
        
        return False
    
    def registrar_entrega(self) -> None:
        # Registra una entrega completada.
        self.entregas_realizadas += 1
        self.ultima_actualizacion = datetime.now()
    
    def obtener_metricas(self) -> Dict[str, Any]:
        # Obtiene métricas completas del dron.
        return {
            'dron_id': self.dron_id,
            'modelo': self.modelo,
            'estado': self.estado.value,
            'bateria_actual': self.bateria_actual,
            'bateria_maxima': self.bateria_maxima,
            'porcentaje_bateria': self.obtener_porcentaje_bateria(),
            'autonomia_actual_km': self.obtener_autonomia_actual(),
            'autonomia_maxima_km': self.obtener_autonomia_maxima(),
            'posicion_actual': self.posicion_actual,
            'kilometros_volados': self.kilometros_volados,
            'entregas_realizadas': self.entregas_realizadas,
            'tiempo_vuelo_total_min': self.tiempo_vuelo_total,
            'ciclos_carga': self.ciclos_carga,
            'consumo_por_km': self.consumo_por_km,
            'velocidad_promedio': self.velocidad_promedio,
            'carga_maxima': self.carga_maxima,
            'ultima_actualizacion': self.ultima_actualizacion.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        # Convierte el dron a diccionario para serialización.
        return self.obtener_metricas()
    
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> 'Dron':
        # Crea un dron desde un diccionario.
        dron = cls(
            dron_id=datos['dron_id'],
            modelo=datos['modelo'],
            bateria_maxima=datos['bateria_maxima'],
            consumo_por_km=datos['consumo_por_km'],
            velocidad_promedio=datos.get('velocidad_promedio', 30.0),
            bateria_actual=datos.get('bateria_actual'),
            posicion_actual=datos.get('posicion_actual'),
            carga_maxima=datos.get('carga_maxima', 5.0),
            tiempo_carga_completa=datos.get('tiempo_carga_completa', 60.0)
        )
        
        # Restaurar métricas
        dron.kilometros_volados = datos.get('kilometros_volados', 0.0)
        dron.entregas_realizadas = datos.get('entregas_realizadas', 0)
        dron.tiempo_vuelo_total = datos.get('tiempo_vuelo_total_min', 0.0)
        dron.ciclos_carga = datos.get('ciclos_carga', 0)
        
        # Restaurar estado
        estado_str = datos.get('estado', 'disponible')
        for estado in EstadoDron:
            if estado.value == estado_str:
                dron.estado = estado
                break
        
        return dron
    
    def __str__(self) -> str:
        # Representación en string del dron
        return (f"Dron({self.dron_id}, {self.modelo}, "
                f"Batería: {self.obtener_porcentaje_bateria():.1f}%, "
                f"Estado: {self.estado.value}, "
                f"Autonomía: {self.obtener_autonomia_actual():.1f}km)")
    
    def __repr__(self) -> str:
        # Representación para debugging
        return self.__str__()

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from .drone import Dron, EstadoDron


class EstadoEstacion(Enum):
    DISPONIBLE = "disponible"
    OCUPADA = "ocupada"
    MANTENIMIENTO = "mantenimiento"
    FUERA_DE_SERVICIO = "fuera_de_servicio"


class TipoRecarga(Enum):
    # Tipos de recarga disponibles
    RAPIDA = "rapida"       # Carga rápida (menor tiempo, menor eficiencia)
    NORMAL = "normal"       # Carga normal (tiempo medio, eficiencia media)
    LENTA = "lenta"         # Carga lenta (mayor tiempo, mayor eficiencia)


class EstacionRecarga:
    def __init__(
        self,
        estacion_id: str,
        nodo_id: str,
        capacidad_maxima: int = 1,
        tipos_recarga: Optional[List[TipoRecarga]] = None,
        eficiencia_energetica: float = 0.95,
        costo_por_kwh: float = 0.15,
        tiempo_base_carga: float = 60.0,
        disponible: bool = True
    ):
        
        self.estacion_id = estacion_id
        self.nodo_id = nodo_id
        self.capacidad_maxima = capacidad_maxima
        self.tipos_recarga = tipos_recarga or [TipoRecarga.NORMAL]
        self.eficiencia_energetica = max(0.0, min(1.0, eficiencia_energetica))
        self.costo_por_kwh = costo_por_kwh
        self.tiempo_base_carga = tiempo_base_carga
        self.disponible = disponible
        
        # Estado operativo
        self.estado = EstadoEstacion.DISPONIBLE if disponible else EstadoEstacion.FUERA_DE_SERVICIO
        self.drones_cargando: Dict[str, Dict[str, Any]] = {}  # dron_id -> info_carga
        self.cola_espera: List[str] = []  # Lista de drones esperando
        
        # Métricas y estadísticas
        self.total_cargas_realizadas = 0
        self.energia_total_suministrada = 0.0  # en kWh
        self.tiempo_operativo_total = 0.0  # en minutos
        self.ingresos_generados = 0.0
        self.ultima_actualizacion = datetime.now()
        
        # Configuración de tipos de recarga
        self.configuracion_recarga = {
            TipoRecarga.RAPIDA: {"multiplicador_tiempo": 0.5, "multiplicador_costo": 1.5, "eficiencia": 0.85},
            TipoRecarga.NORMAL: {"multiplicador_tiempo": 1.0, "multiplicador_costo": 1.0, "eficiencia": 0.95},
            TipoRecarga.LENTA: {"multiplicador_tiempo": 2.0, "multiplicador_costo": 0.8, "eficiencia": 0.98}
        }
    
    def esta_disponible(self) -> bool:
        # Verifica si la estación está disponible para recibir drones.
        return (self.estado == EstadoEstacion.DISPONIBLE and 
                len(self.drones_cargando) < self.capacidad_maxima and
                self.disponible)
    
    def tiene_espacio(self) -> bool:
        # Verifica si hay espacio para más drones (incluyendo cola).
        return len(self.drones_cargando) < self.capacidad_maxima
    
    def obtener_tiempo_espera_estimado(self) -> float:
        if self.tiene_espacio():
            return 0.0
        
        # Calcular tiempo restante del dron que termine primero
        tiempos_restantes = []
        for info_carga in self.drones_cargando.values():
            tiempo_transcurrido = (datetime.now() - info_carga['inicio']).total_seconds() / 60
            tiempo_restante = max(0, info_carga['tiempo_estimado'] - tiempo_transcurrido)
            tiempos_restantes.append(tiempo_restante)
        
        return min(tiempos_restantes) if tiempos_restantes else 0.0
    
    def calcular_tiempo_carga(self, dron: Dron, tipo_recarga: TipoRecarga = TipoRecarga.NORMAL, 
                             objetivo_porcentaje: float = 100.0) -> float:
        if tipo_recarga not in self.tipos_recarga:
            tipo_recarga = self.tipos_recarga[0]  # Usar el primer tipo disponible
        
        config = self.configuracion_recarga[tipo_recarga]
        tiempo_base = dron.calcular_tiempo_carga_necesario(objetivo_porcentaje)
        tiempo_ajustado = tiempo_base * config["multiplicador_tiempo"]
        
        # Ajustar por eficiencia de la estación
        tiempo_final = tiempo_ajustado / self.eficiencia_energetica
        
        return tiempo_final
    
    def calcular_costo_carga(self, dron: Dron, tipo_recarga: TipoRecarga = TipoRecarga.NORMAL,
                           objetivo_porcentaje: float = 100.0) -> float:
        
        if tipo_recarga not in self.tipos_recarga:
            tipo_recarga = self.tipos_recarga[0]
        
        config = self.configuracion_recarga[tipo_recarga]
        
        # Calcular energía necesaria (asumiendo que bateria_maxima está en kWh)
        porcentaje_actual = dron.obtener_porcentaje_bateria()
        energia_necesaria = (objetivo_porcentaje - porcentaje_actual) / 100.0 * (dron.bateria_maxima / 1000.0)  # Convertir a kWh
        
        # Aplicar multiplicadores
        costo_base = energia_necesaria * self.costo_por_kwh
        costo_final = costo_base * config["multiplicador_costo"]
        
        return max(0.0, costo_final)
    
    def iniciar_carga(self, dron: Dron, tipo_recarga: TipoRecarga = TipoRecarga.NORMAL,
                      objetivo_porcentaje: float = 100.0) -> bool:
        if not self.esta_disponible():
            return False
        
        if dron.dron_id in self.drones_cargando:
            return False  # El dron ya está cargando
        
        if tipo_recarga not in self.tipos_recarga:
            tipo_recarga = self.tipos_recarga[0]
        
        # Cambiar estado del dron
        if not dron.cambiar_estado(EstadoDron.CARGANDO):
            return False
        
        # Calcular parámetros de carga
        tiempo_estimado = self.calcular_tiempo_carga(dron, tipo_recarga, objetivo_porcentaje)
        costo_estimado = self.calcular_costo_carga(dron, tipo_recarga, objetivo_porcentaje)
        
        # Registrar información de carga
        info_carga = {
            'dron': dron,
            'tipo_recarga': tipo_recarga,
            'objetivo_porcentaje': objetivo_porcentaje,
            'porcentaje_inicial': dron.obtener_porcentaje_bateria(),
            'tiempo_estimado': tiempo_estimado,
            'costo_estimado': costo_estimado,
            'inicio': datetime.now(),
            'fin_estimado': datetime.now() + timedelta(minutes=tiempo_estimado)
        }
        
        self.drones_cargando[dron.dron_id] = info_carga
        
        # Actualizar posición del dron
        dron.posicion_actual = self.nodo_id
        
        # Actualizar estado de la estación
        if len(self.drones_cargando) >= self.capacidad_maxima:
            self.estado = EstadoEstacion.OCUPADA
        
        self.ultima_actualizacion = datetime.now()
        return True
    
    def finalizar_carga(self, dron_id: str) -> Dict[str, Any]:
        if dron_id not in self.drones_cargando:
            return {"error": "Dron no encontrado en carga"}
        
        info_carga = self.drones_cargando[dron_id]
        dron = info_carga['dron']
        
        # Calcular tiempo real transcurrido
        tiempo_real = (datetime.now() - info_carga['inicio']).total_seconds() / 60
        
        # Cargar la batería del dron
        config = self.configuracion_recarga[info_carga['tipo_recarga']]
        eficiencia_real = config["eficiencia"] * self.eficiencia_energetica
        
        # Calcular porcentaje real cargado (considerando eficiencias)
        porcentaje_objetivo = info_carga['objetivo_porcentaje']
        porcentaje_inicial = info_carga['porcentaje_inicial']
        porcentaje_teorico = porcentaje_objetivo - porcentaje_inicial
        porcentaje_real = porcentaje_teorico * eficiencia_real
        
        # Aplicar carga al dron
        bateria_a_cargar = (porcentaje_real / 100.0) * dron.bateria_maxima
        cantidad_cargada = dron.cargar_bateria(cantidad=bateria_a_cargar, carga_completa=False)
        
        # Cambiar estado del dron de vuelta a disponible
        dron.cambiar_estado(EstadoDron.DISPONIBLE)
          # Calcular métricas finales
        energia_suministrada = cantidad_cargada / 1000.0  # Convertir a kWh
        
        # Calcular costo usando la información original de la carga
        porcentaje_inicial = info_carga['porcentaje_inicial']
        objetivo_porcentaje = info_carga['objetivo_porcentaje']
        energia_teorica_necesaria = (objetivo_porcentaje - porcentaje_inicial) / 100.0 * (dron.bateria_maxima / 1000.0)
        config = self.configuracion_recarga[info_carga['tipo_recarga']]
        costo_real = energia_teorica_necesaria * self.costo_por_kwh * config["multiplicador_costo"]
        
        # Actualizar estadísticas de la estación
        self.total_cargas_realizadas += 1
        self.energia_total_suministrada += energia_suministrada
        self.tiempo_operativo_total += tiempo_real
        self.ingresos_generados += costo_real
        
        # Remover de la lista de carga
        del self.drones_cargando[dron_id]
        
        # Actualizar estado de la estación
        if self.estado == EstadoEstacion.OCUPADA and len(self.drones_cargando) < self.capacidad_maxima:
            self.estado = EstadoEstacion.DISPONIBLE
        
        self.ultima_actualizacion = datetime.now()
        
        # Procesar cola de espera si hay espacio
        self._procesar_cola_espera()
        
        return {
            "dron_id": dron_id,
            "tiempo_real": tiempo_real,
            "tiempo_estimado": info_carga['tiempo_estimado'],
            "porcentaje_inicial": porcentaje_inicial,
            "porcentaje_final": dron.obtener_porcentaje_bateria(),
            "cantidad_cargada": cantidad_cargada,
            "energia_suministrada": energia_suministrada,
            "costo": costo_real,
            "eficiencia_real": eficiencia_real * 100,
            "tipo_recarga": info_carga['tipo_recarga'].value
        }
    
    def verificar_cargas_completadas(self) -> List[Dict[str, Any]]:
        cargas_finalizadas = []
        drones_a_finalizar = []
        
        for dron_id, info_carga in self.drones_cargando.items():
            if datetime.now() >= info_carga['fin_estimado']:
                drones_a_finalizar.append(dron_id)
        
        for dron_id in drones_a_finalizar:
            resultado = self.finalizar_carga(dron_id)
            cargas_finalizadas.append(resultado)
        
        return cargas_finalizadas
    
    def agregar_a_cola(self, dron_id: str) -> bool:
        if dron_id not in self.cola_espera and dron_id not in self.drones_cargando:
            self.cola_espera.append(dron_id)
            return True
        return False
    
    def _procesar_cola_espera(self) -> None:
        while self.tiene_espacio() and self.cola_espera:
            # Nota: Necesitaríamos acceso al dron desde el ID para iniciar carga
            # Por ahora solo removemos de la cola
            self.cola_espera.pop(0)
    
    def cambiar_estado(self, nuevo_estado: EstadoEstacion) -> bool:
        # Validaciones de transiciones de estado
        estados_validos = {
            EstadoEstacion.DISPONIBLE: [EstadoEstacion.OCUPADA, EstadoEstacion.MANTENIMIENTO],
            EstadoEstacion.OCUPADA: [EstadoEstacion.DISPONIBLE, EstadoEstacion.MANTENIMIENTO],
            EstadoEstacion.MANTENIMIENTO: [EstadoEstacion.DISPONIBLE, EstadoEstacion.FUERA_DE_SERVICIO],
            EstadoEstacion.FUERA_DE_SERVICIO: [EstadoEstacion.MANTENIMIENTO]
        }
        
        if nuevo_estado in estados_validos.get(self.estado, []):
            self.estado = nuevo_estado
            self.ultima_actualizacion = datetime.now()
            return True
        
        return False
    
    def obtener_metricas(self) -> Dict[str, Any]:
        return {
            'estacion_id': self.estacion_id,
            'nodo_id': self.nodo_id,
            'estado': self.estado.value,
            'capacidad_maxima': self.capacidad_maxima,
            'drones_cargando': len(self.drones_cargando),
            'cola_espera': len(self.cola_espera),
            'disponible': self.esta_disponible(),
            'tipos_recarga': [tipo.value for tipo in self.tipos_recarga],
            'eficiencia_energetica': self.eficiencia_energetica,
            'costo_por_kwh': self.costo_por_kwh,
            'tiempo_base_carga': self.tiempo_base_carga,
            'total_cargas_realizadas': self.total_cargas_realizadas,
            'energia_total_suministrada': self.energia_total_suministrada,
            'tiempo_operativo_total': self.tiempo_operativo_total,
            'ingresos_generados': self.ingresos_generados,
            'tiempo_espera_estimado': self.obtener_tiempo_espera_estimado(),
            'ultima_actualizacion': self.ultima_actualizacion.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        # Convierte la estación a diccionario para serialización.
        return self.obtener_metricas()
    
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> 'EstacionRecarga':
        # Crea una estación desde un diccionario.
        tipos_recarga = []
        for tipo_str in datos.get('tipos_recarga', ['normal']):
            for tipo in TipoRecarga:
                if tipo.value == tipo_str:
                    tipos_recarga.append(tipo)
                    break
        
        estacion = cls(
            estacion_id=datos['estacion_id'],
            nodo_id=datos['nodo_id'],
            capacidad_maxima=datos.get('capacidad_maxima', 1),
            tipos_recarga=tipos_recarga,
            eficiencia_energetica=datos.get('eficiencia_energetica', 0.95),
            costo_por_kwh=datos.get('costo_por_kwh', 0.15),
            tiempo_base_carga=datos.get('tiempo_base_carga', 60.0),
            disponible=datos.get('disponible', True)
        )
        
        # Restaurar métricas
        estacion.total_cargas_realizadas = datos.get('total_cargas_realizadas', 0)
        estacion.energia_total_suministrada = datos.get('energia_total_suministrada', 0.0)
        estacion.tiempo_operativo_total = datos.get('tiempo_operativo_total', 0.0)
        estacion.ingresos_generados = datos.get('ingresos_generados', 0.0)
        
        # Restaurar estado
        estado_str = datos.get('estado', 'disponible')
        for estado in EstadoEstacion:
            if estado.value == estado_str:
                estacion.estado = estado
                break
        
        return estacion
    
    def __str__(self) -> str:
        # Representación en string de la estación
        return (f"EstacionRecarga({self.estacion_id}, Nodo: {self.nodo_id}, "
                f"Estado: {self.estado.value}, "
                f"Ocupación: {len(self.drones_cargando)}/{self.capacidad_maxima})")
    
    def __repr__(self) -> str:
        # Representación para debugging
        return self.__str__()

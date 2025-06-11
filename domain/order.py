"""
Entidades del dominio (negocio) - Clase Order

Define la estructura y comportamiento de las órdenes/pedidos en el sistema de grafos conectados.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid
import random


class EstadoOrden(Enum):
    """Estados posibles de una orden"""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_PREPARACION = "en_preparacion"
    EN_TRANSITO = "en_transito"
    ENTREGADA = "entregada"
    CANCELADA = "cancelada"
    DEVUELTA = "devuelta"


class PrioridadOrden(Enum):
    """Niveles de prioridad de una orden"""
    BAJA = 1
    MEDIA = 2
    ALTA = 3
    CRITICA = 4


class TipoOrden(Enum):
    """Tipos de orden según su naturaleza"""
    COMPRA = "compra"
    ENTREGA = "entrega"
    RECOGIDA = "recogida"
    INTERCAMBIO = "intercambio"
    SERVICIO = "servicio"


class Orden:
    """
    Representa una orden/pedido en el sistema de grafos conectados.
    
    Una orden conecta un cliente con nodos de origen y destino,
    tiene un estado, prioridad y valor asociado.
    """
    
    def __init__(
        self,
        orden_id: str = None,
        cliente_id: str = "",
        tipo: TipoOrden = TipoOrden.ENTREGA,
        nodo_origen: str = "",
        nodo_destino: str = "",
        prioridad: PrioridadOrden = PrioridadOrden.MEDIA,
        valor_base: float = 0.0,
        descripcion: str = "",
        peso_kg: float = 0.0,
        dimensiones: str = "",
        fecha_entrega_solicitada: Optional[datetime] = None
    ):
        """
        Inicializa una nueva orden.
        
        Args:
            orden_id: Identificador único de la orden
            cliente_id: ID del cliente que realizó la orden
            tipo: Tipo de orden
            nodo_origen: ID del nodo de origen
            nodo_destino: ID del nodo de destino
            prioridad: Prioridad de la orden
            valor_base: Valor base de la orden
            descripcion: Descripción de la orden
            peso_kg: Peso en kilogramos
            dimensiones: Dimensiones del paquete
            fecha_entrega_solicitada: Fecha de entrega solicitada
        """
        self.orden_id = orden_id or f"ORD_{uuid.uuid4().hex[:8].upper()}"
        self.cliente_id = cliente_id
        self.tipo = tipo
        self.nodo_origen = nodo_origen
        self.nodo_destino = nodo_destino
        self.prioridad = prioridad
        self.valor_base = max(0.0, valor_base)
        self.descripcion = descripcion or f"Orden {self.orden_id}"
        self.peso_kg = max(0.0, peso_kg)
        self.dimensiones = dimensiones
        
        # Fechas y tiempos
        self.fecha_creacion = datetime.now()
        self.fecha_entrega_solicitada = fecha_entrega_solicitada or (
            self.fecha_creacion + timedelta(days=random.randint(1, 7))
        )
        self.fecha_confirmacion: Optional[datetime] = None
        self.fecha_inicio_preparacion: Optional[datetime] = None
        self.fecha_inicio_transito: Optional[datetime] = None
        self.fecha_entrega_real: Optional[datetime] = None
        self.fecha_cancelacion: Optional[datetime] = None
        
        # Estado y control
        self.estado = EstadoOrden.PENDIENTE
        self.estado_anterior: Optional[EstadoOrden] = None
        
        # Costos y valores
        self.costo_envio = 0.0
        self.descuento_aplicado = 0.0
        self.impuestos = 0.0
        self.costo_total = self.valor_base
        
        # Métricas y seguimiento
        self.intentos_entrega = 0
        self.tiempo_estimado_entrega = 0.0  # en horas
        self.distancia_estimada = 0.0
        
        # Observaciones y notas
        self.notas_cliente = ""
        self.notas_internas = ""
        self.motivo_cancelacion = ""
        
        # Asignación de recursos
        self.vehiculo_asignado = ""
        self.conductor_asignado = ""
        self.ruta_planificada: List[str] = []  # Lista de nodos en la ruta
    
    def calcular_costo_total(self, descuento_cliente: float = 0.0) -> float:
        """
        Calcula el costo total de la orden incluyendo descuentos e impuestos.
        
        Args:
            descuento_cliente: Descuento adicional del cliente
            
        Returns:
            float: Costo total calculado
        """
        # Calcular costo base con envío
        subtotal = self.valor_base + self.costo_envio
        
        # Aplicar descuentos
        descuento_total = self.descuento_aplicado + descuento_cliente
        subtotal_con_descuento = subtotal - (subtotal * min(descuento_total, 0.30))
        
        # Calcular impuestos sobre el subtotal con descuento
        impuestos_calculados = subtotal_con_descuento * 0.19  # IVA 19%
        
        # Costo total
        total = subtotal_con_descuento + impuestos_calculados
        
        # Actualizar valores internos
        self.impuestos = impuestos_calculados
        self.costo_total = max(0.0, total)
        
        return self.costo_total
    
    def estimar_costo_envio(self, distancia: float, factor_prioridad: float = 1.0) -> float:
        """
        Estima el costo de envío basado en distancia, peso y prioridad.
        
        Args:
            distancia: Distancia entre origen y destino
            factor_prioridad: Factor multiplicador por prioridad
            
        Returns:
            float: Costo de envío estimado
        """
        # Costo base por distancia
        costo_base = distancia * 1.5  # $1.5 por unidad de distancia
        
        # Costo por peso
        costo_peso = self.peso_kg * 0.5 if self.peso_kg > 1.0 else 0.0
        
        # Factor de prioridad
        multiplicador_prioridad = {
            PrioridadOrden.BAJA: 1.0,
            PrioridadOrden.MEDIA: 1.2,
            PrioridadOrden.ALTA: 1.5,
            PrioridadOrden.CRITICA: 2.0
        }
        
        factor = multiplicador_prioridad.get(self.prioridad, 1.0) * factor_prioridad
        
        self.costo_envio = (costo_base + costo_peso) * factor
        self.distancia_estimada = distancia
        
        return self.costo_envio
    
    def cambiar_estado(self, nuevo_estado: EstadoOrden, notas: str = "") -> bool:
        """
        Cambia el estado de la orden validando transiciones válidas.
        
        Args:
            nuevo_estado: Nuevo estado de la orden
            notas: Notas adicionales del cambio de estado
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        # Definir transiciones válidas
        transiciones_validas = {
            EstadoOrden.PENDIENTE: [EstadoOrden.CONFIRMADA, EstadoOrden.CANCELADA],
            EstadoOrden.CONFIRMADA: [EstadoOrden.EN_PREPARACION, EstadoOrden.CANCELADA],
            EstadoOrden.EN_PREPARACION: [EstadoOrden.EN_TRANSITO, EstadoOrden.CANCELADA],
            EstadoOrden.EN_TRANSITO: [EstadoOrden.ENTREGADA, EstadoOrden.DEVUELTA],
            EstadoOrden.ENTREGADA: [EstadoOrden.DEVUELTA],
            EstadoOrden.CANCELADA: [],
            EstadoOrden.DEVUELTA: [EstadoOrden.EN_PREPARACION]
        }
        
        if nuevo_estado not in transiciones_validas.get(self.estado, []):
            return False
        
        # Actualizar estado y fechas
        self.estado_anterior = self.estado
        self.estado = nuevo_estado
        
        ahora = datetime.now()
        
        if nuevo_estado == EstadoOrden.CONFIRMADA:
            self.fecha_confirmacion = ahora
        elif nuevo_estado == EstadoOrden.EN_PREPARACION:
            self.fecha_inicio_preparacion = ahora
        elif nuevo_estado == EstadoOrden.EN_TRANSITO:
            self.fecha_inicio_transito = ahora
        elif nuevo_estado == EstadoOrden.ENTREGADA:
            self.fecha_entrega_real = ahora
        elif nuevo_estado == EstadoOrden.CANCELADA:
            self.fecha_cancelacion = ahora
            self.motivo_cancelacion = notas
        
        if notas:
            self.notas_internas += f"[{ahora.strftime('%Y-%m-%d %H:%M')}] {notas}\n"
        
        return True
    
    def esta_vencida(self) -> bool:
        """
        Verifica si la orden está vencida (fecha de entrega pasada).
        
        Returns:
            bool: True si está vencida
        """
        if self.estado in [EstadoOrden.ENTREGADA, EstadoOrden.CANCELADA]:
            return False
        
        return datetime.now() > self.fecha_entrega_solicitada
    
    def calcular_tiempo_transcurrido(self) -> Dict[str, float]:
        """
        Calcula los tiempos transcurridos en cada etapa.
        
        Returns:
            Dict: Tiempos en horas para cada etapa
        """
        ahora = datetime.now()
        
        tiempos = {
            'total': (ahora - self.fecha_creacion).total_seconds() / 3600,
            'pendiente': 0.0,
            'preparacion': 0.0,
            'transito': 0.0
        }
        
        if self.fecha_confirmacion:
            tiempos['pendiente'] = (
                self.fecha_confirmacion - self.fecha_creacion
            ).total_seconds() / 3600
        
        if self.fecha_inicio_preparacion and self.fecha_inicio_transito:
            tiempos['preparacion'] = (
                self.fecha_inicio_transito - self.fecha_inicio_preparacion
            ).total_seconds() / 3600
        
        if self.fecha_inicio_transito:
            fin_transito = self.fecha_entrega_real or ahora
            tiempos['transito'] = (
                fin_transito - self.fecha_inicio_transito
            ).total_seconds() / 3600
        
        return tiempos
    
    def asignar_ruta(self, ruta_nodos: List[str], tiempo_estimado: float) -> None:
        """
        Asigna una ruta planificada a la orden.
        
        Args:
            ruta_nodos: Lista de IDs de nodos en la ruta
            tiempo_estimado: Tiempo estimado de entrega en horas
        """
        self.ruta_planificada = ruta_nodos.copy()
        self.tiempo_estimado_entrega = tiempo_estimado
        
        # Actualizar notas internas
        self.notas_internas += (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] "
            f"Ruta asignada: {' -> '.join(ruta_nodos)}\n"
        )
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de la orden.
        
        Returns:
            Dict: Resumen de la orden
        """
        tiempos = self.calcular_tiempo_transcurrido()
        
        return {
            # Información básica
            'orden_id': self.orden_id,
            'cliente_id': self.cliente_id,
            'tipo': self.tipo.value,
            'estado': self.estado.value,
            'prioridad': self.prioridad.value,
            
            # Ubicación
            'nodo_origen': self.nodo_origen,
            'nodo_destino': self.nodo_destino,
            'distancia_estimada': round(self.distancia_estimada, 2),
            
            # Descripción y características
            'descripcion': self.descripcion,
            'peso_kg': self.peso_kg,
            'dimensiones': self.dimensiones,
            
            # Valores financieros
            'valor_base': round(self.valor_base, 2),
            'costo_envio': round(self.costo_envio, 2),
            'descuento_aplicado': round(self.descuento_aplicado, 2),
            'impuestos': round(self.impuestos, 2),
            'costo_total': round(self.costo_total, 2),
            
            # Fechas importantes
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_entrega_solicitada': self.fecha_entrega_solicitada.isoformat(),
            'fecha_confirmacion': self.fecha_confirmacion.isoformat() if self.fecha_confirmacion else None,
            'fecha_entrega_real': self.fecha_entrega_real.isoformat() if self.fecha_entrega_real else None,
            'esta_vencida': self.esta_vencida(),
            
            # Tiempos y métricas
            'tiempo_estimado_entrega': self.tiempo_estimado_entrega,
            'tiempo_transcurrido_total': round(tiempos['total'], 2),
            'intentos_entrega': self.intentos_entrega,
            
            # Asignaciones
            'vehiculo_asignado': self.vehiculo_asignado,
            'conductor_asignado': self.conductor_asignado,
            'ruta_planificada': self.ruta_planificada,
            
            # Observaciones
            'notas_cliente': self.notas_cliente,
            'motivo_cancelacion': self.motivo_cancelacion if self.estado == EstadoOrden.CANCELADA else "",
        }
    
    def __str__(self) -> str:
        return f"Orden({self.orden_id}, {self.cliente_id}, {self.estado.value}, ${self.costo_total:.2f})"
    
    def __repr__(self) -> str:
        return (f"Orden(orden_id='{self.orden_id}', cliente_id='{self.cliente_id}', "
                f"estado={self.estado}, tipo={self.tipo}, prioridad={self.prioridad})")

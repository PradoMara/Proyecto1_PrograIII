"""
Entidades del dominio (negocio) - Clase Client

Define la estructura y comportamiento de los clientes en el sistema de grafos conectados.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class TipoCliente(Enum):
    """Tipos de cliente en el sistema"""
    PREMIUM = "premium"
    REGULAR = "regular"
    CORPORATIVO = "corporativo"
    VIP = "vip"


class EstadoCliente(Enum):
    """Estados posibles de un cliente"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"
    BLOQUEADO = "bloqueado"


class Cliente:
    """
    Representa un cliente en el sistema de grafos conectados.
    
    Un cliente puede realizar pedidos y tiene asociado un nodo en el grafo
    donde se encuentra ubicado geográficamente.
    """
    
    def __init__(
        self,
        cliente_id: str = None,
        nombre: str = "",
        tipo: TipoCliente = TipoCliente.REGULAR,
        nodo_ubicacion: str = "",
        email: str = "",
        telefono: str = "",
        direccion: str = "",
        limite_credito: float = 1000.0,
        descuento_base: float = 0.0
    ):
        """
        Inicializa un nuevo cliente.
        
        Args:
            cliente_id: Identificador único del cliente
            nombre: Nombre del cliente
            tipo: Tipo de cliente (premium, regular, etc.)
            nodo_ubicacion: ID del nodo donde está ubicado el cliente
            email: Email del cliente
            telefono: Teléfono del cliente
            direccion: Dirección del cliente
            limite_credito: Límite de crédito del cliente
            descuento_base: Descuento base aplicable (0.0 a 1.0)
        """
        self.cliente_id = cliente_id or f"CLI_{uuid.uuid4().hex[:8].upper()}"
        self.nombre = nombre or f"Cliente_{self.cliente_id[-4:]}"
        self.tipo = tipo
        self.nodo_ubicacion = nodo_ubicacion
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.limite_credito = max(0.0, limite_credito)
        self.descuento_base = max(0.0, min(1.0, descuento_base))
        
        # Estado y métricas
        self.estado = EstadoCliente.ACTIVO
        self.fecha_registro = datetime.now()
        self.fecha_ultima_actividad = datetime.now()
        
        # Estadísticas de pedidos
        self.total_pedidos = 0
        self.total_gastado = 0.0
        self.pedidos_completados = 0
        self.pedidos_cancelados = 0
        
        # Preferencias y configuración
        self.prioridad_default = 1  # 1=baja, 2=media, 3=alta
        self.notificaciones_activas = True
        
        # Histórico y métricas adicionales
        self.fecha_ultimo_pedido: Optional[datetime] = None
        self.promedio_valor_pedido = 0.0
        self.historial_pedidos: List[str] = []  # IDs de pedidos
    
    def puede_realizar_pedido(self, valor_pedido: float) -> bool:
        """
        Verifica si el cliente puede realizar un pedido basado en su límite de crédito.
        
        Args:
            valor_pedido: Valor del pedido a verificar
            
        Returns:
            bool: True si puede realizar el pedido
        """
        if self.estado != EstadoCliente.ACTIVO:
            return False
        
        saldo_pendiente = self.calcular_saldo_pendiente()
        return (saldo_pendiente + valor_pedido) <= self.limite_credito
    
    def calcular_saldo_pendiente(self) -> float:
        """
        Calcula el saldo pendiente del cliente.
        Por simplicidad, asumimos que no hay saldo pendiente por ahora.
        
        Returns:
            float: Saldo pendiente
        """
        # TODO: Implementar lógica de cálculo de saldo pendiente
        # basado en pedidos no pagados
        return 0.0
    
    def calcular_descuento_aplicable(self, valor_base: float) -> float:
        """
        Calcula el descuento aplicable basado en el tipo de cliente.
        
        Args:
            valor_base: Valor base del pedido
            
        Returns:
            float: Descuento aplicable
        """
        descuento_tipo = {
            TipoCliente.REGULAR: 0.0,
            TipoCliente.PREMIUM: 0.05,
            TipoCliente.CORPORATIVO: 0.10,
            TipoCliente.VIP: 0.15
        }
        
        descuento_total = self.descuento_base + descuento_tipo.get(self.tipo, 0.0)
        descuento_total = min(descuento_total, 0.30)  # Máximo 30% de descuento
        
        return valor_base * descuento_total
    
    def registrar_pedido(self, pedido_id: str, valor: float) -> None:
        """
        Registra un nuevo pedido para el cliente.
        
        Args:
            pedido_id: ID del pedido
            valor: Valor del pedido
        """
        self.historial_pedidos.append(pedido_id)
        self.total_pedidos += 1
        self.total_gastado += valor
        self.fecha_ultimo_pedido = datetime.now()
        self.fecha_ultima_actividad = datetime.now()
        
        # Actualizar promedio
        self.promedio_valor_pedido = self.total_gastado / self.total_pedidos
    
    def completar_pedido(self, pedido_id: str) -> None:
        """
        Marca un pedido como completado.
        
        Args:
            pedido_id: ID del pedido completado
        """
        if pedido_id in self.historial_pedidos:
            self.pedidos_completados += 1
            self.fecha_ultima_actividad = datetime.now()
    
    def cancelar_pedido(self, pedido_id: str, valor: float) -> None:
        """
        Marca un pedido como cancelado y ajusta las métricas.
        
        Args:
            pedido_id: ID del pedido cancelado
            valor: Valor del pedido cancelado
        """
        if pedido_id in self.historial_pedidos:
            self.pedidos_cancelados += 1
            self.total_gastado = max(0.0, self.total_gastado - valor)
            
            # Recalcular promedio
            if self.total_pedidos > 0:
                self.promedio_valor_pedido = self.total_gastado / self.total_pedidos
    
    def cambiar_estado(self, nuevo_estado: EstadoCliente) -> bool:
        """
        Cambia el estado del cliente.
        
        Args:
            nuevo_estado: Nuevo estado del cliente
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        estados_validos = {
            EstadoCliente.ACTIVO: [EstadoCliente.INACTIVO, EstadoCliente.SUSPENDIDO],
            EstadoCliente.INACTIVO: [EstadoCliente.ACTIVO],
            EstadoCliente.SUSPENDIDO: [EstadoCliente.ACTIVO, EstadoCliente.BLOQUEADO],
            EstadoCliente.BLOQUEADO: [EstadoCliente.SUSPENDIDO]
        }
        
        if nuevo_estado in estados_validos.get(self.estado, []):
            self.estado = nuevo_estado
            self.fecha_ultima_actividad = datetime.now()
            return True
        
        return False
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen completo del cliente.
        
        Returns:
            Dict: Resumen del cliente
        """
        tasa_completado = (
            (self.pedidos_completados / self.total_pedidos * 100) 
            if self.total_pedidos > 0 else 0.0
        )
        
        tasa_cancelado = (
            (self.pedidos_cancelados / self.total_pedidos * 100) 
            if self.total_pedidos > 0 else 0.0
        )
        
        return {
            # Información básica
            'cliente_id': self.cliente_id,
            'nombre': self.nombre,
            'tipo': self.tipo.value,
            'estado': self.estado.value,
            'nodo_ubicacion': self.nodo_ubicacion,
            
            # Contacto
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            
            # Financiero
            'limite_credito': self.limite_credito,
            'descuento_base': self.descuento_base,
            'saldo_pendiente': self.calcular_saldo_pendiente(),
            
            # Métricas de pedidos
            'total_pedidos': self.total_pedidos,
            'pedidos_completados': self.pedidos_completados,
            'pedidos_cancelados': self.pedidos_cancelados,
            'total_gastado': round(self.total_gastado, 2),
            'promedio_valor_pedido': round(self.promedio_valor_pedido, 2),
            'tasa_completado': round(tasa_completado, 1),
            'tasa_cancelado': round(tasa_cancelado, 1),
            
            # Fechas
            'fecha_registro': self.fecha_registro.isoformat(),
            'fecha_ultima_actividad': self.fecha_ultima_actividad.isoformat(),
            'fecha_ultimo_pedido': self.fecha_ultimo_pedido.isoformat() if self.fecha_ultimo_pedido else None,
            
            # Configuración
            'prioridad_default': self.prioridad_default,
            'notificaciones_activas': self.notificaciones_activas
        }
    
    def __str__(self) -> str:
        return f"Cliente({self.cliente_id}, {self.nombre}, {self.tipo.value}, {self.estado.value})"
    
    def __repr__(self) -> str:
        return (f"Cliente(cliente_id='{self.cliente_id}', nombre='{self.nombre}', "
                f"tipo={self.tipo}, estado={self.estado}, total_pedidos={self.total_pedidos})")

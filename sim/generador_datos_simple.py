"""
Generador de datos de simulación para clientes y órdenes.

Este módulo se encarga de generar datos simulados realistas
para clientes y órdenes basándose en un grafo existente.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from model import BuscadorNodos, RolNodo
from domain.client import Cliente
from domain.order import Orden


class GeneradorDatosSimulacion:
    """
    Genera datos de simulación para clientes y órdenes basándose en un grafo.
    """
    
    def __init__(self, semilla: Optional[int] = None):
        """
        Inicializa el generador con una semilla opcional para reproducibilidad.
        
        Args:
            semilla: Semilla para el generador de números aleatorios
        """
        if semilla:
            random.seed(semilla)
        
        # Listas de nombres para generar datos realistas
        self.nombres_clientes = [
            "Juan Pérez", "María González", "Carlos Silva", "Ana Martínez",
            "Luis Rodriguez", "Carmen López", "Jorge Fernández", "Sofia Torres",
            "Roberto Morales", "Laura Castro", "Miguel Herrera", "Elena Vargas",
            "Francisco Jiménez", "Isabel Ruiz", "Antonio Mendoza", "Patricia Guerrero"
        ]
        
        self.empresas = [
            "TechCorp SA", "GlobalTech Ltda", "InnovaSoft", "DataSystems",
            "CloudSolutions", "DigitalPro", "TechAdvance", "SystemsPlus",
            "InfoTech", "NetSolutions", "DataCorp", "TechFlow"
        ]
        
        self.productos_servicios = [
            "Entrega de paquete", "Servicio técnico", "Entrega de documentos",
            "Transporte de equipos", "Servicio de mantenimiento", "Entrega urgente",
            "Traslado de materiales", "Servicio especializado", "Entrega programada",
            "Servicio express", "Transporte especial", "Entrega corporativa"
        ]
        
        # Tipos de cliente disponibles
        self.tipos_cliente = ["regular", "premium", "corporativo", "vip"]
        
        # Prioridades disponibles  
        self.prioridades = ["low", "normal", "high", "critical"]
    
    def generar_clientes(self, grafo, cantidad: int = None) -> List[Cliente]:
        """
        Genera clientes basándose en los nodos de tipo cliente del grafo.
        
        Args:
            grafo: Grafo del cual obtener nodos cliente
            cantidad: Cantidad específica de clientes (si no se especifica, usa nodos cliente disponibles)
            
        Returns:
            List[Cliente]: Lista de clientes generados
        """
        # Buscar nodos de tipo cliente
        nodos_cliente = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.CLIENTE)
        
        if not nodos_cliente:
            return []
        
        # Determinar cantidad a generar
        if cantidad is None:
            # Generar entre 1-3 clientes por nodo cliente
            cantidad = len(nodos_cliente) * random.randint(1, 3)
        
        clientes = []
        
        for i in range(cantidad):
            # Seleccionar nodo aleatorio para ubicar cliente
            nodo = random.choice(nodos_cliente)
            cliente = self._generar_cliente_individual(nodo)
            clientes.append(cliente)
        
        return clientes
    
    def _generar_cliente_individual(self, nodo) -> Cliente:
        """
        Genera un cliente individual basado en un nodo.
        
        Args:
            nodo: Nodo del grafo
            
        Returns:
            Cliente: Cliente generado
        """
        # Determinar tipo de cliente con probabilidades realistas
        tipos_probabilidades = [
            ("regular", 0.60),
            ("premium", 0.25),
            ("corporativo", 0.10),
            ("vip", 0.05)
        ]
        
        tipo_cliente = self._seleccionar_por_probabilidad(tipos_probabilidades)
        
        # Generar nombre según el tipo
        if tipo_cliente == "corporativo":
            nombre = random.choice(self.empresas)
        else:
            nombre = random.choice(self.nombres_clientes)
        
        # Crear cliente con los nuevos campos simplificados
        cliente = Cliente(
            name=nombre,
            type=tipo_cliente
        )
        
        # Simular actividad histórica (algunos clientes con órdenes previas)
        if random.random() < 0.7:  # 70% de clientes con actividad previa
            self._simular_actividad_previa(cliente)
        
        return cliente
    
    def generar_ordenes(self, grafo, clientes: List[Cliente], 
                       cantidad_base: int = None) -> List[Orden]:
        """
        Genera órdenes basándose en los clientes y el grafo.
        
        Args:
            grafo: Grafo para obtener nodos de origen y destino
            clientes: Lista de clientes que pueden realizar órdenes
            cantidad_base: Cantidad base de órdenes
            
        Returns:
            List[Orden]: Lista de órdenes generadas
        """
        if not clientes:
            return []
        
        # Obtener nodos de almacenamiento y recarga como posibles orígenes
        nodos_almacenamiento = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.ALMACENAMIENTO)
        nodos_recarga = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.RECARGA)
        nodos_origen_posibles = nodos_almacenamiento + nodos_recarga
        
        if not nodos_origen_posibles:
            return []
        
        # Obtener nodos cliente como posibles destinos
        nodos_cliente = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.CLIENTE)
        
        if not nodos_cliente:
            return []
        
        # Determinar cantidad de órdenes
        if cantidad_base is None:
            # Generar entre 1-3 órdenes por cliente
            cantidad_base = len(clientes) * random.randint(1, 3)
        
        ordenes = []
        
        for _ in range(cantidad_base):
            orden = self._generar_orden_individual(clientes, nodos_origen_posibles, nodos_cliente)
            if orden:
                ordenes.append(orden)
        
        return ordenes
    
    def _generar_orden_individual(self, clientes: List[Cliente], 
                                 nodos_origen: List, nodos_destino: List) -> Optional[Orden]:
        """
        Genera una orden individual.
        
        Args:
            clientes: Lista de clientes disponibles
            nodos_origen: Lista de nodos de origen posibles
            nodos_destino: Lista de nodos de destino posibles
            
        Returns:
            Optional[Orden]: Orden generada o None si no es posible
        """
        if not clientes or not nodos_origen or not nodos_destino:
            return None
        
        # Seleccionar cliente aleatorio
        cliente = random.choice(clientes)
        
        # Seleccionar nodos de origen y destino
        nodo_origen = random.choice(nodos_origen)
        nodo_destino = random.choice(nodos_destino)
        
        # Determinar prioridad basada en tipo de cliente
        prioridades_por_tipo = {
            "regular": [
                ("low", 0.60),
                ("normal", 0.35),
                ("high", 0.05)
            ],
            "premium": [
                ("low", 0.30),
                ("normal", 0.50),
                ("high", 0.20)
            ],
            "corporativo": [
                ("normal", 0.40),
                ("high", 0.50),
                ("critical", 0.10)
            ],
            "vip": [
                ("high", 0.60),
                ("critical", 0.40)
            ]
        }
        
        prioridad = self._seleccionar_por_probabilidad(
            prioridades_por_tipo[cliente.type]
        )
        
        # Crear orden con los nuevos campos simplificados
        orden = Orden(
            client=cliente.name,
            client_id=cliente.client_id,
            origin=nodo_origen.element()['id'],
            destination=nodo_destino.element()['id'],
            priority=prioridad
        )
        
        # Calcular costo de ruta basado en distancia estimada
        distancia_estimada = random.uniform(5.0, 50.0)
        costo_base = distancia_estimada * 1.5
        
        # Aplicar multiplicador por prioridad
        multiplicador_prioridad = {
            "low": 1.0,
            "normal": 1.2,
            "high": 1.5,
            "critical": 2.0
        }
        
        costo_final = costo_base * multiplicador_prioridad.get(prioridad, 1.0)
        orden.set_route_cost(round(costo_final, 2))
        
        # Simular algunos estados avanzados para órdenes históricas
        if random.random() < 0.3:  # 30% de órdenes entregadas
            orden.mark_delivered()
        
        # Registrar en el cliente
        cliente.increment_orders()
        
        return orden
    
    def _simular_actividad_previa(self, cliente: Cliente) -> None:
        """
        Simula actividad previa para un cliente.
        
        Args:
            cliente: Cliente al cual agregar actividad
        """
        # Simular órdenes previas
        num_ordenes_previas = random.randint(1, 10)
        cliente.total_orders = num_ordenes_previas
    
    def _seleccionar_por_probabilidad(self, opciones_probabilidades: List[Tuple]) -> any:
        """
        Selecciona una opción basándose en probabilidades.
        
        Args:
            opciones_probabilidades: Lista de tuplas (opcion, probabilidad)
            
        Returns:
            Opción seleccionada
        """
        valor_aleatorio = random.random()
        acumulado = 0.0
        
        for opcion, probabilidad in opciones_probabilidades:
            acumulado += probabilidad
            if valor_aleatorio <= acumulado:
                return opcion
        
        # Fallback: retornar la primera opción
        return opciones_probabilidades[0][0]
    
    def generar_datos_completos(self, grafo, cantidad_clientes: int = None, 
                               cantidad_ordenes: int = None) -> Tuple[List[Cliente], List[Orden]]:
        """
        Genera un conjunto completo de clientes y órdenes.
        
        Args:
            grafo: Grafo base para la generación
            cantidad_clientes: Cantidad específica de clientes
            cantidad_ordenes: Cantidad específica de órdenes
            
        Returns:
            Tuple[List[Cliente], List[Orden]]: Clientes y órdenes generados
        """
        # Generar clientes
        clientes = self.generar_clientes(grafo, cantidad_clientes)
        
        # Generar órdenes basándose en los clientes
        ordenes = self.generar_ordenes(grafo, clientes, cantidad_ordenes)
        
        return clientes, ordenes

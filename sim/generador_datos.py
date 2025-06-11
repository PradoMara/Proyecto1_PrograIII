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
from domain.client import Cliente, TipoCliente, EstadoCliente
from domain.order import Orden, TipoOrden, PrioridadOrden, EstadoOrden


class GeneradorDatosSimulacion:
    """
    Genera datos de simulación para clientes y órdenes basándose en un grafo.
    """
    
    def __init__(self, semilla: Optional[int] = None):
        """
        Inicializa el generador de datos.
        
        Args:
            semilla: Semilla para la generación aleatoria
        """
        if semilla:
            random.seed(semilla)
        
        # Configuraciones para generación realista
        self.nombres_clientes = [
            "Juan Pérez", "María González", "Carlos Rodríguez", "Ana López",
            "Pedro Martín", "Laura García", "Diego Hernández", "Carmen Silva",
            "Roberto Torres", "Elena Morales", "Fernando Castro", "Isabel Ruiz",
            "Manuel Vargas", "Patricia Jiménez", "Antonio Flores", "Rosa Delgado",
            "José Mendoza", "Francisca Vega", "Ricardo Peña", "Mónica Soto",
            "Alejandro Reyes", "Gabriela Ortiz", "Miguel Romero", "Claudia Núñez",
            "Daniel Guerrero", "Beatriz Contreras", "Sergio Molina", "Valeria Cruz"
        ]
        
        self.empresas = [
            "Tech Solutions SA", "Logística Moderna", "Comercial Central",
            "Servicios Premium", "Distribuidora Norte", "Mayorista del Sur",
            "Importadora Elite", "Retail Express", "Corporate Services",
            "Industrial Group", "Trading Company", "Business Solutions"
        ]
        
        self.productos_servicios = [
            "Paquete documentos", "Equipos electrónicos", "Productos farmacéuticos",
            "Alimentos perecederos", "Material de oficina", "Componentes industriales",
            "Libros y material educativo", "Ropa y textiles", "Herramientas",
            "Repuestos automotriz", "Productos de belleza", "Artículos deportivos",
            "Medicamentos urgentes", "Equipos médicos", "Software licenciado"
        ]
    
    def generar_clientes(self, grafo, cantidad: int = None) -> List[Cliente]:
        """
        Genera clientes basándose en los nodos cliente del grafo.
        
        Args:
            grafo: Grafo del cual obtener los nodos cliente
            cantidad: Cantidad específica de clientes (si no se especifica, usa todos los nodos cliente)
            
        Returns:
            List[Cliente]: Lista de clientes generados
        """
        # Obtener nodos cliente del grafo
        nodos_cliente = BuscadorNodos.buscar_nodos_por_rol(grafo, RolNodo.CLIENTE)
        
        if not nodos_cliente:
            return []
        
        # Determinar cantidad de clientes a generar
        if cantidad is None:
            cantidad = len(nodos_cliente)
        else:
            cantidad = min(cantidad, len(nodos_cliente))
        
        clientes = []
        nodos_seleccionados = random.sample(nodos_cliente, cantidad)
        
        for nodo in nodos_seleccionados:
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
        nodo_info = nodo.element()
        
        # Determinar tipo de cliente con probabilidades realistas
        tipos_probabilidades = [
            (TipoCliente.REGULAR, 0.60),
            (TipoCliente.PREMIUM, 0.25),
            (TipoCliente.CORPORATIVO, 0.10),
            (TipoCliente.VIP, 0.05)
        ]
        
        tipo_cliente = self._seleccionar_por_probabilidad(tipos_probabilidades)
        
        # Generar nombre según el tipo
        if tipo_cliente == TipoCliente.CORPORATIVO:
            nombre = random.choice(self.empresas)
            email = f"contacto@{nombre.lower().replace(' ', '').replace('sa', '')}.com"
        else:
            nombre = random.choice(self.nombres_clientes)
            email = f"{nombre.lower().replace(' ', '.')}.{random.randint(100, 999)}@email.com"
        
        # Configurar límites de crédito según tipo
        limites_credito = {
            TipoCliente.REGULAR: (500, 2000),
            TipoCliente.PREMIUM: (2000, 5000),
            TipoCliente.CORPORATIVO: (5000, 50000),
            TipoCliente.VIP: (10000, 100000)
        }
        
        limite_min, limite_max = limites_credito[tipo_cliente]
        limite_credito = random.uniform(limite_min, limite_max)
        
        # Generar otros atributos
        cliente = Cliente(
            nombre=nombre,
            tipo=tipo_cliente,
            nodo_ubicacion=nodo_info['id'],
            email=email,
            telefono=f"+56{random.randint(900000000, 999999999)}",
            direccion=f"{nodo_info['nombre']} #{random.randint(100, 9999)}",
            limite_credito=limite_credito,
            descuento_base=random.uniform(0.0, 0.05) if tipo_cliente != TipoCliente.REGULAR else 0.0
        )
        
        # Simular actividad histórica (algunos clientes con historial)
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
            cantidad_base: Cantidad base de órdenes (se puede modificar según clientes activos)
            
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
        
        # Determinar cantidad de órdenes
        clientes_activos = [c for c in clientes if c.estado == EstadoCliente.ACTIVO]
        if cantidad_base is None:
            # Generar entre 1-3 órdenes por cliente activo
            cantidad_base = len(clientes_activos) * random.randint(1, 3)
        
        ordenes = []
        
        for _ in range(cantidad_base):
            orden = self._generar_orden_individual(
                clientes_activos, nodos_origen_posibles
            )
            if orden:
                ordenes.append(orden)
        
        return ordenes
    
    def _generar_orden_individual(self, clientes: List[Cliente], 
                                 nodos_origen: List) -> Optional[Orden]:
        """
        Genera una orden individual.
        
        Args:
            clientes: Lista de clientes disponibles
            nodos_origen: Lista de nodos de origen posibles
            
        Returns:
            Optional[Orden]: Orden generada o None si no es posible
        """
        if not clientes or not nodos_origen:
            return None
        
        # Seleccionar cliente
        cliente = random.choice(clientes)
        
        # Seleccionar nodo de origen
        nodo_origen = random.choice(nodos_origen)
        
        # Determinar tipo de orden
        tipos_probabilidades = [
            (TipoOrden.ENTREGA, 0.70),
            (TipoOrden.RECOGIDA, 0.15),
            (TipoOrden.COMPRA, 0.10),
            (TipoOrden.SERVICIO, 0.05)
        ]
        
        tipo_orden = self._seleccionar_por_probabilidad(tipos_probabilidades)
        
        # Determinar prioridad basada en tipo de cliente
        prioridades_por_tipo = {
            TipoCliente.REGULAR: [
                (PrioridadOrden.BAJA, 0.60),
                (PrioridadOrden.MEDIA, 0.35),
                (PrioridadOrden.ALTA, 0.05)
            ],
            TipoCliente.PREMIUM: [
                (PrioridadOrden.BAJA, 0.30),
                (PrioridadOrden.MEDIA, 0.50),
                (PrioridadOrden.ALTA, 0.20)
            ],
            TipoCliente.CORPORATIVO: [
                (PrioridadOrden.MEDIA, 0.40),
                (PrioridadOrden.ALTA, 0.50),
                (PrioridadOrden.CRITICA, 0.10)
            ],
            TipoCliente.VIP: [
                (PrioridadOrden.ALTA, 0.60),
                (PrioridadOrden.CRITICA, 0.40)
            ]
        }
        
        prioridad = self._seleccionar_por_probabilidad(
            prioridades_por_tipo[cliente.tipo]
        )
        
        # Generar valores y características
        valor_base = self._generar_valor_orden(cliente.tipo, tipo_orden)
        peso_kg = random.uniform(0.1, 50.0)
        descripcion = random.choice(self.productos_servicios)
        
        # Crear fechas de entrega
        dias_entrega = {
            PrioridadOrden.CRITICA: random.randint(1, 1),
            PrioridadOrden.ALTA: random.randint(1, 2),
            PrioridadOrden.MEDIA: random.randint(2, 5),
            PrioridadOrden.BAJA: random.randint(5, 10)
        }
        
        fecha_entrega = datetime.now() + timedelta(days=dias_entrega[prioridad])
        
        # Crear orden
        orden = Orden(
            cliente_id=cliente.cliente_id,
            tipo=tipo_orden,
            nodo_origen=nodo_origen.element()['id'],
            nodo_destino=cliente.nodo_ubicacion,
            prioridad=prioridad,
            valor_base=valor_base,
            descripcion=descripcion,
            peso_kg=peso_kg,
            dimensiones=f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)}cm",
            fecha_entrega_solicitada=fecha_entrega
        )
        
        # Simular algunos estados avanzados para órdenes históricas
        if random.random() < 0.3:  # 30% de órdenes tienen progreso
            self._simular_progreso_orden(orden)
        
        # Calcular costos
        distancia_estimada = random.uniform(1.0, 50.0)  # Simulada
        orden.estimar_costo_envio(distancia_estimada)
        descuento_cliente = cliente.calcular_descuento_aplicable(orden.valor_base)
        orden.calcular_costo_total(descuento_cliente / orden.valor_base)
        
        # Registrar en el cliente
        cliente.registrar_pedido(orden.orden_id, orden.costo_total)
        
        return orden
    
    def _simular_actividad_previa(self, cliente: Cliente) -> None:
        """
        Simula actividad previa para un cliente.
        
        Args:
            cliente: Cliente al cual agregar actividad
        """
        # Simular fecha de registro anterior
        dias_registro = random.randint(30, 365)
        cliente.fecha_registro = datetime.now() - timedelta(days=dias_registro)
        
        # Simular pedidos previos
        num_pedidos_previos = random.randint(1, 20)
        
        for _ in range(num_pedidos_previos):
            valor_pedido = random.uniform(50.0, 1000.0)
            pedido_id = f"HIST_{uuid.uuid4().hex[:6]}"
            cliente.registrar_pedido(pedido_id, valor_pedido)
            
            # Simular completados y cancelados
            if random.random() < 0.85:  # 85% completados
                cliente.completar_pedido(pedido_id)
            elif random.random() < 0.10:  # 10% cancelados
                cliente.cancelar_pedido(pedido_id, valor_pedido)
    
    def _simular_progreso_orden(self, orden: Orden) -> None:
        """
        Simula progreso en una orden (para órdenes históricas).
        
        Args:
            orden: Orden a la cual simular progreso
        """
        estados_progresivos = [
            EstadoOrden.CONFIRMADA,
            EstadoOrden.EN_PREPARACION,
            EstadoOrden.EN_TRANSITO,
            EstadoOrden.ENTREGADA
        ]
        
        # Determinar hasta qué estado progresó
        progreso = random.randint(1, len(estados_progresivos))
        
        for i in range(progreso):
            estado = estados_progresivos[i]
            orden.cambiar_estado(estado, f"Progreso simulado a {estado.value}")
            
            # Simular retraso entre estados
            if i > 0:
                retraso = timedelta(hours=random.randint(1, 24))
                if estado == EstadoOrden.CONFIRMADA:
                    orden.fecha_confirmacion -= retraso
                elif estado == EstadoOrden.EN_PREPARACION:
                    orden.fecha_inicio_preparacion -= retraso
                elif estado == EstadoOrden.EN_TRANSITO:
                    orden.fecha_inicio_transito -= retraso
                elif estado == EstadoOrden.ENTREGADA:
                    orden.fecha_entrega_real -= retraso
    
    def _generar_valor_orden(self, tipo_cliente: TipoCliente, tipo_orden: TipoOrden) -> float:
        """
        Genera un valor para la orden basado en el tipo de cliente y orden.
        
        Args:
            tipo_cliente: Tipo de cliente
            tipo_orden: Tipo de orden
            
        Returns:
            float: Valor generado
        """
        # Rangos base por tipo de orden
        rangos_base = {
            TipoOrden.COMPRA: (50, 500),
            TipoOrden.ENTREGA: (20, 200),
            TipoOrden.RECOGIDA: (15, 100),
            TipoOrden.INTERCAMBIO: (30, 300),
            TipoOrden.SERVICIO: (100, 1000)
        }
        
        # Multiplicadores por tipo de cliente
        multiplicadores = {
            TipoCliente.REGULAR: 1.0,
            TipoCliente.PREMIUM: 1.5,
            TipoCliente.CORPORATIVO: 3.0,
            TipoCliente.VIP: 5.0
        }
        
        valor_min, valor_max = rangos_base[tipo_orden]
        multiplicador = multiplicadores[tipo_cliente]
        
        valor = random.uniform(valor_min, valor_max) * multiplicador
        return round(valor, 2)
    
    def _seleccionar_por_probabilidad(self, opciones_probabilidades: List[Tuple]) -> any:
        """
        Selecciona una opción basada en probabilidades.
        
        Args:
            opciones_probabilidades: Lista de tuplas (opcion, probabilidad)
            
        Returns:
            Opción seleccionada
        """
        numero_aleatorio = random.random()
        probabilidad_acumulada = 0.0
        
        for opcion, probabilidad in opciones_probabilidades:
            probabilidad_acumulada += probabilidad
            if numero_aleatorio <= probabilidad_acumulada:
                return opcion
        
        # Fallback: retornar la primera opción
        return opciones_probabilidades[0][0]
    
    def generar_datos_completos(self, grafo, cantidad_clientes: int = None, 
                               cantidad_ordenes: int = None) -> Tuple[List[Cliente], List[Orden]]:
        """
        Genera un conjunto completo de datos de simulación.
        
        Args:
            grafo: Grafo base para la simulación
            cantidad_clientes: Cantidad específica de clientes
            cantidad_ordenes: Cantidad específica de órdenes
            
        Returns:
            Tuple[List[Cliente], List[Orden]]: Clientes y órdenes generados
        """
        # Generar clientes
        clientes = self.generar_clientes(grafo, cantidad_clientes)
        
        # Generar órdenes
        ordenes = self.generar_ordenes(grafo, clientes, cantidad_ordenes)
        
        return clientes, ordenes

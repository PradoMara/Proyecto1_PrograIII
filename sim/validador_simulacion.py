from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math


class TipoError(Enum):
    CRITICO = "critico"      # Bloquea la simulación
    ADVERTENCIA = "advertencia"  # Permite continuar con advertencia
    INFORMATIVO = "informativo"  # Solo información


@dataclass
class ErrorValidacion:
    tipo: TipoError
    codigo: str
    mensaje: str
    parametro: Optional[str] = None
    valor_actual: Optional[Any] = None
    valor_recomendado: Optional[Any] = None
    
    def __str__(self) -> str:
        icono = {
            TipoError.CRITICO: "❌",
            TipoError.ADVERTENCIA: "⚠️",
            TipoError.INFORMATIVO: "ℹ️"
        }
        return f"{icono[self.tipo]} {self.mensaje}"


@dataclass
class ResultadoValidacion:
    es_valida: bool
    errores: List[ErrorValidacion]
    advertencias: List[ErrorValidacion]
    informacion: List[ErrorValidacion]
    
    def __str__(self) -> str:
        if self.es_valida:
            return "✅ Configuración válida"
        else:
            return f"❌ Configuración inválida ({len(self.errores)} errores)"
    
    @property
    def tiene_errores_criticos(self) -> bool:
        """Verifica si hay errores críticos"""
        return any(error.tipo == TipoError.CRITICO for error in self.errores)
    
    @property
    def puede_ejecutar(self) -> bool:
        """Verifica si se puede ejecutar la simulación"""
        return self.es_valida and not self.tiene_errores_criticos


class ValidadorSimulacion:

    def __init__(self):
        # Límites y configuraciones por defecto
        self.limites = {
            'nodos': {'min': 1, 'max': 1000, 'recomendado_max': 500},
            'probabilidad_arista': {'min': 0.0, 'max': 1.0, 'recomendado_min': 0.1, 'recomendado_max': 0.8},
            'porcentajes': {'tolerancia': 0.1, 'min_individual': 0.0, 'max_individual': 100.0},
            'semilla': {'min': 1, 'max': 999999},
            'clientes': {'min_por_nodo_cliente': 1, 'max_por_nodo_cliente': 10},
            'ordenes': {'min_por_cliente': 1, 'max_por_cliente': 50},
            'drones': {
                'bateria_min': 100.0, 'bateria_max': 10000.0,
                'consumo_min': 0.1, 'consumo_max': 10.0,
                'autonomia_min': 10.0, 'autonomia_max': 1000.0
            },
            'estaciones': {
                'capacidad_min': 1, 'capacidad_max': 20,
                'costo_min': 0.1, 'costo_max': 100.0
            },
            'rutas': {
                'max_distancia': 1000.0,
                'max_tiempo': 24.0,  # horas
                'margen_bateria': 5.0  # porcentaje mínimo
            }
        }
        
        # Configuraciones de rendimiento
        self.rendimiento = {
            'nodos_rapido': 50,      # Simulación rápida
            'nodos_normal': 200,     # Simulación normal
            'nodos_lento': 500,      # Simulación lenta
            'tiempo_estimado_por_nodo': 0.01  # segundos por nodo
        }
        
        # Configuraciones de escenarios
        self.escenarios = {
            'pequena_ciudad': {
                'nodos': (10, 50),
                'densidad': (0.2, 0.4),
                'clientes_por_nodo': (1, 3)
            },
            'ciudad_mediana': {
                'nodos': (50, 200),
                'densidad': (0.15, 0.35),
                'clientes_por_nodo': (2, 8)
            },
            'ciudad_grande': {
                'nodos': (200, 500),
                'densidad': (0.1, 0.3),
                'clientes_por_nodo': (5, 15)
            }
        }
    
    def validar_configuracion_completa(self, config: Dict[str, Any]) -> ResultadoValidacion:
        errores = []
        advertencias = []
        informacion = []
        
        # 1. Validar parámetros básicos
        resultado_basicos = self._validar_parametros_basicos(config)
        errores.extend(resultado_basicos.errores)
        advertencias.extend(resultado_basicos.advertencias)
        informacion.extend(resultado_basicos.informacion)
        
        # 2. Validar distribución de roles
        resultado_roles = self._validar_distribucion_roles(config)
        errores.extend(resultado_roles.errores)
        advertencias.extend(resultado_roles.advertencias)
        informacion.extend(resultado_roles.informacion)
        
        # 3. Validar conectividad y aristas
        resultado_conectividad = self._validar_conectividad(config)
        errores.extend(resultado_conectividad.errores)
        advertencias.extend(resultado_conectividad.advertencias)
        informacion.extend(resultado_conectividad.informacion)
        
        # 4. Validar parámetros de órdenes y clientes
        resultado_datos = self._validar_parametros_datos(config)
        errores.extend(resultado_datos.errores)
        advertencias.extend(resultado_datos.advertencias)
        informacion.extend(resultado_datos.informacion)
        
        # 5. Validar rendimiento y optimizaciones
        resultado_rendimiento = self._validar_rendimiento(config)
        errores.extend(resultado_rendimiento.errores)
        advertencias.extend(resultado_rendimiento.advertencias)
        informacion.extend(resultado_rendimiento.informacion)
        
        # 6. Validar lógica de negocio
        resultado_negocio = self._validar_logica_negocio(config)
        errores.extend(resultado_negocio.errores)
        advertencias.extend(resultado_negocio.advertencias)
        informacion.extend(resultado_negocio.informacion)
        
        # Determinar si la configuración es válida
        es_valida = not any(error.tipo == TipoError.CRITICO for error in errores)
        
        return ResultadoValidacion(
            es_valida=es_valida,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def _validar_parametros_basicos(self, config: Dict[str, Any]) -> ResultadoValidacion:
        errores = []
        advertencias = []
        informacion = []
        
        # Validar número de nodos
        num_nodos = config.get('num_nodos', 0)
        if num_nodos < self.limites['nodos']['min']:
            errores.append(ErrorValidacion(
                tipo=TipoError.CRITICO,
                codigo="NODOS_MINIMO",
                mensaje=f"El número de nodos debe ser al menos {self.limites['nodos']['min']}",
                parametro="num_nodos",
                valor_actual=num_nodos,
                valor_recomendado=self.limites['nodos']['min']
            ))
        elif num_nodos > self.limites['nodos']['max']:
            errores.append(ErrorValidacion(
                tipo=TipoError.CRITICO,
                codigo="NODOS_MAXIMO",
                mensaje=f"El número de nodos no puede exceder {self.limites['nodos']['max']}",
                parametro="num_nodos",
                valor_actual=num_nodos,
                valor_recomendado=self.limites['nodos']['recomendado_max']
            ))
        elif num_nodos > self.limites['nodos']['recomendado_max']:
            advertencias.append(ErrorValidacion(
                tipo=TipoError.ADVERTENCIA,
                codigo="NODOS_LENTO",
                mensaje=f"Con {num_nodos} nodos la simulación puede ser lenta",
                parametro="num_nodos",
                valor_actual=num_nodos,
                valor_recomendado=self.limites['nodos']['recomendado_max']
            ))
        
        # Validar probabilidad de arista (solo si está presente)
        if 'prob_arista' in config:
            prob_arista = config['prob_arista']
            if not (self.limites['probabilidad_arista']['min'] <= prob_arista <= self.limites['probabilidad_arista']['max']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="PROB_ARISTA_RANGO",
                    mensaje=f"La probabilidad de arista debe estar entre {self.limites['probabilidad_arista']['min']} y {self.limites['probabilidad_arista']['max']}",
                    parametro="prob_arista",
                    valor_actual=prob_arista,
                    valor_recomendado=0.3
                ))
            elif prob_arista < self.limites['probabilidad_arista']['recomendado_min']:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="PROB_ARISTA_BAJA",
                    mensaje="Probabilidad de arista muy baja, el grafo puede estar poco conectado",
                    parametro="prob_arista",
                    valor_actual=prob_arista,
                    valor_recomendado=self.limites['probabilidad_arista']['recomendado_min']
                ))
            elif prob_arista > self.limites['probabilidad_arista']['recomendado_max']:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="PROB_ARISTA_ALTA",
                    mensaje="Probabilidad de arista muy alta, el grafo puede ser muy denso",
                    parametro="prob_arista",
                    valor_actual=prob_arista,
                    valor_recomendado=self.limites['probabilidad_arista']['recomendado_max']
                ))
        
        # Validar semilla (solo si está presente)
        if 'semilla' in config:
            semilla = config['semilla']
            if not (self.limites['semilla']['min'] <= semilla <= self.limites['semilla']['max']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="SEMILLA_RANGO",
                    mensaje=f"La semilla debe estar entre {self.limites['semilla']['min']} y {self.limites['semilla']['max']}",
                    parametro="semilla",
                    valor_actual=semilla,
                    valor_recomendado=42
                ))
            else:
                informacion.append(ErrorValidacion(
                    tipo=TipoError.INFORMATIVO,
                    codigo="SEMILLA_CONFIGURADA",
                    mensaje=f"Simulación reproducible con semilla {semilla}",
                    parametro="semilla",
                    valor_actual=semilla
                ))
        
        return ResultadoValidacion(
            es_valida=len([e for e in errores if e.tipo == TipoError.CRITICO]) == 0,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def _validar_distribucion_roles(self, config: Dict[str, Any]) -> ResultadoValidacion:
        errores = []
        advertencias = []
        informacion = []
        
        pct_almacenamiento = config.get('pct_almacenamiento', 0.0)
        pct_recarga = config.get('pct_recarga', 0.0)
        pct_cliente = config.get('pct_cliente', 0.0)
        num_nodos = config.get('num_nodos', 0)
        
        # Validar rangos individuales solo si están presentes
        if 'pct_almacenamiento' in config:
            if not (self.limites['porcentajes']['min_individual'] <= pct_almacenamiento <= self.limites['porcentajes']['max_individual']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="PORCENTAJE_ALMACENAMIENTO_RANGO",
                    mensaje=f"El porcentaje de almacenamiento debe estar entre 0% y 100%",
                    parametro="pct_almacenamiento",
                    valor_actual=pct_almacenamiento,
                    valor_recomendado=20.0
                ))
        
        if 'pct_recarga' in config:
            if not (self.limites['porcentajes']['min_individual'] <= pct_recarga <= self.limites['porcentajes']['max_individual']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="PORCENTAJE_RECARGA_RANGO",
                    mensaje=f"El porcentaje de recarga debe estar entre 0% y 100%",
                    parametro="pct_recarga",
                    valor_actual=pct_recarga,
                    valor_recomendado=30.0
                ))
        
        if 'pct_cliente' in config:
            if not (self.limites['porcentajes']['min_individual'] <= pct_cliente <= self.limites['porcentajes']['max_individual']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="PORCENTAJE_CLIENTE_RANGO",
                    mensaje=f"El porcentaje de cliente debe estar entre 0% y 100%",
                    parametro="pct_cliente",
                    valor_actual=pct_cliente,
                    valor_recomendado=50.0
                ))
        
        # Validar suma de porcentajes solo si todos están presentes
        if all(key in config for key in ['pct_almacenamiento', 'pct_recarga', 'pct_cliente']):
            suma_porcentajes = pct_almacenamiento + pct_recarga + pct_cliente
            if abs(suma_porcentajes - 100.0) > self.limites['porcentajes']['tolerancia']:
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="PORCENTAJES_SUMA",
                    mensaje=f"Los porcentajes deben sumar 100% (actual: {suma_porcentajes:.1f}%)",
                    parametro="porcentajes",
                    valor_actual=suma_porcentajes,
                    valor_recomendado=100.0
                ))
            
            # Validar lógica de negocio para roles
            if num_nodos >= 2:
                if pct_almacenamiento == 0:
                    advertencias.append(ErrorValidacion(
                        tipo=TipoError.ADVERTENCIA,
                        codigo="SIN_ALMACENAMIENTO",
                        mensaje="Se recomienda al menos 1 nodo de almacenamiento",
                        parametro="pct_almacenamiento",
                        valor_actual=pct_almacenamiento,
                        valor_recomendado=20.0
                    ))
                
                if pct_recarga == 0:
                    advertencias.append(ErrorValidacion(
                        tipo=TipoError.ADVERTENCIA,
                        codigo="SIN_RECARGA",
                        mensaje="Se recomienda al menos 1 nodo de recarga",
                        parametro="pct_recarga",
                        valor_actual=pct_recarga,
                        valor_recomendado=30.0
                    ))
            
            # Información sobre distribución estimada
            if num_nodos > 0 and abs(suma_porcentajes - 100.0) <= self.limites['porcentajes']['tolerancia']:
                nodos_alm = max(1, round(num_nodos * pct_almacenamiento / 100))
                nodos_rec = max(1, round(num_nodos * pct_recarga / 100))
                nodos_cli = num_nodos - nodos_alm - nodos_rec
                
                informacion.append(ErrorValidacion(
                    tipo=TipoError.INFORMATIVO,
                    codigo="DISTRIBUCION_ESTIMADA",
                    mensaje=f"Distribución estimada: {nodos_alm} almacenamiento, {nodos_rec} recarga, {nodos_cli} cliente",
                    parametro="distribucion",
                    valor_actual=f"{pct_almacenamiento:.1f}%/{pct_recarga:.1f}%/{pct_cliente:.1f}%"
                ))
        
        return ResultadoValidacion(
            es_valida=len([e for e in errores if e.tipo == TipoError.CRITICO]) == 0,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def _validar_conectividad(self, config: Dict[str, Any]) -> ResultadoValidacion:
        errores = []
        advertencias = []
        informacion = []
        
        # Solo validar si ambos parámetros están presentes
        if 'num_nodos' in config and 'prob_arista' in config:
            num_nodos = config['num_nodos']
            prob_arista = config['prob_arista']
            
            if num_nodos > 1:
                # Calcular aristas mínimas necesarias para conectividad
                aristas_minimas = num_nodos - 1
                
                # Calcular aristas máximas posibles
                aristas_maximas = num_nodos * (num_nodos - 1) // 2
                
                # Calcular aristas estimadas
                aristas_estimadas = int(aristas_minimas + prob_arista * (aristas_maximas - aristas_minimas))
                
                # Calcular densidad estimada
                densidad_estimada = aristas_estimadas / aristas_maximas if aristas_maximas > 0 else 0
                
                informacion.append(ErrorValidacion(
                    tipo=TipoError.INFORMATIVO,
                    codigo="ARISTAS_ESTIMADAS",
                    mensaje=f"Aristas estimadas: {aristas_estimadas} (densidad: {densidad_estimada:.3f})",
                    parametro="aristas",
                    valor_actual=aristas_estimadas
                ))
                
                # Validar densidad mínima para conectividad
                if densidad_estimada < 0.1:
                    advertencias.append(ErrorValidacion(
                        tipo=TipoError.ADVERTENCIA,
                        codigo="DENSIDAD_BAJA",
                        mensaje="Densidad muy baja, verificar conectividad",
                        parametro="prob_arista",
                        valor_actual=prob_arista,
                        valor_recomendado=0.2
                    ))
                
                # Validar densidad máxima para rendimiento
                if densidad_estimada > 0.8:
                    advertencias.append(ErrorValidacion(
                        tipo=TipoError.ADVERTENCIA,
                        codigo="DENSIDAD_ALTA",
                        mensaje="Densidad muy alta, puede afectar rendimiento",
                        parametro="prob_arista",
                        valor_actual=prob_arista,
                        valor_recomendado=0.5
                    ))
        
        return ResultadoValidacion(
            es_valida=True,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def _validar_parametros_datos(self, config: Dict[str, Any]) -> ResultadoValidacion:
        errores = []
        advertencias = []
        informacion = []
        
        # Validar parámetros de clientes
        if 'clientes_por_nodo' in config:
            clientes_por_nodo = config['clientes_por_nodo']
            if not (self.limites['clientes']['min_por_nodo_cliente'] <= clientes_por_nodo <= self.limites['clientes']['max_por_nodo_cliente']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="CLIENTES_POR_NODO_RANGO",
                    mensaje=f"Clientes por nodo debe estar entre {self.limites['clientes']['min_por_nodo_cliente']} y {self.limites['clientes']['max_por_nodo_cliente']}",
                    parametro="clientes_por_nodo",
                    valor_actual=clientes_por_nodo,
                    valor_recomendado=3
                ))
        
        # Validar parámetros de órdenes
        if 'ordenes_por_cliente' in config:
            ordenes_por_cliente = config['ordenes_por_cliente']
            if not (self.limites['ordenes']['min_por_cliente'] <= ordenes_por_cliente <= self.limites['ordenes']['max_por_cliente']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="ORDENES_POR_CLIENTE_RANGO",
                    mensaje=f"Órdenes por cliente debe estar entre {self.limites['ordenes']['min_por_cliente']} y {self.limites['ordenes']['max_por_cliente']}",
                    parametro="ordenes_por_cliente",
                    valor_actual=ordenes_por_cliente,
                    valor_recomendado=10
                ))
        
        # Validar parámetros de drones
        if 'bateria_dron' in config:
            bateria = config['bateria_dron']
            if not (self.limites['drones']['bateria_min'] <= bateria <= self.limites['drones']['bateria_max']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="BATERIA_DRON_RANGO",
                    mensaje=f"Batería del dron debe estar entre {self.limites['drones']['bateria_min']} y {self.limites['drones']['bateria_max']} mAh",
                    parametro="bateria_dron",
                    valor_actual=bateria,
                    valor_recomendado=1000.0
                ))
        
        if 'consumo_dron' in config:
            consumo = config['consumo_dron']
            if not (self.limites['drones']['consumo_min'] <= consumo <= self.limites['drones']['consumo_max']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="CONSUMO_DRON_RANGO",
                    mensaje=f"Consumo del dron debe estar entre {self.limites['drones']['consumo_min']} y {self.limites['drones']['consumo_max']} mAh/km",
                    parametro="consumo_dron",
                    valor_actual=consumo,
                    valor_recomendado=2.0
                ))
        
        # Validar parámetros de estaciones de recarga
        if 'capacidad_estacion' in config:
            capacidad = config['capacidad_estacion']
            if not (self.limites['estaciones']['capacidad_min'] <= capacidad <= self.limites['estaciones']['capacidad_max']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="CAPACIDAD_ESTACION_RANGO",
                    mensaje=f"Capacidad de estación debe estar entre {self.limites['estaciones']['capacidad_min']} y {self.limites['estaciones']['capacidad_max']} drones",
                    parametro="capacidad_estacion",
                    valor_actual=capacidad,
                    valor_recomendado=5
                ))
        
        if 'costo_recarga' in config:
            costo = config['costo_recarga']
            if not (self.limites['estaciones']['costo_min'] <= costo <= self.limites['estaciones']['costo_max']):
                errores.append(ErrorValidacion(
                    tipo=TipoError.CRITICO,
                    codigo="COSTO_RECARGA_RANGO",
                    mensaje=f"Costo de recarga debe estar entre ${self.limites['estaciones']['costo_min']} y ${self.limites['estaciones']['costo_max']}",
                    parametro="costo_recarga",
                    valor_actual=costo,
                    valor_recomendado=5.0
                ))
        
        # Validar parámetros de rutas
        if 'max_distancia_ruta' in config:
            max_dist = config['max_distancia_ruta']
            if max_dist > self.limites['rutas']['max_distancia']:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="DISTANCIA_RUTA_ALTA",
                    mensaje=f"Distancia máxima de ruta muy alta ({max_dist}km), puede afectar la autonomía del dron",
                    parametro="max_distancia_ruta",
                    valor_actual=max_dist,
                    valor_recomendado=self.limites['rutas']['max_distancia']
                ))
        
        if 'margen_bateria' in config:
            margen = config['margen_bateria']
            if margen < self.limites['rutas']['margen_bateria']:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="MARGEN_BATERIA_BAJO",
                    mensaje=f"Margen de batería muy bajo ({margen}%), se recomienda al menos {self.limites['rutas']['margen_bateria']}%",
                    parametro="margen_bateria",
                    valor_actual=margen,
                    valor_recomendado=self.limites['rutas']['margen_bateria']
                ))
        
        # Validar escenarios específicos
        num_nodos = config.get('num_nodos', 0)
        prob_arista = config.get('prob_arista', 0.0)
        
        if num_nodos > 0 and prob_arista > 0:
            # Determinar escenario recomendado
            escenario_recomendado = self._determinar_escenario_recomendado(num_nodos, prob_arista)
            if escenario_recomendado:
                informacion.append(ErrorValidacion(
                    tipo=TipoError.INFORMATIVO,
                    codigo="ESCENARIO_RECOMENDADO",
                    mensaje=f"Configuración similar a escenario: {escenario_recomendado}",
                    parametro="escenario",
                    valor_actual=f"{num_nodos} nodos, {prob_arista:.2f} densidad"
                ))
        
        return ResultadoValidacion(
            es_valida=len([e for e in errores if e.tipo == TipoError.CRITICO]) == 0,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def _determinar_escenario_recomendado(self, num_nodos: int, prob_arista: float) -> Optional[str]:
        for nombre, config in self.escenarios.items():
            min_nodos, max_nodos = config['nodos']
            min_densidad, max_densidad = config['densidad']
            
            if min_nodos <= num_nodos <= max_nodos and min_densidad <= prob_arista <= max_densidad:
                return nombre
        return None
    
    def _validar_rendimiento(self, config: Dict[str, Any]) -> ResultadoValidacion:
        errores = []
        advertencias = []
        informacion = []
        
        num_nodos = config.get('num_nodos', 0)
        
        # Estimar tiempo de simulación
        tiempo_estimado = num_nodos * self.rendimiento['tiempo_estimado_por_nodo']
        
        if num_nodos > self.rendimiento['nodos_lento']:
            advertencias.append(ErrorValidacion(
                tipo=TipoError.ADVERTENCIA,
                codigo="RENDIMIENTO_LENTO",
                mensaje=f"Simulación estimada: {tiempo_estimado:.1f}s (puede ser lenta)",
                parametro="num_nodos",
                valor_actual=num_nodos,
                valor_recomendado=self.rendimiento['nodos_normal']
            ))
        elif num_nodos > self.rendimiento['nodos_normal']:
            advertencias.append(ErrorValidacion(
                tipo=TipoError.ADVERTENCIA,
                codigo="RENDIMIENTO_NORMAL",
                mensaje=f"Simulación estimada: {tiempo_estimado:.1f}s",
                parametro="num_nodos",
                valor_actual=num_nodos
            ))
        else:
            informacion.append(ErrorValidacion(
                tipo=TipoError.INFORMATIVO,
                codigo="RENDIMIENTO_RAPIDO",
                mensaje=f"Simulación estimada: {tiempo_estimado:.1f}s",
                parametro="num_nodos",
                valor_actual=num_nodos
            ))
        
        return ResultadoValidacion(
            es_valida=True,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def _validar_logica_negocio(self, config: Dict[str, Any]) -> ResultadoValidacion:

        errores = []
        advertencias = []
        informacion = []
        
        num_nodos = config.get('num_nodos', 0)
        pct_almacenamiento = config.get('pct_almacenamiento', 0.0)
        pct_recarga = config.get('pct_recarga', 0.0)
        pct_cliente = config.get('pct_cliente', 0.0)
        
        # Validar proporciones recomendadas para diferentes escenarios
        if num_nodos >= 10:
            # Para redes grandes, validar proporciones balanceadas
            if pct_cliente < 40:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="POCOS_CLIENTES",
                    mensaje="Proporción de clientes muy baja para una red de este tamaño",
                    parametro="pct_cliente",
                    valor_actual=pct_cliente,
                    valor_recomendado=50.0
                ))
            
            if pct_almacenamiento > 30:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="MUCHOS_ALMACENES",
                    mensaje="Proporción de almacenamiento muy alta",
                    parametro="pct_almacenamiento",
                    valor_actual=pct_almacenamiento,
                    valor_recomendado=20.0
                ))
        
        # Validar escenarios específicos
        if num_nodos == 1:
            # Con un solo nodo, debe ser cliente o almacenamiento
            if pct_recarga > 0:
                advertencias.append(ErrorValidacion(
                    tipo=TipoError.ADVERTENCIA,
                    codigo="NODO_UNICO_RECARGA",
                    mensaje="Con un solo nodo, no es recomendable que sea de recarga",
                    parametro="pct_recarga",
                    valor_actual=pct_recarga,
                    valor_recomendado=0.0
                ))
        
        return ResultadoValidacion(
            es_valida=True,
            errores=errores,
            advertencias=advertencias,
            informacion=informacion
        )
    
    def obtener_configuracion_recomendada(self, num_nodos: int, escenario: str = "balanceado") -> Dict[str, Any]:
    
        configuraciones = {
            "balanceado": {
                "pct_almacenamiento": 20.0,
                "pct_recarga": 30.0,
                "pct_cliente": 50.0,
                "prob_arista": 0.3
            },
            "logistica": {
                "pct_almacenamiento": 15.0,
                "pct_recarga": 25.0,
                "pct_cliente": 60.0,
                "prob_arista": 0.25
            },
            "servicio": {
                "pct_almacenamiento": 10.0,
                "pct_recarga": 40.0,
                "pct_cliente": 50.0,
                "prob_arista": 0.35
            },
            "pequena_ciudad": {
                "pct_almacenamiento": 25.0,
                "pct_recarga": 35.0,
                "pct_cliente": 40.0,
                "prob_arista": 0.3,
                "clientes_por_nodo": 2,
                "ordenes_por_cliente": 5,
                "bateria_dron": 1000.0,
                "consumo_dron": 2.0,
                "capacidad_estacion": 3,
                "costo_recarga": 3.0
            },
            "ciudad_mediana": {
                "pct_almacenamiento": 20.0,
                "pct_recarga": 30.0,
                "pct_cliente": 50.0,
                "prob_arista": 0.25,
                "clientes_por_nodo": 5,
                "ordenes_por_cliente": 10,
                "bateria_dron": 2000.0,
                "consumo_dron": 1.8,
                "capacidad_estacion": 5,
                "costo_recarga": 4.0
            },
            "ciudad_grande": {
                "pct_almacenamiento": 15.0,
                "pct_recarga": 25.0,
                "pct_cliente": 60.0,
                "prob_arista": 0.2,
                "clientes_por_nodo": 10,
                "ordenes_por_cliente": 15,
                "bateria_dron": 3000.0,
                "consumo_dron": 1.5,
                "capacidad_estacion": 8,
                "costo_recarga": 5.0
            }
        }
        
        config = configuraciones.get(escenario, configuraciones["balanceado"])
        config["num_nodos"] = num_nodos
        config["semilla"] = 42
        
        return config 
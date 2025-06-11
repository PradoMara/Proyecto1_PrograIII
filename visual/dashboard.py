"""
Dashboard principal con Streamlit para el Sistema de Grafos Conectados

Interfaz interactiva que permite:
- Configurar parámetros de generación de grafos
- Ejecutar simulaciones con validaciones
- Visualizar resultados y estadísticas
- Analizar rutas y conectividad
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import GeneradorGrafoConectado, RolNodo, ConfiguracionRoles
from model import ConsultorGrafo, CalculadorDistancias, BuscadorNodos
from visual.networkx_adapter import NetworkXAdapter
from tda.avl_rutas import AVLRutas
from domain.route import RutaInfo
from sim.generador_datos import GeneradorDatosSimulacion
from domain.client import Cliente, TipoCliente, EstadoCliente
from domain.order import Orden, TipoOrden, PrioridadOrden, EstadoOrden

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Grafos Conectados",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SimulacionState:
    """Gestión del estado de la simulación"""
    
    def __init__(self):
        if 'grafo_actual' not in st.session_state:
            st.session_state.grafo_actual = None
        if 'estadisticas_actuales' not in st.session_state:
            st.session_state.estadisticas_actuales = None
        if 'avl_rutas' not in st.session_state:
            st.session_state.avl_rutas = AVLRutas()
        if 'historial_simulaciones' not in st.session_state:
            st.session_state.historial_simulaciones = []
        if 'networkx_graph' not in st.session_state:
            st.session_state.networkx_graph = None
        if 'clientes_actuales' not in st.session_state:
            st.session_state.clientes_actuales = []
        if 'ordenes_actuales' not in st.session_state:
            st.session_state.ordenes_actuales = []
        if 'generador_datos' not in st.session_state:
            st.session_state.generador_datos = GeneradorDatosSimulacion()

    @staticmethod
    def limpiar_estado():
        """Limpia el estado actual de la simulación"""
        st.session_state.grafo_actual = None
        st.session_state.estadisticas_actuales = None
        st.session_state.avl_rutas = AVLRutas()
        st.session_state.networkx_graph = None
        st.session_state.clientes_actuales = []
        st.session_state.ordenes_actuales = []

    @staticmethod
    def agregar_al_historial(config: Dict, stats: Dict):
        """Agrega una simulación al historial"""
        simulacion = {
            'timestamp': time.time(),
            'configuracion': config.copy(),
            'estadisticas': stats.copy()
        }
        st.session_state.historial_simulaciones.append(simulacion)

def validar_configuracion(num_nodos: int, prob_arista: float, 
                         pct_almacenamiento: float, pct_recarga: float, 
                         pct_cliente: float) -> Tuple[bool, List[str]]:
    """
    Valida la configuración de la simulación
    
    Returns:
        Tuple[bool, List[str]]: (es_valida, lista_errores)
    """
    errores = []
    
    # Validar número de nodos
    if num_nodos < 1:
        errores.append("❌ El número de nodos debe ser mayor a 0")
    elif num_nodos > 1000:
        errores.append("⚠️ Número de nodos muy alto (>1000), puede ser lento")
    
    # Validar probabilidad de arista
    if not (0.0 <= prob_arista <= 1.0):
        errores.append("❌ La probabilidad de arista debe estar entre 0.0 y 1.0")
    
    # Validar porcentajes de roles
    suma_porcentajes = pct_almacenamiento + pct_recarga + pct_cliente
    if abs(suma_porcentajes - 100.0) > 0.1:
        errores.append(f"❌ Los porcentajes deben sumar 100% (actual: {suma_porcentajes:.1f}%)")
    
    # Validar que cada porcentaje sea válido
    for nombre, valor in [("almacenamiento", pct_almacenamiento), 
                         ("recarga", pct_recarga), 
                         ("cliente", pct_cliente)]:
        if valor < 0 or valor > 100:
            errores.append(f"❌ El porcentaje de {nombre} debe estar entre 0% y 100%")
    
    # Validaciones de lógica de negocio
    if num_nodos >= 2:
        if pct_almacenamiento == 0:
            errores.append("⚠️ Se recomienda al menos 1 nodo de almacenamiento")
        if pct_recarga == 0:
            errores.append("⚠️ Se recomienda al menos 1 nodo de recarga")
    
    return len(errores) == 0, errores

def mostrar_metricas_principales(stats: Dict):
    """Muestra las métricas principales en columnas"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔗 Nodos",
            value=stats['numero_vertices'],
            help="Número total de vértices en el grafo"
        )
    
    with col2:
        st.metric(
            label="📊 Aristas", 
            value=stats['numero_aristas'],
            help="Número total de conexiones entre nodos"
        )
    
    with col3:
        conectado = "✅ Sí" if stats['esta_conectado'] else "❌ No"
        st.metric(
            label="🌐 Conectado",
            value=conectado,
            help="Si existe un camino entre cualquier par de nodos"
        )
    
    with col4:
        st.metric(
            label="📈 Densidad",
            value=f"{stats['densidad']:.3f}",
            help="Proporción de aristas existentes vs. máximo posible"
        )

def mostrar_distribucion_roles(stats: Dict):
    """Muestra la distribución de roles en gráfico circular"""
    distribucion = stats['distribución_roles']
    
    if distribucion:
        # Preparar datos para el gráfico
        roles = list(distribucion.keys())
        cantidades = list(distribucion.values())
        
        # Colores específicos para cada rol
        color_map = {
            RolNodo.ALMACENAMIENTO: '#FF6B6B',
            RolNodo.RECARGA: '#4ECDC4', 
            RolNodo.CLIENTE: '#45B7D1'
        }
        
        colores = [color_map.get(rol, '#95A5A6') for rol in roles]
        
        fig = go.Figure(data=[go.Pie(
            labels=roles,
            values=cantidades,
            hole=0.4,
            marker_colors=colores,
            textinfo='label+percent+value',
            hovertemplate='<b>%{label}</b><br>' +
                         'Cantidad: %{value}<br>' +
                         'Porcentaje: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title="Distribución de Roles en el Grafo",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def ejecutar_simulacion(config: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Ejecuta una simulación con la configuración dada
    
    Returns:
        Tuple[bool, Optional[Dict], Optional[str]]: (exito, estadisticas, mensaje_error)
    """
    try:
        # Crear configuración de roles
        configuracion_roles = ConfiguracionRoles(
            almacenamiento=config['pct_almacenamiento'] / 100.0,
            recarga=config['pct_recarga'] / 100.0,
            cliente=config['pct_cliente'] / 100.0
        )
        
        # Crear generador
        generador = GeneradorGrafoConectado(configuracion_roles)
        
        # Establecer semilla si se especifica
        if config.get('semilla'):
            generador.establecer_semilla(config['semilla'])
        
        # Generar grafo
        grafo = generador.crear_grafo_conectado(
            config['num_nodos'], 
            config['prob_arista']
        )
        
        # Obtener estadísticas
        stats = generador.obtener_estadisticas_grafo(grafo)
        
        # Convertir a NetworkX para visualización
        nx_graph = NetworkXAdapter.convertir_a_networkx(grafo)
        
        # Generar datos de simulación (clientes y órdenes)
        if config.get('semilla'):
            st.session_state.generador_datos = GeneradorDatosSimulacion(config['semilla'])
        
        clientes, ordenes = st.session_state.generador_datos.generar_datos_completos(grafo)
        
        # Guardar en session state
        st.session_state.grafo_actual = grafo
        st.session_state.estadisticas_actuales = stats
        st.session_state.networkx_graph = nx_graph
        st.session_state.clientes_actuales = clientes
        st.session_state.ordenes_actuales = ordenes
        
        return True, stats, None
        
    except Exception as e:
        return False, None, f"Error al generar el grafo: {str(e)}"

def mostrar_exploracion_red():
    """Muestra la interfaz de exploración de red con cálculo de rutas interactivo"""
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay un grafo generado. Ve a la pestaña 'Simulación' para crear uno.")
        return
    
    st.header("🌐 Exploración de Red y Cálculo de Rutas")
    
    grafo = st.session_state.grafo_actual
    
    # Inicializar variables de estado para la pestaña
    if 'nodos_seleccionados' not in st.session_state:
        st.session_state.nodos_seleccionados = []
    if 'ruta_calculada' not in st.session_state:
        st.session_state.ruta_calculada = None
    if 'historial_rutas' not in st.session_state:
        st.session_state.historial_rutas = []
    
    # Convertir a NetworkX si no existe
    if st.session_state.networkx_graph is None:
        st.session_state.networkx_graph = NetworkXAdapter.convertir_a_networkx(st.session_state.grafo_actual)
    
    nx_graph = st.session_state.networkx_graph
    vertices = list(grafo.vertices())
    
    # === SECCIÓN 1: VISUALIZACIÓN PRINCIPAL ===
    st.subheader("🗺️ Mapa de la Red")
    
    # Controles de visualización
    col_viz1, col_viz2, col_viz3 = st.columns(3)
    
    with col_viz1:
        layout_type = st.selectbox(
            "Layout del Grafo",
            ["spring", "circular", "kamada_kawai", "random"],
            help="Algoritmo de posicionamiento de nodos"
        )
    
    with col_viz2:
        mostrar_info_nodos = st.checkbox("Mostrar Info de Nodos", value=True)
    
    with col_viz3:
        auto_zoom = st.checkbox("Auto-zoom en Ruta", value=True)
    
    # Crear visualización principal
    if len(vertices) <= 100:  # Limitar para grafos grandes
        # Determinar si hay una ruta para resaltar
        ruta_ids = None
        if st.session_state.ruta_calculada:
            ruta_ids = [v.element()['id'] for v in st.session_state.ruta_calculada['camino']]
        
        fig_principal = NetworkXAdapter.crear_visualizacion_plotly(
            nx_graph,
            resaltar_camino=ruta_ids,
            titulo="Red de Distribución - Exploración Interactiva"
        )
        
        # Ajustar altura y mostrar
        fig_principal.update_layout(height=500)
        st.plotly_chart(fig_principal, use_container_width=True)
        
        # Información de la ruta actual si existe
        if st.session_state.ruta_calculada:
            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
            
            with col_info1:
                st.metric(
                    "🎯 Origen", 
                    st.session_state.ruta_calculada['origen']['nombre']
                )
            
            with col_info2:
                st.metric(
                    "📍 Destino", 
                    st.session_state.ruta_calculada['destino']['nombre']
                )
            
            with col_info3:
                st.metric(
                    "📏 Distancia Total", 
                    f"{st.session_state.ruta_calculada['distancia']:.2f}"
                )
            
            with col_info4:
                st.metric(
                    "🔢 Número de Saltos", 
                    len(st.session_state.ruta_calculada['camino']) - 1
                )
    
    else:
        st.warning("⚠️ Grafo demasiado grande para visualización interactiva (>100 nodos)")
        st.info("📊 Usa las herramientas de selección y cálculo de rutas a continuación.")
    
    st.markdown("---")
    
    # === SECCIÓN 2: SELECCIÓN DE NODOS ===
    st.subheader("🎯 Selección de Nodos")
    
    col_sel1, col_sel2 = st.columns(2)
    
    with col_sel1:
        st.write("**🚀 Nodo Origen**")
        
        # Filtros para nodo origen
        filtro_rol_origen = st.selectbox(
            "Filtrar por Rol (Origen)",
            ["Todos"] + [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA, RolNodo.CLIENTE],
            key="filtro_rol_origen"
        )
        
        # Filtrar opciones de origen
        opciones_origen = []
        for v in vertices:
            datos = v.element()
            if filtro_rol_origen == "Todos" or datos.get('rol') == filtro_rol_origen:
                opciones_origen.append(v)
        
        if opciones_origen:
            # Crear opciones legibles
            opciones_origen_texto = [
                f"ID {v.element()['id']} | {v.element()['nombre']} | {v.element().get('rol', 'sin_rol').title()}"
                for v in opciones_origen
            ]
            
            idx_origen = st.selectbox(
                "Seleccionar Origen",
                range(len(opciones_origen)),
                format_func=lambda x: opciones_origen_texto[x],
                key="selector_origen"
            )
            
            nodo_origen = opciones_origen[idx_origen]
            
            # Mostrar información del nodo origen
            origen_info = nodo_origen.element()
            st.info(f"**Seleccionado:** {origen_info['nombre']}")
            st.write(f"• **ID:** {origen_info['id']}")
            st.write(f"• **Rol:** {origen_info.get('rol', 'sin_rol').title()}")
            st.write(f"• **Grado:** {ConsultorGrafo.obtener_grado(grafo, nodo_origen)}")
        
        else:
            st.warning("No hay nodos disponibles con el filtro seleccionado")
            nodo_origen = None
    
    with col_sel2:
        st.write("**🎯 Nodo Destino**")
        
        # Filtros para nodo destino
        filtro_rol_destino = st.selectbox(
            "Filtrar por Rol (Destino)",
            ["Todos"] + [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA, RolNodo.CLIENTE],
            key="filtro_rol_destino"
        )
        
        # Filtrar opciones de destino (excluyendo el origen)
        opciones_destino = []
        for v in vertices:
            datos = v.element()
            if (filtro_rol_destino == "Todos" or datos.get('rol') == filtro_rol_destino) and \
               (nodo_origen is None or v != nodo_origen):
                opciones_destino.append(v)
        
        if opciones_destino and nodo_origen is not None:
            # Crear opciones legibles
            opciones_destino_texto = [
                f"ID {v.element()['id']} | {v.element()['nombre']} | {v.element().get('rol', 'sin_rol').title()}"
                for v in opciones_destino
            ]
            
            idx_destino = st.selectbox(
                "Seleccionar Destino",
                range(len(opciones_destino)),
                format_func=lambda x: opciones_destino_texto[x],
                key="selector_destino"
            )
            
            nodo_destino = opciones_destino[idx_destino]
            
            # Mostrar información del nodo destino
            destino_info = nodo_destino.element()
            st.info(f"**Seleccionado:** {destino_info['nombre']}")
            st.write(f"• **ID:** {destino_info['id']}")
            st.write(f"• **Rol:** {destino_info.get('rol', 'sin_rol').title()}")
            st.write(f"• **Grado:** {ConsultorGrafo.obtener_grado(grafo, nodo_destino)}")
        
        else:
            if nodo_origen is None:
                st.info("Primero selecciona un nodo origen")
            else:
                st.warning("No hay nodos de destino disponibles con el filtro seleccionado")
            nodo_destino = None
    
    # === SECCIÓN 3: CÁLCULO DE RUTAS ===
    st.markdown("---")
    st.subheader("🔍 Cálculo de Rutas")
    
    col_calc1, col_calc2, col_calc3 = st.columns([2, 1, 1])
    
    with col_calc1:
        # Botón principal de cálculo
        calcular_disabled = nodo_origen is None or nodo_destino is None or nodo_origen == nodo_destino
        
        if st.button(
            "🗺️ Calcular Ruta Óptima",
            type="primary",
            disabled=calcular_disabled,
            help="Calcula la ruta más corta usando el algoritmo de Dijkstra"
        ):
            if nodo_origen and nodo_destino:
                with st.spinner("🔄 Calculando ruta óptima..."):
                    resultado = CalculadorDistancias.encontrar_camino_mas_corto(
                        grafo, nodo_origen, nodo_destino
                    )
                    
                    if resultado:
                        camino, distancia_total = resultado
                        
                        # Guardar resultado en session state
                        st.session_state.ruta_calculada = {
                            'origen': nodo_origen.element(),
                            'destino': nodo_destino.element(),
                            'camino': camino,
                            'distancia': distancia_total,
                            'timestamp': datetime.now()
                        }
                        
                        # Agregar al historial
                        ruta_historial = {
                            'id': len(st.session_state.historial_rutas) + 1,
                            'origen_id': nodo_origen.element()['id'],
                            'destino_id': nodo_destino.element()['id'],
                            'origen_nombre': nodo_origen.element()['nombre'],
                            'destino_nombre': nodo_destino.element()['nombre'],
                            'distancia': distancia_total,
                            'saltos': len(camino) - 1,
                            'timestamp': datetime.now()
                        }
                        st.session_state.historial_rutas.append(ruta_historial)
                        
                        # Guardar en AVL de rutas
                        ruta_id = f"explorador_{nodo_origen.element()['id']}_{nodo_destino.element()['id']}"
                        ruta_info = RutaInfo(
                            ruta_id=ruta_id,
                            origen=nodo_origen.element()['nombre'],
                            destino=nodo_destino.element()['nombre'],
                            camino=[v.element()['nombre'] for v in camino],
                            distancia=distancia_total,
                            frecuencia_uso=1,
                            ultimo_uso=datetime.now(),
                            tiempo_promedio=0.0,
                            metadatos={"creado_en": "explorador", "tipo": "busqueda_interactiva"}
                        )
                        st.session_state.avl_rutas.insertar_ruta(ruta_info)
                        
                        st.success("✅ ¡Ruta calculada exitosamente!")
                        st.rerun()
                    
                    else:
                        st.error("❌ No se encontró una ruta entre los nodos seleccionados")
                        st.info("💡 Verifica que los nodos estén en la misma componente conexa del grafo")
    
    with col_calc2:
        if st.button("🔄 Limpiar Ruta", help="Limpia la ruta actual"):
            st.session_state.ruta_calculada = None
            st.rerun()
    
    with col_calc3:
        if st.button("📋 Ver Historial", help="Muestra el historial de rutas calculadas"):
            if st.session_state.historial_rutas:
                st.session_state.mostrar_historial_rutas = True
            else:
                st.info("📝 No hay rutas en el historial")
    
    # === SECCIÓN 4: DETALLES DE LA RUTA ACTUAL ===
    if st.session_state.ruta_calculada:
        st.markdown("---")
        st.subheader("📋 Detalles de la Ruta Calculada")
        
        ruta_actual = st.session_state.ruta_calculada
        camino = ruta_actual['camino']
        
        # Información general
        col_det1, col_det2 = st.columns([2, 1])
        
        with col_det1:
            st.write("**🛣️ Camino Completo:**")
            
            # Mostrar el camino paso a paso
            camino_texto = []
            for i, nodo in enumerate(camino):
                nombre = nodo.element()['nombre']
                rol = nodo.element().get('rol', 'sin_rol')
                emoji_rol = {"almacenamiento": "🏪", "recarga": "⚡", "cliente": "👤"}.get(rol, "📍")
                
                if i == 0:
                    camino_texto.append(f"🚀 **{nombre}** {emoji_rol}")
                elif i == len(camino) - 1:
                    camino_texto.append(f"🎯 **{nombre}** {emoji_rol}")
                else:
                    camino_texto.append(f"   ↓ {nombre} {emoji_rol}")
            
            for texto in camino_texto:
                st.write(texto)
        
        with col_det2:
            st.write("**📊 Estadísticas:**")
            st.metric("Distancia Total", f"{ruta_actual['distancia']:.2f} km")
            st.metric("Número de Saltos", len(camino) - 1)
            st.metric("Nodos Intermedios", max(0, len(camino) - 2))
            
            # Tiempo de cálculo
            tiempo_calc = datetime.now() - ruta_actual['timestamp']
            st.write(f"⏱️ Calculada hace: {tiempo_calc.total_seconds():.1f}s")
        
        # Tabla detallada de segmentos
        st.write("**📏 Análisis por Segmentos:**")
        
        if len(camino) > 1:
            datos_segmentos = []
            distancia_acumulada = 0
            
            for i in range(len(camino) - 1):
                nodo_actual = camino[i]
                nodo_siguiente = camino[i + 1]
                
                # Calcular distancia del segmento
                distancia_segmento = CalculadorDistancias.calcular_distancia_entre(
                    grafo, nodo_actual, nodo_siguiente
                )
                
                if distancia_segmento is not None:
                    distancia_acumulada += distancia_segmento
                    
                    datos_segmentos.append({
                        "Segmento": f"{i + 1}",
                        "Desde": nodo_actual.element()['nombre'],
                        "Hacia": nodo_siguiente.element()['nombre'],
                        "Distancia": f"{distancia_segmento:.2f} km",
                        "Distancia Acum.": f"{distancia_acumulada:.2f} km",
                        "Rol Origen": nodo_actual.element().get('rol', 'sin_rol').title(),
                        "Rol Destino": nodo_siguiente.element().get('rol', 'sin_rol').title()
                    })
            
            if datos_segmentos:
                df_segmentos = pd.DataFrame(datos_segmentos)
                st.dataframe(df_segmentos, use_container_width=True, hide_index=True)
        
        # Acciones adicionales
        col_acc1, col_acc2, col_acc3 = st.columns(3)
        
        with col_acc1:
            if st.button("💾 Guardar Ruta", help="Guarda la ruta con un nombre personalizado"):
                st.info("🚧 Funcionalidad de guardado personalizado en desarrollo")
        
        with col_acc2:
            if st.button("📤 Exportar Ruta", help="Exporta la ruta en formato JSON"):
                ruta_export = {
                    'origen': ruta_actual['origen'],
                    'destino': ruta_actual['destino'],
                    'camino': [nodo.element() for nodo in camino],
                    'distancia_total': ruta_actual['distancia'],
                    'fecha_calculo': ruta_actual['timestamp'].isoformat()
                }
                st.json(ruta_export)
        
        with col_acc3:
            if st.button("🔍 Analizar Ruta", help="Análisis detallado de la ruta"):
                st.info("🚧 Análisis avanzado de rutas en desarrollo")
    
    # === SECCIÓN 5: HERRAMIENTAS ADICIONALES ===
    st.markdown("---")
    st.subheader("🛠️ Herramientas de Exploración")
    
    col_herr1, col_herr2 = st.columns(2)
    
    with col_herr1:
        st.write("**🎯 Búsqueda por Proximidad**")
        
        if nodo_origen:
            rol_busqueda = st.selectbox(
                "Buscar nodos cercanos de tipo:",
                [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA, RolNodo.CLIENTE],
                format_func=lambda x: x.title(),
                key="rol_busqueda_proximidad"
            )
            
            k_cercanos = st.slider("Número de nodos más cercanos:", 1, 10, 3, key="k_cercanos_prox")
            
            if st.button("🔍 Buscar Nodos Cercanos"):
                resultado_cercanos = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
                    grafo, nodo_origen, rol_busqueda, k_cercanos
                )
                
                if resultado_cercanos:
                    st.success(f"✅ Encontrados {len(resultado_cercanos)} nodos cercanos")
                    
                    datos_cercanos = []
                    for i, (nodo, distancia) in enumerate(resultado_cercanos, 1):
                        datos_cercanos.append({
                            "Posición": i,
                            "Nodo": nodo.element()['nombre'],
                            "ID": nodo.element()['id'],
                            "Distancia": f"{distancia:.2f} km"
                        })
                    
                    df_cercanos = pd.DataFrame(datos_cercanos)
                    st.dataframe(df_cercanos, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"⚠️ No se encontraron nodos del tipo '{rol_busqueda}'")
        else:
            st.info("Selecciona un nodo origen para usar esta herramienta")
    
    with col_herr2:
        st.write("**📊 Estadísticas de Red**")
        
        if st.button("📈 Analizar Conectividad"):
            # Análisis de conectividad desde el nodo origen
            if nodo_origen:
                distancias, _ = CalculadorDistancias.dijkstra(grafo, nodo_origen)
                
                # Estadísticas de alcance
                nodos_alcanzables = sum(1 for d in distancias.values() if d != float('inf'))
                distancia_promedio = sum(d for d in distancias.values() if d != float('inf')) / max(1, nodos_alcanzables - 1)
                distancia_maxima = max(d for d in distancias.values() if d != float('inf'))
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.metric("Nodos Alcanzables", f"{nodos_alcanzables}/{len(vertices)}")
                
                with col_stat2:
                    st.metric("Distancia Promedio", f"{distancia_promedio:.2f}")
                
                with col_stat3:
                    st.metric("Distancia Máxima", f"{distancia_maxima:.2f}")
                
                # Análisis por roles
                stats_roles = BuscadorNodos.obtener_estadisticas_roles(grafo)
                st.write("**Distribución por Roles:**")
                for rol, info in stats_roles.items():
                    st.write(f"• {rol.title()}: {info['cantidad']} nodos ({info['porcentaje']:.1f}%)")
            
            else:
                st.info("Selecciona un nodo origen para análisis detallado")
    
    # === SECCIÓN 6: HISTORIAL DE RUTAS ===
    if st.session_state.historial_rutas:
        st.markdown("---")
        st.subheader("📋 Historial de Rutas Calculadas")
        
        # Controles del historial
        col_hist1, col_hist2 = st.columns([3, 1])
        
        with col_hist1:
            st.write(f"**Total de rutas calculadas:** {len(st.session_state.historial_rutas)}")
        
        with col_hist2:
            if st.button("🗑️ Limpiar Historial"):
                st.session_state.historial_rutas = []
                st.rerun()
        
        # Tabla del historial
        datos_historial = []
        for ruta in reversed(st.session_state.historial_rutas[-10:]):  # Mostrar últimas 10
            datos_historial.append({
                "ID": ruta['id'],
                "Origen": ruta['origen_nombre'],
                "Destino": ruta['destino_nombre'],
                "Distancia": f"{ruta['distancia']:.2f} km",
                "Saltos": ruta['saltos'],
                "Hora": ruta['timestamp'].strftime("%H:%M:%S")
            })
        
        if datos_historial:
            st.dataframe(datos_historial, use_container_width=True, hide_index=True)

def mostrar_analisis_detallado():
    """Muestra análisis detallado del grafo actual (función original simplificada)"""
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay un grafo generado. Ve a la pestaña 'Simulación' para crear uno.")
        return
    
    st.header("📊 Análisis Detallado del Grafo")
    
    # Convertir a NetworkX si no existe
    if st.session_state.networkx_graph is None:
        st.session_state.networkx_graph = NetworkXAdapter.convertir_a_networkx(st.session_state.grafo_actual)
    
    nx_graph = st.session_state.networkx_graph
    
    # Métricas básicas en columnas
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📈 Métricas de Red")
        metricas = NetworkXAdapter.analizar_metricas_red(nx_graph)
        
        if metricas:
            # Mostrar métricas en una tabla
            df_metricas = pd.DataFrame([
                {"Métrica": "Número de Nodos", "Valor": str(metricas.get('num_nodos', 'N/A'))},
                {"Métrica": "Número de Aristas", "Valor": str(metricas.get('num_aristas', 'N/A'))},
                {"Métrica": "Densidad", "Valor": f"{metricas.get('densidad', 0):.4f}"},
                {"Métrica": "Conectado", "Valor": "Sí" if metricas.get('conectado', False) else "No"},
                {"Métrica": "Grado Promedio", "Valor": f"{metricas.get('grado_promedio', 0):.2f}"},
            ])
            
            st.dataframe(df_metricas, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Distribución de Grados")
        fig_grados = NetworkXAdapter.crear_grafico_distribucion_grados(nx_graph)
        st.plotly_chart(fig_grados, use_container_width=True)
    
    # Análisis por roles
    st.subheader("👥 Análisis por Roles")
    
    if st.session_state.grafo_actual:
        stats_roles = BuscadorNodos.obtener_estadisticas_roles(st.session_state.grafo_actual)
        
        if stats_roles:
            # Crear tabla de estadísticas por rol
            datos_roles = []
            for rol, info in stats_roles.items():
                datos_roles.append({
                    "Rol": rol.title(),
                    "Cantidad": info['cantidad'],
                    "Porcentaje": f"{info['porcentaje']:.1f}%",
                    "Grado Promedio": f"{info['grado_promedio']:.2f}",
                })
            
            df_roles = pd.DataFrame(datos_roles)
            st.dataframe(df_roles, use_container_width=True, hide_index=True)

def actualizar_visualizacion_con_ruta(ruta_calculada: Dict) -> None:
    """Actualiza la visualización del grafo resaltando la ruta calculada"""
    if st.session_state.networkx_graph is None or not ruta_calculada:
        return
    
    # Extraer IDs de la ruta
    camino = ruta_calculada['camino']
    ruta_ids = [v.element()['id'] for v in camino]
    
    # Crear visualización con ruta resaltada
    fig_ruta = NetworkXAdapter.resaltar_ruta_en_grafo(
        st.session_state.networkx_graph,
        ruta_ids
    )
    
    # Mostrar información adicional de la ruta
    st.success(f"✅ Ruta calculada: {ruta_calculada['origen']['nombre']} → {ruta_calculada['destino']['nombre']}")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("📏 Distancia Total", f"{ruta_calculada['distancia']:.2f} km")
    with col_info2:
        st.metric("🔢 Número de Saltos", len(camino) - 1)
    with col_info3:
        st.metric("📍 Nodos en Ruta", len(camino))
    
    # Mostrar la visualización
    st.plotly_chart(fig_ruta, use_container_width=True, key="ruta_resaltada")
    
    return fig_ruta

def main():
    """Función principal del dashboard"""
    
    # Inicializar estado
    sim_state = SimulacionState()
    
    # Título principal
    st.title("🌐 Sistema de Grafos Conectados")
    st.markdown("---")
    
    # Sidebar para configuración global
    with st.sidebar:
        st.header("⚙️ Configuración Global")
        
        # Tema de visualización
        tema_viz = st.selectbox(
            "Tema de Visualización",
            ["plotly", "plotly_white", "plotly_dark"],
            index=1
        )
        
        # Configuración de rendimiento
        st.subheader("🚀 Rendimiento")
        max_nodos_viz = st.slider(
            "Máx. nodos para visualización",
            min_value=10, max_value=500, value=100,
            help="Limita la visualización para grafos grandes"
        )
        
        # Información del estado actual
        st.subheader("📊 Estado Actual")
        if st.session_state.estadisticas_actuales:
            st.success("✅ Grafo cargado")
            st.write(f"Nodos: {st.session_state.estadisticas_actuales['numero_vertices']}")
            st.write(f"Aristas: {st.session_state.estadisticas_actuales['numero_aristas']}")
            
            # Información de clientes y órdenes
            if st.session_state.clientes_actuales or st.session_state.ordenes_actuales:
                st.write("---")
                st.write("**Datos de Simulación:**")
                st.write(f"👥 Clientes: {len(st.session_state.clientes_actuales)}")
                st.write(f"📋 Órdenes: {len(st.session_state.ordenes_actuales)}")
                
                if st.session_state.ordenes_actuales:
                    valor_total = sum(orden.costo_total for orden in st.session_state.ordenes_actuales)
                    st.write(f"💰 Valor Total: ${valor_total:,.2f}")
        else:
            st.info("⏳ Sin grafo cargado")
        
        # Botón para limpiar estado
        if st.button("🗑️ Limpiar Todo", type="secondary"):
            SimulacionState.limpiar_estado()
            st.rerun()
    
    # Pestañas principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Simulación", 
        "🌐 Exploración de Red", 
        "👥 Clientes & Órdenes",
        "🗺️ Rutas", 
        "📈 Historial"
    ])
    
    # PESTAÑA 1: CONFIGURACIÓN Y SIMULACIÓN
    with tab1:
        st.header("🚀 Configuración y Ejecución de Simulación")
        
        # Columnas para la configuración
        col_config, col_preview = st.columns([2, 1])
        
        with col_config:
            st.subheader("⚙️ Parámetros de Generación")
            
            # Configuración básica
            with st.expander("🔧 Configuración Básica", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    num_nodos = st.slider(
                        "Número de Nodos",
                        min_value=1, max_value=1000, value=20,
                        help="Cantidad total de nodos en el grafo"
                    )
                    
                with col2:
                    prob_arista = st.slider(
                        "Probabilidad de Arista",
                        min_value=0.0, max_value=1.0, value=0.3, step=0.05,
                        help="Probabilidad de crear aristas adicionales entre nodos"
                    )
            
            # Configuración de roles
            with st.expander("👥 Distribución de Roles", expanded=True):
                st.info("💡 Los porcentajes deben sumar exactamente 100%")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pct_almacenamiento = st.slider(
                        "🏪 Almacenamiento (%)",
                        min_value=0.0, max_value=100.0, value=20.0, step=1.0,
                        help="Porcentaje de nodos de almacenamiento"
                    )
                
                with col2:
                    pct_recarga = st.slider(
                        "⚡ Recarga (%)",
                        min_value=0.0, max_value=100.0, value=30.0, step=1.0,
                        help="Porcentaje de nodos de recarga"
                    )
                
                with col3:
                    pct_cliente = st.slider(
                        "👤 Cliente (%)",
                        min_value=0.0, max_value=100.0, value=50.0, step=1.0,
                        help="Porcentaje de nodos cliente"
                    )
                
                # Mostrar suma de porcentajes
                suma_actual = pct_almacenamiento + pct_recarga + pct_cliente
                if abs(suma_actual - 100.0) > 0.1:
                    st.error(f"⚠️ Suma actual: {suma_actual:.1f}% (debe ser 100%)")
                else:
                    st.success(f"✅ Suma: {suma_actual:.1f}%")
            
            # Configuración avanzada
            with st.expander("🔬 Configuración Avanzada"):
                usar_semilla = st.checkbox("Usar semilla fija (reproducible)")
                semilla = None
                if usar_semilla:
                    semilla = st.number_input(
                        "Semilla",
                        min_value=1, max_value=999999, value=42,
                        help="Semilla para resultados reproducibles"
                    )
        
        with col_preview:
            st.subheader("📋 Vista Previa")
            
            # Configuración actual
            config_actual = {
                'num_nodos': num_nodos,
                'prob_arista': prob_arista,
                'pct_almacenamiento': pct_almacenamiento,
                'pct_recarga': pct_recarga,
                'pct_cliente': pct_cliente,
                'semilla': semilla
            }
            
            # Cálculo de estimaciones
            try:
                config_roles = ConfiguracionRoles(
                    pct_almacenamiento/100, pct_recarga/100, pct_cliente/100
                )
                distribucion_estimada = config_roles.calcular_cantidad_nodos(num_nodos)
                
                st.info("📊 **Distribución Estimada:**")
                for rol, cantidad in distribucion_estimada.items():
                    emoji = {"almacenamiento": "🏪", "recarga": "⚡", "cliente": "👤"}
                    st.write(f"{emoji.get(rol, '•')} {rol.title()}: {cantidad} nodos")
                
                # Estimaciones adicionales
                max_aristas = num_nodos * (num_nodos - 1) // 2
                aristas_estimadas = int((num_nodos - 1) + prob_arista * (max_aristas - (num_nodos - 1)))
                
                st.write(f"🔗 Aristas estimadas: ~{aristas_estimadas}")
                st.write(f"📈 Densidad estimada: ~{aristas_estimadas/max_aristas:.3f}")
                
            except ValueError as e:
                st.error(f"❌ Error en configuración: {e}")
        
        # Validación y ejecución
        st.markdown("---")
        
        # Validar configuración
        es_valida, errores = validar_configuracion(
            num_nodos, prob_arista, pct_almacenamiento, pct_recarga, pct_cliente
        )
        
        # Mostrar errores si los hay
        if errores:
            for error in errores:
                if error.startswith("❌"):
                    st.error(error)
                else:
                    st.warning(error)
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            btn_ejecutar = st.button(
                "🚀 Ejecutar Simulación",
                type="primary",
                disabled=not es_valida,
                help="Genera un nuevo grafo con la configuración actual"
            )
        
        with col_btn2:
            if st.button("🎲 Configuración Aleatoria"):
                st.rerun()
        
        with col_btn3:
            if st.button("📋 Usar Preset"):
                # Aquí se pueden agregar configuraciones predefinidas
                pass
        
        # Ejecutar simulación
        if btn_ejecutar and es_valida:
            with st.spinner("🔄 Generando grafo..."):
                exito, stats, error = ejecutar_simulacion(config_actual)
                
                if exito:
                    st.success("✅ ¡Simulación ejecutada exitosamente!")
                    
                    # Agregar al historial
                    SimulacionState.agregar_al_historial(config_actual, stats)
                    
                    # Mostrar resultados inmediatos
                    st.subheader("📊 Resultados de la Simulación")
                    mostrar_metricas_principales(stats)
                    
                    # Distribución de roles
                    mostrar_distribucion_roles(stats)
                    
                else:
                    st.error(f"❌ Error en la simulación: {error}")
        
        # Mostrar resultados de simulación actual
        if st.session_state.estadisticas_actuales:
            st.markdown("---")
            st.subheader("📊 Simulación Actual")
            mostrar_metricas_principales(st.session_state.estadisticas_actuales)

    # PESTAÑA 2: EXPLORACIÓN DE RED
    with tab2:
        mostrar_exploracion_red()

"""    # PESTAÑA 3: CLIENTES Y ÓRDENES
    with tab3:
        mostrar_clientes_y_ordenes()

    # PESTAÑA 4: RUTAS
    with tab4:
        mostrar_analisis_rutas()

    # PESTAÑA 5: HISTORIAL
    with tab5:
        mostrar_historial()"""

if __name__ == "__main__":
    main()

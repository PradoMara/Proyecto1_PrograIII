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
from domain.client import Cliente
from domain.order import Orden

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

def mostrar_clientes_y_ordenes():
    """Muestra la pestaña de clientes y órdenes con información detallada"""
    
    # Verificar si hay simulación activa
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay una simulación activa. Ve a la pestaña 'Simulación' para crear una.")
        return
    
    if not st.session_state.clientes_actuales and not st.session_state.ordenes_actuales:
        st.warning("⚠️ No hay datos de clientes u órdenes generados. Ejecuta una simulación primero.")
        return
    
    st.header("👥 Gestión de Clientes y Órdenes")
    
    # Métricas generales
    col_metricas1, col_metricas2, col_metricas3, col_metricas4 = st.columns(4)
    
    with col_metricas1:
        st.metric(
            "👥 Total Clientes",
            len(st.session_state.clientes_actuales)
        )
    
    with col_metricas2:
        # Solo mostrar total de clientes ya que no tenemos estado en el nuevo modelo
        st.metric(
            "✅ Clientes Totales",
            len(st.session_state.clientes_actuales)
        )
    
    with col_metricas3:
        st.metric(
            "📋 Total Órdenes",
            len(st.session_state.ordenes_actuales)
        )
    
    with col_metricas4:
        if st.session_state.ordenes_actuales:
            valor_total = sum(orden.route_cost for orden in st.session_state.ordenes_actuales)
            st.metric(
                "💰 Valor Total",
                f"${valor_total:,.2f}"
            )
        else:
            st.metric(
                "💰 Valor Total",
                "$0.00"
            )
    
    # Pestañas para clientes y órdenes
    tab_clientes, tab_ordenes = st.tabs(["👤 Clientes", "📦 Órdenes"])
    
    # ================== PESTAÑA CLIENTES ==================
    with tab_clientes:
        st.subheader("📊 Lista de Clientes")
        
        if st.session_state.clientes_actuales:
            # Filtros
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                filtro_tipo = st.selectbox(
                    "Filtrar por Tipo",
                    ["Todos", "regular", "premium", "corporativo", "vip"],
                    key="filtro_tipo_cliente"
                )
            
            with col_filtro2:
                # Simplificado - sin estados
                st.write("**Información:** Solo campos simplificados")
            
            with col_filtro3:
                mostrar_como = st.selectbox(
                    "Mostrar como",
                    ["Tabla", "JSON"],
                    key="vista_clientes"
                )
            
            # Aplicar filtros
            clientes_filtrados = st.session_state.clientes_actuales
            
            if filtro_tipo != "Todos":
                clientes_filtrados = [c for c in clientes_filtrados 
                                    if c.type == filtro_tipo]
            
            # Mostrar información
            st.write(f"**Mostrando {len(clientes_filtrados)} de {len(st.session_state.clientes_actuales)} clientes**")
            
            if mostrar_como == "Tabla":
                # Preparar datos para tabla
                datos_clientes = []
                for cliente in clientes_filtrados:
                    datos_clientes.append({
                        "ID": cliente.client_id,
                        "Nombre": cliente.name,
                        "Tipo": cliente.type.title(),
                        "Total Órdenes": cliente.total_orders
                    })
                
                if datos_clientes:
                    df_clientes = pd.DataFrame(datos_clientes)
                    st.dataframe(df_clientes, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay clientes que coincidan con los filtros seleccionados.")
            
            else:  # JSON
                # Mostrar como JSON expandible
                for i, cliente in enumerate(clientes_filtrados):
                    with st.expander(f"Cliente {i+1}: {cliente.name} ({cliente.client_id})"):
                        cliente_resumen = {
                            "client_id": cliente.client_id,
                            "name": cliente.name,
                            "type": cliente.type,
                            "total_orders": cliente.total_orders
                        }
                        st.json(cliente_resumen)
        
        else:
            st.info("📝 No hay clientes registrados en la simulación actual.")
    
    # ================== PESTAÑA ÓRDENES ==================
    with tab_ordenes:
        st.subheader("📦 Lista de Órdenes")
        
        if st.session_state.ordenes_actuales:
            # Filtros para órdenes
            col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
            
            with col_filtro1:
                filtro_estado_orden = st.selectbox(
                    "Filtrar por Estado",
                    ["Todos", "pending", "delivered"],
                    key="filtro_estado_orden"
                )
            
            with col_filtro2:
                # Simplificado
                st.write("**Estados:** pending, delivered")
            
            with col_filtro3:
                filtro_prioridad = st.selectbox(
                    "Filtrar por Prioridad",
                    ["Todos", "low", "normal", "high", "critical"],
                    key="filtro_prioridad_orden"
                )
            
            with col_filtro4:
                mostrar_ordenes_como = st.selectbox(
                    "Mostrar como",
                    ["Tabla", "JSON"],
                    key="vista_ordenes"
                )
            
            # Aplicar filtros
            ordenes_filtradas = st.session_state.ordenes_actuales
            
            if filtro_estado_orden != "Todos":
                ordenes_filtradas = [o for o in ordenes_filtradas 
                                   if o.status == filtro_estado_orden]
            
            if filtro_prioridad != "Todos":
                ordenes_filtradas = [o for o in ordenes_filtradas 
                                   if o.priority == filtro_prioridad]
            
            # Mostrar información
            st.write(f"**Mostrando {len(ordenes_filtradas)} de {len(st.session_state.ordenes_actuales)} órdenes**")
            
            if mostrar_ordenes_como == "Tabla":
                # Preparar datos para tabla
                datos_ordenes = []
                for orden in ordenes_filtradas:
                    # Buscar nombre del cliente
                    cliente_nombre = "Cliente No Encontrado"
                    for cliente in st.session_state.clientes_actuales:
                        if cliente.client_id == orden.client_id:
                            cliente_nombre = cliente.name
                            break
                    
                    datos_ordenes.append({
                        "ID Orden": orden.order_id,
                        "Cliente": cliente_nombre,
                        "Cliente ID": orden.client_id,
                        "Estado": orden.status,
                        "Prioridad": orden.priority,
                        "Origen": orden.origin,
                        "Destino": orden.destination,
                        "Costo Ruta": f"${orden.route_cost:,.2f}",
                        "Fecha Creación": orden.created_at.strftime("%Y-%m-%d %H:%M"),
                        "Fecha Entrega": orden.delivered_at.strftime("%Y-%m-%d %H:%M") if orden.delivered_at else "Pendiente"
                    })
                
                if datos_ordenes:
                    df_ordenes = pd.DataFrame(datos_ordenes)
                    st.dataframe(df_ordenes, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay órdenes que coincidan con los filtros seleccionados.")
            
            else:  # JSON
                # Mostrar como JSON expandible
                for i, orden in enumerate(ordenes_filtradas):
                    estado_emoji = {
                        "pending": "⏳",
                        "delivered": "✅"
                    }
                    emoji = estado_emoji.get(orden.status, "📋")
                    
                    with st.expander(f"Orden {i+1}: {orden.order_id} {emoji}"):
                        orden_resumen = {
                            "order_id": orden.order_id,
                            "client": orden.client,
                            "client_id": orden.client_id,
                            "origin": orden.origin,
                            "destination": orden.destination,
                            "status": orden.status,
                            "priority": orden.priority,
                            "created_at": orden.created_at.isoformat(),
                            "delivered_at": orden.delivered_at.isoformat() if orden.delivered_at else None,
                            "route_cost": orden.route_cost
                        }
                        st.json(orden_resumen)
        
        else:
            st.info("📝 No hay órdenes registradas en la simulación actual.")
    
    # ================== ESTADÍSTICAS ADICIONALES ==================
    if st.session_state.clientes_actuales or st.session_state.ordenes_actuales:
        st.markdown("---")
        st.subheader("📊 Estadísticas Adicionales")
        
        col_stats1, col_stats2 = st.columns(2)
        
        with col_stats1:
            st.write("**📈 Distribución de Clientes por Tipo**")
            if st.session_state.clientes_actuales:
                tipos_clientes = {}
                for cliente in st.session_state.clientes_actuales:
                    tipo = cliente.type.title()
                    tipos_clientes[tipo] = tipos_clientes.get(tipo, 0) + 1
                
                for tipo, cantidad in tipos_clientes.items():
                    st.write(f"• {tipo}: {cantidad} clientes")
        
        with col_stats2:
            st.write("**📦 Distribución de Órdenes por Estado**")
            if st.session_state.ordenes_actuales:
                estados_ordenes = {}
                for orden in st.session_state.ordenes_actuales:
                    estado = orden.status.title()
                    estados_ordenes[estado] = estados_ordenes.get(estado, 0) + 1
                
                for estado, cantidad in estados_ordenes.items():
                    st.write(f"• {estado}: {cantidad} órdenes")


def mostrar_analisis_rutas():
    """Muestra la pestaña de análisis de rutas con visualización del árbol AVL"""
    st.header("🗺️ Análisis de Rutas Frecuentes")
    
    # Verificar si hay datos de simulación
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay un grafo generado. Ve a la pestaña 'Simulación' para crear uno.")
        return
    
    if not st.session_state.ordenes_actuales:
        st.info("📋 No hay órdenes generadas. Las rutas se crean basándose en las órdenes de los clientes.")
        return
    
    # === SECCIÓN 1: GENERACIÓN DE RUTAS FRECUENTES ===
    st.subheader("🚀 Generación de Rutas Frecuentes")
    
    col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
    
    with col_gen1:
        st.write("**Opciones de Generación**")
        incluir_rutas_explorador = st.checkbox(
            "Incluir rutas del explorador", 
            value=True,
            help="Incluye las rutas calculadas en el explorador de red"
        )
        
        min_frecuencia = st.slider(
            "Frecuencia mínima para mostrar",
            min_value=1, max_value=10, value=1,
            help="Solo mostrar rutas con al menos esta frecuencia de uso"
        )
    
    with col_gen2:
        if st.button("🔄 Generar Rutas", type="primary"):
            with st.spinner("🔄 Generando rutas frecuentes..."):
                rutas_generadas = _generar_rutas_desde_ordenes(incluir_rutas_explorador)
                if rutas_generadas > 0:
                    st.success(f"✅ Generadas {rutas_generadas} rutas frecuentes")
                    st.rerun()
                else:
                    st.warning("⚠️ No se pudieron generar rutas desde las órdenes")
    
    with col_gen3:
        if st.button("🗑️ Limpiar AVL"):
            st.session_state.avl_rutas = AVLRutas()
            st.success("✅ AVL de rutas limpiado")
            st.rerun()
    
    # === SECCIÓN 2: ESTADÍSTICAS DEL AVL ===
    st.markdown("---")
    st.subheader("📊 Estadísticas del Árbol AVL")
    
    stats_avl = st.session_state.avl_rutas.obtener_estadisticas_uso()
    
    if stats_avl['total_rutas'] == 0:
        st.info("📝 El árbol AVL está vacío. Genera rutas para comenzar el análisis.")
        return
    
    # Métricas principales
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    
    with col_met1:
        st.metric("🗺️ Total Rutas", stats_avl['total_rutas'])
    
    with col_met2:
        st.metric("🔄 Total Usos", stats_avl['total_usos'])
    
    with col_met3:
        st.metric("📈 Uso Promedio", f"{stats_avl['uso_promedio']:.1f}")
    
    with col_met4:
        st.metric("🌳 Altura Árbol", stats_avl['altura_arbol'])
    
    # === SECCIÓN 3: RUTAS MÁS FRECUENTES ===
    st.markdown("---")
    st.subheader("🔥 Rutas Más Frecuentes")
    
    rutas_frecuentes = st.session_state.avl_rutas.obtener_rutas_por_frecuencia(limite=10)
    rutas_filtradas = [r for r in rutas_frecuentes if r.frecuencia_uso >= min_frecuencia]
    
    if rutas_filtradas:
        # Tabla de rutas frecuentes
        col_tabla, col_detalles = st.columns([2, 1])
        
        with col_tabla:
            st.write("**📋 Top Rutas por Frecuencia**")
            
            datos_rutas = []
            for i, ruta in enumerate(rutas_filtradas[:10], 1):
                datos_rutas.append({
                    "Rank": i,
                    "Ruta ID": ruta.ruta_id,
                    "Origen": ruta.origen,
                    "Destino": ruta.destino,
                    "Frecuencia": ruta.frecuencia_uso,
                    "Distancia": f"{ruta.distancia:.2f} km",
                    "Camino": " → ".join(ruta.camino[:3]) + ("..." if len(ruta.camino) > 3 else "")
                })
            
            df_rutas = pd.DataFrame(datos_rutas)
            st.dataframe(df_rutas, use_container_width=True, hide_index=True)
        
        with col_detalles:
            st.write("**🏆 Estadísticas Destacadas**")
            
            if stats_avl['ruta_mas_usada']:
                st.success(f"🥇 **Ruta más usada:**")
                st.write(f"• {stats_avl['ruta_mas_usada'].origen} → {stats_avl['ruta_mas_usada'].destino}")
                st.write(f"• Usos: {stats_avl['ruta_mas_usada'].frecuencia_uso}")
                st.write(f"• Distancia: {stats_avl['ruta_mas_usada'].distancia:.2f} km")
            
            if stats_avl['rutas_nunca_usadas'] > 0:
                st.warning(f"⚠️ **Rutas sin uso:** {stats_avl['rutas_nunca_usadas']}")
        
        # === SECCIÓN 4: VISUALIZACIÓN DEL ÁRBOL AVL ===
        st.markdown("---")
        st.subheader("🌳 Visualización del Árbol AVL")
        
        if len(rutas_filtradas) <= 30:  # Limitar para evitar visualizaciones muy densas
            _crear_visualizacion_avl(rutas_filtradas)
        else:
            st.warning(f"⚠️ Demasiadas rutas para visualizar ({len(rutas_filtradas)}). Mostrando solo las top 30.")
            _crear_visualizacion_avl(rutas_filtradas[:30])
    
    else:
        st.info(f"📝 No hay rutas con frecuencia mínima de {min_frecuencia}. Ajusta el filtro o genera más rutas.")
    
    # === SECCIÓN 5: ANÁLISIS DETALLADO ===
    st.markdown("---")
    st.subheader("🔍 Análisis Detallado")
    
    col_analisis1, col_analisis2 = st.columns(2)
    
    with col_analisis1:
        st.write("**🎯 Búsqueda por Origen-Destino**")
        
        # Obtener nodos únicos del grafo
        vertices = list(st.session_state.grafo_actual.vertices())
        nodos_nombres = [v.element()['nombre'] for v in vertices]
        
        origen_busqueda = st.selectbox("Origen:", ["Seleccionar..."] + nodos_nombres, key="origen_busqueda_avl")
        destino_busqueda = st.selectbox("Destino:", ["Seleccionar..."] + nodos_nombres, key="destino_busqueda_avl")
        
        if origen_busqueda != "Seleccionar..." and destino_busqueda != "Seleccionar..." and origen_busqueda != destino_busqueda:
            rutas_origen_destino = st.session_state.avl_rutas.buscar_rutas_por_origen_destino(origen_busqueda, destino_busqueda)
            
            if rutas_origen_destino:
                st.success(f"✅ Encontradas {len(rutas_origen_destino)} rutas")
                for ruta in rutas_origen_destino:
                    st.write(f"• **{ruta.ruta_id}**: {ruta.frecuencia_uso} usos, {ruta.distancia:.2f} km")
            else:
                st.info("📝 No se encontraron rutas para esta combinación origen-destino")
    
    with col_analisis2:
        st.write("**📊 Propiedades del AVL**")
        
        col_prop1, col_prop2 = st.columns(2)
        
        with col_prop1:
            esta_balanceado = st.session_state.avl_rutas.es_balanceado()
            st.metric("⚖️ Balanceado", "Sí" if esta_balanceado else "No")
            
        with col_prop2:
            esta_vacio = st.session_state.avl_rutas.esta_vacio()
            st.metric("📭 Vacío", "Sí" if esta_vacio else "No")
        
        if st.button("🔧 Verificar Estructura"):
            if esta_balanceado:
                st.success("✅ El árbol AVL está correctamente balanceado")
            else:
                st.error("❌ El árbol AVL no está balanceado (esto no debería ocurrir)")
            
            st.info(f"📏 Factor de balanceo máximo permitido: ±1")
            st.info(f"🌳 Altura teórica mínima: {int(1.44 * stats_avl['total_rutas'])}")


def _generar_rutas_desde_ordenes(incluir_explorador=True):
    """Genera rutas frecuentes basándose en las órdenes y las añade al AVL"""
    from model import CalculadorDistancias
    from domain.route import crear_ruta_desde_camino, generar_id_ruta
    import random
    
    rutas_generadas = 0
    
    try:
        # Incluir rutas del explorador si está habilitado
        if incluir_explorador and hasattr(st.session_state, 'historial_rutas') and st.session_state.historial_rutas:
            for ruta_hist in st.session_state.historial_rutas:
                ruta_id = f"explorador_{ruta_hist['origen_id']}_{ruta_hist['destino_id']}"
                # Verificar si ya existe para incrementar uso
                if st.session_state.avl_rutas.buscar_ruta(ruta_id):
                    st.session_state.avl_rutas.incrementar_uso_ruta(ruta_id, 1)
                else:
                    # Crear nueva ruta desde historial
                    camino_nombres = [ruta_hist['origen_nombre'], ruta_hist['destino_nombre']]
                    ruta_info = crear_ruta_desde_camino(
                        ruta_id=ruta_id,
                        camino=camino_nombres,
                        distancia=ruta_hist['distancia'],
                        metadatos={"origen": "explorador", "saltos": ruta_hist['saltos']}
                    )
                    ruta_info.frecuencia_uso = 1
                    st.session_state.avl_rutas.insertar_ruta(ruta_info)
                    rutas_generadas += 1
        
        # Generar rutas desde órdenes
        grafo = st.session_state.grafo_actual
        vertices = list(grafo.vertices())
        nodos_dict = {v.element()['id']: v for v in vertices}
        
        # Crear rutas frecuentes basándose en las órdenes
        conteo_rutas = {}
        
        for orden in st.session_state.ordenes_actuales:
            origen_id = orden.origin
            destino_id = orden.destination
            
            # Buscar nodos en el grafo
            if origen_id in nodos_dict and destino_id in nodos_dict:
                nodo_origen = nodos_dict[origen_id]
                nodo_destino = nodos_dict[destino_id]
                
                # Intentar calcular ruta
                resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, nodo_origen, nodo_destino)
                
                if resultado:
                    camino, distancia_total = resultado
                    camino_nombres = [nodo.element()['nombre'] for nodo in camino]
                    
                    # Crear clave para la ruta
                    ruta_key = f"{camino_nombres[0]} → {camino_nombres[-1]}"
                    
                    if ruta_key not in conteo_rutas:
                        conteo_rutas[ruta_key] = {
                            'camino': camino_nombres,
                            'distancia': distancia_total,
                            'frecuencia': 0,
                            'origen': camino_nombres[0],
                            'destino': camino_nombres[-1]
                        }
                    
                    conteo_rutas[ruta_key]['frecuencia'] += 1
        
        # Insertar rutas en el AVL
        for i, (ruta_key, datos) in enumerate(conteo_rutas.items()):
            if datos['frecuencia'] >= 1:  # Solo rutas con al menos un uso
                ruta_id = generar_id_ruta(datos['origen'], datos['destino'], i)
                
                # Verificar si ya existe
                if st.session_state.avl_rutas.buscar_ruta(ruta_id):
                    st.session_state.avl_rutas.incrementar_uso_ruta(ruta_id, datos['frecuencia'])
                else:
                    ruta_info = crear_ruta_desde_camino(
                        ruta_id=ruta_id,
                        camino=datos['camino'],
                        distancia=datos['distancia'],
                        metadatos={
                            "origen": "ordenes_simulacion",
                            "tipo_generacion": "automatica"
                        }
                    )
                    ruta_info.frecuencia_uso = datos['frecuencia']
                    st.session_state.avl_rutas.insertar_ruta(ruta_info)
                    rutas_generadas += 1
        
        return rutas_generadas
        
    except Exception as e:
        st.error(f"Error generando rutas: {str(e)}")
        return 0


def _crear_visualizacion_avl(rutas_frecuentes):
    """Crea una visualización del árbol AVL usando NetworkX"""
    try:
        import networkx as nx
        import plotly.graph_objects as go
        import plotly.express as px
        import math
        
        # Crear grafo dirigido para la visualización
        G = nx.DiGraph()
        
        # Obtener todas las rutas del AVL y construir el árbol de visualización
        def agregar_nodo_recursivo(nodo_avl, G, pos_x=0, pos_y=0, nivel=0, parent=None):
            if nodo_avl is None:
                return
            
            # Crear ID único para el nodo en la visualización
            node_id = f"avl_{nodo_avl.key}"
            
            # Agregar nodo con información
            ruta_info = nodo_avl.ruta_info
            label = f"{ruta_info.origen} → {ruta_info.destino}"
            
            G.add_node(node_id, 
                      label=label,
                      frecuencia=ruta_info.frecuencia_uso,
                      distancia=ruta_info.distancia,
                      pos=(pos_x, pos_y),
                      nivel=nivel,
                      height=nodo_avl.height)
            
            # Agregar arista del padre si existe
            if parent:
                G.add_edge(parent, node_id)
            
            # Calcular posiciones para los hijos
            offset = max(1, 2 ** (3 - nivel))  # Espaciado dinámico
            
            # Recursivamente agregar hijos
            if nodo_avl.left:
                agregar_nodo_recursivo(nodo_avl.left, G, pos_x - offset, pos_y - 1, nivel + 1, node_id)
            
            if nodo_avl.right:
                agregar_nodo_recursivo(nodo_avl.right, G, pos_x + offset, pos_y - 1, nivel + 1, node_id)
        
        # Construir el grafo desde la raíz del AVL
        root = st.session_state.avl_rutas.root
        if root:
            agregar_nodo_recursivo(root, G)
            
            # Obtener posiciones
            pos = nx.get_node_attributes(G, 'pos')
            
            if not pos:  # Fallback si no hay posiciones
                pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Extraer coordenadas
            x_nodes = [pos[node][0] for node in G.nodes()]
            y_nodes = [pos[node][1] for node in G.nodes()]
            
            # Preparar datos para las aristas
            x_edges = []
            y_edges = []
            
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                x_edges.extend([x0, x1, None])
                y_edges.extend([y0, y1, None])
            
            # Preparar datos de los nodos
            node_labels = []
            node_colors = []
            node_sizes = []
            hover_texts = []
            
            for node in G.nodes():
                data = G.nodes[node]
                frecuencia = data.get('frecuencia', 0)
                
                # Etiqueta con formato especial para AVL
                label = data.get('label', node)
                node_labels.append(f"{label}<br>Freq: {frecuencia}")
                
                # Color basado en frecuencia (gradiente de azul a rojo)
                intensity = min(frecuencia / max(1, max(rutas_frecuentes, key=lambda r: r.frecuencia_uso).frecuencia_uso), 1)
                node_colors.append(intensity)
                
                # Tamaño basado en frecuencia
                size = 20 + (frecuencia * 5)
                node_sizes.append(min(size, 60))  # Limitar tamaño máximo
                
                # Texto de hover
                hover_text = f"""
                <b>{label}</b><br>
                Frecuencia: {frecuencia}<br>
                Distancia: {data.get('distancia', 0):.2f} km<br>
                Altura: {data.get('height', 0)}<br>
                Nivel: {data.get('nivel', 0)}
                """
                hover_texts.append(hover_text)
            
            # Crear figura
            fig = go.Figure()
            
            # Agregar aristas
            fig.add_trace(go.Scatter(
                x=x_edges, y=y_edges,
                mode='lines',
                line=dict(color='rgba(125,125,125,0.5)', width=2),
                hoverinfo='none',
                showlegend=False,
                name='Conexiones'
            ))
            
            # Agregar nodos
            fig.add_trace(go.Scatter(
                x=x_nodes, y=y_nodes,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    colorscale='Viridis',
                    colorbar=dict(
                        title="Frecuencia<br>de Uso",
                        x=1.02
                    ),
                    line=dict(width=2, color='rgba(50,50,50,0.8)')
                ),
                text=node_labels,
                textposition="middle center",
                textfont=dict(size=10, color='white'),
                hovertext=hover_texts,
                hoverinfo='text',
                showlegend=False,
                name='Rutas'
            ))
            
            # Configurar layout
            fig.update_layout(
                title={
                    'text': f"🌳 Árbol AVL de Rutas Frecuentes ({len(G.nodes())} nodos)",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(0,0,0,0)',
                height=600,
                margin=dict(l=20, r=80, t=60, b=20)
            )
            
            # Mostrar la visualización
            st.plotly_chart(fig, use_container_width=True)
            
            # Información adicional
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.info(f"🌳 **Nodos totales:** {len(G.nodes())}")
            
            with col_info2:
                st.info(f"🔗 **Conexiones:** {len(G.edges())}")
            
            with col_info3:
                altura_real = st.session_state.avl_rutas.altura()
                st.info(f"📏 **Altura real:** {altura_real}")
        
        else:
            st.warning("⚠️ El árbol AVL está vacío")
    
    except ImportError:
        st.error("❌ Error: Se requieren las librerías networkx y plotly para la visualización")
    except Exception as e:
        st.error(f"❌ Error creando visualización: {str(e)}")


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
                    valor_total = sum(orden.route_cost for orden in st.session_state.ordenes_actuales)
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

    # PESTAÑA 3: CLIENTES Y ÓRDENES
    with tab3:
        mostrar_clientes_y_ordenes()

    # PESTAÑA 4: RUTAS
    with tab4:
        mostrar_analisis_rutas()

    # PESTAÑA 5: HISTORIAL
    with tab5:
        st.info("🚧 Funcionalidad de historial en desarrollo")
        # mostrar_historial()

if __name__ == "__main__":
    main()

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

def mostrar_analisis_detallado():
    """Muestra análisis detallado del grafo actual"""
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay un grafo generado. Ve a la pestaña 'Simulación' para crear uno.")
        return
    
    st.header("📊 Análisis Detallado del Grafo")
    
    # Convertir a NetworkX si no existe
    if st.session_state.networkx_graph is None:
        st.session_state.networkx_graph = NetworkXAdapter.convertir_a_networkx(st.session_state.grafo_actual)
    
    nx_graph = st.session_state.networkx_graph
    
    # Métricas básicas
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📈 Métricas de Red")
        metricas = NetworkXAdapter.analizar_metricas_red(nx_graph)
        
        if metricas:
            # Mostrar métricas en una tabla
            df_metricas = pd.DataFrame([
                {"Métrica": "Número de Nodos", "Valor": metricas.get('num_nodos', 'N/A')},
                {"Métrica": "Número de Aristas", "Valor": metricas.get('num_aristas', 'N/A')},
                {"Métrica": "Densidad", "Valor": f"{metricas.get('densidad', 0):.4f}"},
                {"Métrica": "Conectado", "Valor": "Sí" if metricas.get('conectado', False) else "No"},
                {"Métrica": "Componentes Conexas", "Valor": metricas.get('num_componentes', 'N/A')},
                {"Métrica": "Grado Promedio", "Valor": f"{metricas.get('grado_promedio', 0):.2f}"},
                {"Métrica": "Grado Máximo", "Valor": metricas.get('grado_max', 'N/A')},
                {"Métrica": "Grado Mínimo", "Valor": metricas.get('grado_min', 'N/A')},
            ])
            
            if metricas.get('conectado', False):
                df_metricas = pd.concat([df_metricas, pd.DataFrame([
                    {"Métrica": "Diámetro", "Valor": metricas.get('diametro', 'N/A')},
                    {"Métrica": "Radio", "Valor": metricas.get('radio', 'N/A')},
                    {"Métrica": "Clustering Promedio", "Valor": f"{metricas.get('clustering_promedio', 0):.4f}"},
                ])], ignore_index=True)
            
            st.dataframe(df_metricas, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Distribución de Grados")
        fig_grados = NetworkXAdapter.crear_grafico_distribucion_grados(nx_graph)
        st.plotly_chart(fig_grados, use_container_width=True)
    
    # Visualización del grafo
    st.subheader("🌐 Visualización Interactiva")
    
    # Controles de visualización
    col_viz1, col_viz2, col_viz3 = st.columns(3)
    
    with col_viz1:
        layout_type = st.selectbox(
            "Tipo de Layout",
            ["spring", "circular", "kamada_kawai", "random"],
            help="Algoritmo de posicionamiento de nodos"
        )
    
    with col_viz2:
        mostrar_etiquetas = st.checkbox("Mostrar Etiquetas", value=True)
    
    with col_viz3:
        tamaño_figura = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande"], index=1)
    
    # Crear visualización
    if len(nx_graph.nodes()) <= 100:  # Limitar visualización para grafos grandes
        fig_grafo = NetworkXAdapter.crear_visualizacion_plotly(
            nx_graph, 
            titulo="Visualización del Grafo Generado"
        )
        
        altura = {"Pequeño": 400, "Mediano": 600, "Grande": 800}[tamaño_figura]
        fig_grafo.update_layout(height=altura)
        
        st.plotly_chart(fig_grafo, use_container_width=True)
    else:
        st.warning("⚠️ Grafo demasiado grande para visualización interactiva (>100 nodos)")
    
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
                    "Grado Máximo": info['grado_maximo'],
                    "Grado Mínimo": info['grado_minimo']
                })
            
            df_roles = pd.DataFrame(datos_roles)
            st.dataframe(df_roles, use_container_width=True, hide_index=True)

def mostrar_analisis_rutas():
    """Muestra herramientas de análisis de rutas"""
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay un grafo generado. Ve a la pestaña 'Simulación' para crear uno.")
        return
    
    st.header("🗺️ Análisis de Rutas")
    
    grafo = st.session_state.grafo_actual
    
    # Herramientas de búsqueda de rutas
    st.subheader("🔍 Búsqueda de Rutas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Seleccionar Nodo Origen**")
        vertices = list(grafo.vertices())
        opciones_origen = [f"ID {v.element()['id']} - {v.element()['nombre']}" for v in vertices]
        
        idx_origen = st.selectbox("Nodo Origen", range(len(opciones_origen)), 
                                 format_func=lambda x: opciones_origen[x])
        nodo_origen = vertices[idx_origen]
    
    with col2:
        st.write("**Seleccionar Nodo Destino**")
        opciones_destino = [f"ID {v.element()['id']} - {v.element()['nombre']}" for v in vertices]
        
        idx_destino = st.selectbox("Nodo Destino", range(len(opciones_destino)), 
                                  format_func=lambda x: opciones_destino[x])
        nodo_destino = vertices[idx_destino]
    
    # Calcular ruta más corta
    if st.button("🗺️ Calcular Ruta Más Corta"):
        if nodo_origen != nodo_destino:
            resultado = CalculadorDistancias.encontrar_camino_mas_corto(grafo, nodo_origen, nodo_destino)
            
            if resultado:
                camino, distancia = resultado
                
                # Mostrar información de la ruta
                st.success(f"✅ Ruta encontrada - Distancia: {distancia:.2f}")
                
                # Crear información de la ruta
                nombres_camino = [v.element()['nombre'] for v in camino]
                st.write(f"**Camino:** {' → '.join(nombres_camino)}")
                st.write(f"**Número de saltos:** {len(camino) - 1}")
                
                # Guardar ruta en AVL
                ruta_id = f"ruta_{nodo_origen.element()['id']}_{nodo_destino.element()['id']}"
                ruta_info = RutaInfo(
                    ruta_id=ruta_id,
                    origen=nodo_origen.element()['nombre'],
                    destino=nodo_destino.element()['nombre'],
                    camino=[v.element()['nombre'] for v in camino],
                    distancia=distancia
                )
                
                st.session_state.avl_rutas.insertar_ruta(ruta_info)
                st.info("💾 Ruta guardada en el sistema de rutas")
                
                # Visualizar ruta si el grafo no es muy grande
                if st.session_state.networkx_graph and len(st.session_state.networkx_graph.nodes()) <= 50:
                    ids_camino = [v.element()['id'] for v in camino]
                    fig_ruta = NetworkXAdapter.resaltar_ruta_en_grafo(
                        st.session_state.networkx_graph, ids_camino
                    )
                    st.plotly_chart(fig_ruta, use_container_width=True)
                
            else:
                st.error("❌ No se encontró una ruta entre los nodos seleccionados")
        else:
            st.warning("⚠️ El nodo origen y destino deben ser diferentes")
    
    # Búsqueda por roles
    st.subheader("🎯 Búsqueda por Roles")
    
    col_rol1, col_rol2 = st.columns(2)
    
    with col_rol1:
        rol_buscado = st.selectbox(
            "Rol a Buscar",
            [RolNodo.ALMACENAMIENTO, RolNodo.RECARGA, RolNodo.CLIENTE],
            format_func=lambda x: x.title()
        )
    
    with col_rol2:
        k_cercanos = st.slider("Número de nodos más cercanos", 1, 10, 3)
    
    if st.button("🔍 Buscar Nodos Más Cercanos"):
        resultado_k = BuscadorNodos.buscar_k_nodos_mas_cercanos_por_rol(
            grafo, nodo_origen, rol_buscado, k_cercanos
        )
        
        if resultado_k:
            st.success(f"✅ Encontrados {len(resultado_k)} nodos de tipo '{rol_buscado}'")
            
            # Mostrar tabla de resultados
            datos_cercanos = []
            for i, (nodo, distancia) in enumerate(resultado_k, 1):
                datos_cercanos.append({
                    "Posición": i,
                    "Nodo": nodo.element()['nombre'],
                    "ID": nodo.element()['id'],
                    "Distancia": f"{distancia:.2f}"
                })
            
            df_cercanos = pd.DataFrame(datos_cercanos)
            st.dataframe(df_cercanos, use_container_width=True, hide_index=True)
            
        else:
            st.warning(f"⚠️ No se encontraron nodos del tipo '{rol_buscado}'")
    
    # Gestión de rutas guardadas
    st.subheader("💾 Rutas Guardadas")
    
    if not st.session_state.avl_rutas.esta_vacio():
        rutas_guardadas = st.session_state.avl_rutas.listar_todas_rutas()
        
        # Mostrar estadísticas de rutas
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.metric("Total Rutas", len(rutas_guardadas))
        
        with col_stats2:
            distancia_promedio = sum(r.distancia for r in rutas_guardadas) / len(rutas_guardadas)
            st.metric("Distancia Promedio", f"{distancia_promedio:.2f}")
        
        with col_stats3:
            ruta_mas_larga = max(rutas_guardadas, key=lambda r: r.distancia)
            st.metric("Ruta Más Larga", f"{ruta_mas_larga.distancia:.2f}")
        
        # Tabla de rutas
        datos_rutas = []
        for ruta in rutas_guardadas:
            datos_rutas.append({
                "ID": ruta.ruta_id,
                "Origen": ruta.origen,
                "Destino": ruta.destino,
                "Distancia": f"{ruta.distancia:.2f}",
                "Saltos": len(ruta.camino) - 1,
                "Último Uso": ruta.ultimo_uso.strftime("%H:%M:%S")
            })
        
        df_rutas = pd.DataFrame(datos_rutas)
        st.dataframe(df_rutas, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Limpiar Rutas Guardadas"):
            st.session_state.avl_rutas = AVLRutas()
            st.rerun()
    else:
        st.info("📝 No hay rutas guardadas. Calcula algunas rutas para verlas aquí.")

def mostrar_historial():
    """Muestra el historial de simulaciones"""
    st.header("📈 Historial de Simulaciones")
    
    if not st.session_state.historial_simulaciones:
        st.info("📝 No hay simulaciones en el historial. Ejecuta algunas simulaciones para verlas aquí.")
        return
    
    # Estadísticas del historial
    st.subheader("📊 Resumen del Historial")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Simulaciones", len(st.session_state.historial_simulaciones))
    
    with col2:
        nodos_promedio = sum(s['estadisticas']['numero_vertices'] 
                           for s in st.session_state.historial_simulaciones) / len(st.session_state.historial_simulaciones)
        st.metric("Nodos Promedio", f"{nodos_promedio:.1f}")
    
    with col3:
        conectadas = sum(1 for s in st.session_state.historial_simulaciones 
                        if s['estadisticas']['esta_conectado'])
        pct_conectadas = (conectadas / len(st.session_state.historial_simulaciones)) * 100
        st.metric("% Conectadas", f"{pct_conectadas:.1f}%")
    
    with col4:
        densidad_promedio = sum(s['estadisticas']['densidad'] 
                              for s in st.session_state.historial_simulaciones) / len(st.session_state.historial_simulaciones)
        st.metric("Densidad Promedio", f"{densidad_promedio:.3f}")
    
    # Gráficos de tendencias
    st.subheader("📈 Tendencias")
    
    # Preparar datos para gráficos
    df_historial = []
    for i, sim in enumerate(st.session_state.historial_simulaciones):
        df_historial.append({
            'Simulación': i + 1,
            'Timestamp': datetime.fromtimestamp(sim['timestamp']),
            'Nodos': sim['estadisticas']['numero_vertices'],
            'Aristas': sim['estadisticas']['numero_aristas'],
            'Densidad': sim['estadisticas']['densidad'],
            'Conectado': sim['estadisticas']['esta_conectado'],
            'Prob_Arista': sim['configuracion']['prob_arista'],
            'Almacenamiento_%': sim['configuracion']['pct_almacenamiento'],
            'Recarga_%': sim['configuracion']['pct_recarga'],
            'Cliente_%': sim['configuracion']['pct_cliente']
        })
    
    df = pd.DataFrame(df_historial)
    
    # Gráfico de evolución de nodos y aristas
    fig_evolucion = go.Figure()
    
    fig_evolucion.add_trace(go.Scatter(
        x=df['Simulación'],
        y=df['Nodos'],
        mode='lines+markers',
        name='Nodos',
        line=dict(color='blue')
    ))
    
    fig_evolucion.add_trace(go.Scatter(
        x=df['Simulación'],
        y=df['Aristas'],
        mode='lines+markers',
        name='Aristas',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig_evolucion.update_layout(
        title="Evolución de Nodos y Aristas",
        xaxis_title="Número de Simulación",
        yaxis=dict(title="Nodos", side="left"),
        yaxis2=dict(title="Aristas", side="right", overlaying="y"),
        height=400
    )
    
    st.plotly_chart(fig_evolucion, use_container_width=True)
    
    # Tabla detallada del historial
    st.subheader("📋 Detalle del Historial")
    
    # Formatear datos para mostrar
    df_display = df.copy()
    df_display['Timestamp'] = df_display['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_display['Conectado'] = df_display['Conectado'].map({True: '✅', False: '❌'})
    df_display['Densidad'] = df_display['Densidad'].round(4)
    df_display['Prob_Arista'] = df_display['Prob_Arista'].round(3);
    
    st.dataframe(
        df_display[[
            'Simulación', 'Timestamp', 'Nodos', 'Aristas', 
            'Densidad', 'Conectado', 'Prob_Arista'
        ]], 
        use_container_width=True, 
        hide_index=True
    )
    
    # Controles del historial
    st.subheader("🔧 Controles")
    
    col_ctrl1, col_ctrl2 = st.columns(2)
    
    with col_ctrl1:
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.historial_simulaciones = []
            st.rerun()
    
    with col_ctrl2:
        if st.button("📊 Análisis Comparativo"):
            st.info("🚧 Función de análisis comparativo en desarrollo")

def mostrar_clientes_y_ordenes():
    """Muestra información de clientes y órdenes del sistema"""
    if st.session_state.grafo_actual is None:
        st.warning("⚠️ No hay un grafo generado. Ve a la pestaña 'Simulación' para crear uno.")
        return
    
    st.header("👥 Clientes y Órdenes del Sistema")
    
    # Verificar si hay datos generados
    if not st.session_state.clientes_actuales and not st.session_state.ordenes_actuales:
        st.info("📝 No hay datos de clientes y órdenes generados. Los datos se crean automáticamente al ejecutar una simulación.")
        return
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Clientes",
            value=len(st.session_state.clientes_actuales),
            help="Número total de clientes en el sistema"
        )
    
    with col2:
        clientes_activos = len([c for c in st.session_state.clientes_actuales if c.estado == EstadoCliente.ACTIVO])
        st.metric(
            label="✅ Clientes Activos",
            value=clientes_activos,
            help="Clientes con estado activo"
        )
    
    with col3:
        st.metric(
            label="📋 Total Órdenes",
            value=len(st.session_state.ordenes_actuales),
            help="Número total de órdenes en el sistema"
        )
    
    with col4:
        if st.session_state.ordenes_actuales:
            valor_total = sum(orden.costo_total for orden in st.session_state.ordenes_actuales)
            st.metric(
                label="💰 Valor Total",
                value=f"${valor_total:,.2f}",
                help="Valor total de todas las órdenes"
            )
    
    # Pestañas secundarias
    tab_clientes, tab_ordenes = st.tabs(["👥 Clientes", "📋 Órdenes"])
    
    # PESTAÑA CLIENTES
    with tab_clientes:
        st.subheader("📊 Lista de Clientes")
        
        if st.session_state.clientes_actuales:
            # Filtros para clientes
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                filtro_tipo = st.selectbox(
                    "Filtrar por Tipo",
                    ["Todos"] + [tipo.value for tipo in TipoCliente],
                    key="filtro_tipo_cliente"
                )
            
            with col_filtro2:
                filtro_estado = st.selectbox(
                    "Filtrar por Estado",
                    ["Todos"] + [estado.value for estado in EstadoCliente],
                    key="filtro_estado_cliente"
                )
            
            with col_filtro3:
                ordenar_por = st.selectbox(
                    "Ordenar por",
                    ["Nombre", "Total Pedidos", "Total Gastado", "Fecha Registro"],
                    key="ordenar_clientes"
                )
            
            # Aplicar filtros
            clientes_filtrados = st.session_state.clientes_actuales.copy()
            
            if filtro_tipo != "Todos":
                clientes_filtrados = [c for c in clientes_filtrados if c.tipo.value == filtro_tipo]
            
            if filtro_estado != "Todos":
                clientes_filtrados = [c for c in clientes_filtrados if c.estado.value == filtro_estado]
            
            # Ordenar
            if ordenar_por == "Nombre":
                clientes_filtrados.sort(key=lambda c: c.nombre)
            elif ordenar_por == "Total Pedidos":
                clientes_filtrados.sort(key=lambda c: c.total_pedidos, reverse=True)
            elif ordenar_por == "Total Gastado":
                clientes_filtrados.sort(key=lambda c: c.total_gastado, reverse=True)
            elif ordenar_por == "Fecha Registro":
                clientes_filtrados.sort(key=lambda c: c.fecha_registro, reverse=True)
            
            # Mostrar resumen de filtros
            st.write(f"**Mostrando {len(clientes_filtrados)} de {len(st.session_state.clientes_actuales)} clientes**")
            
            # Preparar datos para mostrar
            datos_clientes = []
            for cliente in clientes_filtrados:
                resumen = cliente.obtener_resumen()
                datos_clientes.append({
                    "ID": resumen['cliente_id'],
                    "Nombre": resumen['nombre'],
                    "Tipo": resumen['tipo'].title(),
                    "Estado": resumen['estado'].title(),
                    "Ubicación": resumen['nodo_ubicacion'],
                    "Total Pedidos": resumen['total_pedidos'],
                    "Completados": resumen['pedidos_completados'],
                    "Cancelados": resumen['pedidos_cancelados'],
                    "Total Gastado": f"${resumen['total_gastado']:,.2f}",
                    "Promedio Pedido": f"${resumen['promedio_valor_pedido']:,.2f}",
                    "Tasa Éxito": f"{resumen['tasa_completado']:.1f}%",
                    "Límite Crédito": f"${resumen['limite_credito']:,.2f}",
                    "Email": resumen['email'],
                    "Teléfono": resumen['telefono']
                })
            
            # Mostrar tabla de clientes
            if datos_clientes:
                st.dataframe(
                    datos_clientes,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Sección de detalles en JSON
                st.subheader("📄 Detalles Completos de Clientes")
                
                # Selector de cliente para mostrar detalles
                nombres_clientes = [f"{c.cliente_id} - {c.nombre}" for c in clientes_filtrados]
                if nombres_clientes:
                    cliente_seleccionado_idx = st.selectbox(
                        "Seleccionar cliente para ver detalles:",
                        range(len(nombres_clientes)),
                        format_func=lambda x: nombres_clientes[x],
                        key="selector_cliente_detalle"
                    )
                    
                    if cliente_seleccionado_idx is not None:
                        cliente_detalle = clientes_filtrados[cliente_seleccionado_idx]
                        st.json(cliente_detalle.obtener_resumen())
            else:
                st.info("No hay clientes que coincidan con los filtros seleccionados.")
        
        else:
            st.info("📝 No hay clientes generados.")
    
    # PESTAÑA ÓRDENES
    with tab_ordenes:
        st.subheader("📋 Lista de Órdenes")
        
        if st.session_state.ordenes_actuales:
            # Filtros para órdenes
            col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
            
            with col_filtro1:
                filtro_estado_orden = st.selectbox(
                    "Filtrar por Estado",
                    ["Todos"] + [estado.value for estado in EstadoOrden],
                    key="filtro_estado_orden"
                )
            
            with col_filtro2:
                filtro_prioridad = st.selectbox(
                    "Filtrar por Prioridad",
                    ["Todas"] + [f"{p.value} ({p.name})" for p in PrioridadOrden],
                    key="filtro_prioridad_orden"
                )
            
            with col_filtro3:
                ordenar_ordenes_por = st.selectbox(
                    "Ordenar por",
                    ["Fecha Creación", "Valor Total", "Prioridad", "Estado"],
                    key="ordenar_ordenes"
                )
            
            # Aplicar filtros
            ordenes_filtradas = st.session_state.ordenes_actuales.copy()
            
            if filtro_estado_orden != "Todos":
                ordenes_filtradas = [o for o in ordenes_filtradas if o.estado.value == filtro_estado_orden]
            
            if filtro_prioridad != "Todas":
                prioridad_numero = filtro_prioridad.split(" (")[1].replace(")", "")
                ordenes_filtradas = [o for o in ordenes_filtradas if o.prioridad.name == prioridad_numero]
            
            # Ordenar
            if ordenar_ordenes_por == "Fecha Creación":
                ordenes_filtradas.sort(key=lambda o: o.fecha_creacion, reverse=True)
            elif ordenar_ordenes_por == "Valor Total":
                ordenes_filtradas.sort(key=lambda o: o.costo_total, reverse=True)
            elif ordenar_ordenes_por == "Prioridad":
                ordenes_filtradas.sort(key=lambda o: o.prioridad.value, reverse=True)
            elif ordenar_ordenes_por == "Estado":
                ordenes_filtradas.sort(key=lambda o: o.estado.value)
            
            # Mostrar resumen de filtros
            st.write(f"**Mostrando {len(ordenes_filtradas)} de {len(st.session_state.ordenes_actuales)} órdenes**")
            
            # Preparar datos para mostrar
            datos_ordenes = []
            for orden in ordenes_filtradas:
                resumen = orden.obtener_resumen()
                
                # Formatear estado con emoji
                estado_emoji = {
                    "pendiente": "⏳",
                    "confirmada": "✅",
                    "en_preparacion": "📦",
                    "en_transito": "🚚",
                    "entregada": "✅",
                    "cancelada": "❌",
                    "devuelta": "↩️"
                }
                
                estado_formato = f"{estado_emoji.get(resumen['estado'], '❓')} {resumen['estado'].title()}"
                
                # Formatear prioridad con color
                prioridad_emoji = {
                    1: "🟢",  # Baja
                    2: "🟡",  # Media
                    3: "🟠",  # Alta
                    4: "🔴"   # Crítica
                }
                
                prioridad_formato = f"{prioridad_emoji.get(resumen['prioridad'], '⚪')} {PrioridadOrden(resumen['prioridad']).name.title()}"
                
                datos_ordenes.append({
                    "ID": resumen['orden_id'],
                    "Cliente ID": resumen['cliente_id'],
                    "Tipo": resumen['tipo'].title(),
                    "Estado": estado_formato,
                    "Prioridad": prioridad_formato,
                    "Origen": resumen['nodo_origen'],
                    "Destino": resumen['nodo_destino'],
                    "Descripción": resumen['descripcion'],
                    "Valor Base": f"${resumen['valor_base']:,.2f}",
                    "Costo Envío": f"${resumen['costo_envio']:,.2f}",
                    "Costo Total": f"${resumen['costo_total']:,.2f}",
                    "Peso (kg)": resumen['peso_kg'],
                    "Fecha Creación": datetime.fromisoformat(resumen['fecha_creacion']).strftime("%Y-%m-%d %H:%M"),
                    "Entrega Solicitada": datetime.fromisoformat(resumen['fecha_entrega_solicitada']).strftime("%Y-%m-%d"),
                    "Vencida": "🔴 Sí" if resumen['esta_vencida'] else "🟢 No",
                    "Tiempo Transcurrido": f"{resumen['tiempo_transcurrido_total']:.1f}h"
                })
            
            # Mostrar tabla de órdenes
            if datos_ordenes:
                st.dataframe(
                    datos_ordenes,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Estadísticas adicionales
                st.subheader("📊 Estadísticas de Órdenes")
                
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                
                with col_stats1:
                    # Distribución por estado
                    distribucion_estado = {}
                    for orden in ordenes_filtradas:
                        estado = orden.estado.value
                        distribucion_estado[estado] = distribucion_estado.get(estado, 0) + 1
                    
                    st.write("**Por Estado:**")
                    for estado, cantidad in distribucion_estado.items():
                        st.write(f"• {estado.title()}: {cantidad}")
                
                with col_stats2:
                    # Distribución por prioridad
                    distribucion_prioridad = {}
                    for orden in ordenes_filtradas:
                        prioridad = PrioridadOrden(orden.prioridad.value).name
                        distribucion_prioridad[prioridad] = distribucion_prioridad.get(prioridad, 0) + 1
                    
                    st.write("**Por Prioridad:**")
                    for prioridad, cantidad in distribucion_prioridad.items():
                        st.write(f"• {prioridad.title()}: {cantidad}")
                
                with col_stats3:
                    # Métricas financieras
                    if ordenes_filtradas:
                        valor_promedio = sum(o.costo_total for o in ordenes_filtradas) / len(ordenes_filtradas)
                        orden_max_valor = max(ordenes_filtradas, key=lambda o: o.costo_total)
                        
                        st.write("**Métricas Financieras:**")
                        st.write(f"• Valor Promedio: ${valor_promedio:,.2f}")
                        st.write(f"• Orden Máxima: ${orden_max_valor.costo_total:,.2f}")
                
                # Sección de detalles en JSON
                st.subheader("📄 Detalles Completos de Órdenes")
                
                # Selector de orden para mostrar detalles
                nombres_ordenes = [f"{o.orden_id} - {o.descripcion}" for o in ordenes_filtradas]
                if nombres_ordenes:
                    orden_seleccionada_idx = st.selectbox(
                        "Seleccionar orden para ver detalles:",
                        range(len(nombres_ordenes)),
                        format_func=lambda x: nombres_ordenes[x],
                        key="selector_orden_detalle"
                    )
                    
                    if orden_seleccionada_idx is not None:
                        orden_detalle = ordenes_filtradas[orden_seleccionada_idx]
                        st.json(orden_detalle.obtener_resumen())
            else:
                st.info("No hay órdenes que coincidan con los filtros seleccionados.")
        
        else:
            st.info("📝 No hay órdenes generadas.")

# ...existing code...

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
        "📊 Análisis", 
        "👥 Clients & Orders",
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

    # PESTAÑA 2: ANÁLISIS
    with tab2:
        mostrar_analisis_detallado()

    # PESTAÑA 3: CLIENTES Y ÓRDENES
    with tab3:
        mostrar_clientes_y_ordenes()

    # PESTAÑA 4: RUTAS
    with tab4:
        mostrar_analisis_rutas()

    # PESTAÑA 5: HISTORIAL
    with tab5:
        mostrar_historial()

if __name__ == "__main__":
    main()

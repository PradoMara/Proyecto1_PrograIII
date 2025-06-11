import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.simulation import DroneSimulation

# Configuración de la página
st.set_page_config(
    page_title="Simulación Drones - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar simulación en session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = DroneSimulation()

# Título principal
st.title("🚁 Simulación Logística de Drones - Correos Chile")
st.markdown("---")

# Sidebar para navegación
st.sidebar.title("🎛️ Panel de Control")
tab_selection = st.sidebar.selectbox(
    "Seleccionar Pestaña:",
    ["🔄 Run Simulation", "🌍 Explore Network", "🌐 Clients & Orders", 
     "📋 Route Analytics", "📈 General Statistics"]
)

# =================== PESTAÑA 1: RUN SIMULATION ===================
if tab_selection == "🔄 Run Simulation":
    st.header("🔄 Configuración e Inicio de Simulación")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⚙️ Parámetros de Simulación")
        
        # Sliders para configuración
        n_nodes = st.slider(
            "🔹 Número de Nodos",
            min_value=10,
            max_value=150,
            value=15,
            help="Cantidad total de nodos en la red (máximo 150)"
        )
        
        min_edges = n_nodes - 1
        max_edges = min(300, n_nodes * (n_nodes - 1) // 2)
        
        m_edges = st.slider(
            "🔹 Número de Aristas",
            min_value=min_edges,
            max_value=max_edges,
            value=max(20, min_edges),
            help=f"Cantidad de conexiones entre nodos (mínimo {min_edges} para conectividad)"
        )
        
        n_orders = st.slider(
            "🔹 Número de Órdenes",
            min_value=1,
            max_value=500,
            value=10,
            help="Cantidad de órdenes de entrega a generar"
        )
    
    with col2:
        st.subheader("📊 Información de la Red")
        
        # Calcular distribución
        n_storage = max(1, int(n_nodes * 0.20))
        n_charging = max(1, int(n_nodes * 0.20))
        n_clients = n_nodes - n_storage - n_charging
        
        st.info(f"""
        **Distribución de Nodos:**
        - 📦 Almacenamiento: {n_storage} ({n_storage/n_nodes*100:.1f}%)
        - 🔋 Recarga: {n_charging} ({n_charging/n_nodes*100:.1f}%)
        - 👤 Clientes: {n_clients} ({n_clients/n_nodes*100:.1f}%)
        
        **Configuración:**
        - Total Nodos: {n_nodes}
        - Total Aristas: {m_edges}
        - Total Órdenes: {n_orders}
        - Autonomía Dron: 50 unidades
        """)
    
    st.markdown("---")
    
    # Botón para iniciar simulación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 Iniciar Simulación", type="primary", use_container_width=True):
            with st.spinner("Generando red de drones..."):
                success = st.session_state.simulation.initialize_simulation(n_nodes, m_edges, n_orders)
                
                if success:
                    st.balloons()

# =================== PESTAÑA 2: EXPLORE NETWORK ===================
elif tab_selection == "🌍 Explore Network":
    st.header("🌍 Exploración de la Red")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero en la pestaña 'Run Simulation'.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Visualización de la Red")
            
            # Mostrar grafo
            if 'current_path' not in st.session_state:
                st.session_state.current_path = None
            
            fig = st.session_state.simulation.get_network_visualization(st.session_state.current_path)
            if fig:
                st.pyplot(fig)
            else:
                st.error("Error al generar la visualización de la red.")
        
        with col2:
            st.subheader("🛣️ Calculadora de Rutas")
            
            # Selectores de origen y destino
            node_options = st.session_state.simulation.get_node_options()
            
            if node_options:
                origin_options = [(id, label) for id, label in node_options]
                destination_options = [(id, label) for id, label in node_options]
                
                selected_origin = st.selectbox(
                    "📍 Nodo Origen:",
                    options=[id for id, _ in origin_options],
                    format_func=lambda x: next(label for id, label in origin_options if id == x),
                    key="origin_select"
                )
                
                selected_destination = st.selectbox(
                    "📍 Nodo Destino:",
                    options=[id for id, _ in destination_options],
                    format_func=lambda x: next(label for id, label in destination_options if id == x),
                    key="destination_select"
                )
                
                # Selector de algoritmo
                algorithm = st.selectbox(
                    "🔍 Algoritmo de Búsqueda:",
                    ["BFS", "DFS", "Topological Sort"],
                    help="Algoritmo para encontrar la ruta"
                )
                
                # Botón para calcular ruta
                if st.button("✈️ Calcular Ruta", type="primary", use_container_width=True):
                    if selected_origin != selected_destination:
                        with st.spinner("Calculando ruta..."):
                            route_info = st.session_state.simulation.calculate_route(
                                selected_origin, selected_destination, algorithm
                            )
                            
                            if route_info:
                                st.session_state.current_path = route_info['path']
                                st.session_state.current_route_info = route_info
                                st.session_state.current_origin = selected_origin
                                st.session_state.current_destination = selected_destination
                                st.rerun()
                    else:
                        st.error("El origen y destino deben ser diferentes.")
                
                # Mostrar información de la ruta actual
                if 'current_route_info' in st.session_state and st.session_state.current_route_info:
                    route_info = st.session_state.current_route_info
                    
                    st.success(f"""
                    **Ruta Encontrada:**
                    
                    📍 **Camino:** {route_info['path_string']}
                    
                    💰 **Costo Total:** {route_info['cost']} unidades
                    
                    🔋 **Estado:** {'Requiere recarga' if route_info['requires_charging'] else 'Autonomía suficiente'}
                    
                    ✅ **Válida:** {'Sí' if route_info['valid'] else 'No'}
                    """)
                    
                    # Botón para completar entrega
                    if st.button("✅ Completar Entrega y Crear Orden", type="secondary", use_container_width=True):
                        success = st.session_state.simulation.complete_delivery(
                            route_info, 
                            st.session_state.current_origin, 
                            st.session_state.current_destination
                        )
                        if success:
                            st.session_state.current_path = None
                            st.session_state.current_route_info = None
                            st.rerun()
            
            else:
                st.error("No hay nodos disponibles.")

# =================== PESTAÑA 3: CLIENTS & ORDERS ===================
elif tab_selection == "🌐 Clients & Orders":
    st.header("🌐 Clientes y Órdenes")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero en la pestaña 'Run Simulation'.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Lista de Clientes")
            clients_data = st.session_state.simulation.get_clients_data()
            
            if clients_data:
                st.json(clients_data)
            else:
                st.info("No hay clientes registrados.")
        
        with col2:
            st.subheader("📦 Lista de Órdenes")
            orders_data = st.session_state.simulation.get_orders_data()
            
            if orders_data:
                # Mostrar como tabla para mejor legibilidad
                df_orders = pd.DataFrame(orders_data)
                st.dataframe(df_orders, use_container_width=True)
                
                # Mostrar también como JSON si se prefiere
                with st.expander("Ver como JSON"):
                    st.json(orders_data)
            else:
                st.info("No hay órdenes registradas.")

# =================== PESTAÑA 4: ROUTE ANALYTICS ===================
elif tab_selection == "📋 Route Analytics":
    st.header("📋 Análisis de Rutas")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero en la pestaña 'Run Simulation'.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Rutas Más Frecuentes")
            frequent_routes = st.session_state.simulation.get_route_analytics()
            
            if frequent_routes:
                # Crear DataFrame para mejor visualización
                df_routes = pd.DataFrame(frequent_routes, columns=['Ruta', 'Frecuencia'])
                st.dataframe(df_routes, use_container_width=True)
                
                # Gráfico de barras
                fig = px.bar(
                    df_routes.head(10), 
                    x='Frecuencia', 
                    y='Ruta',
                    orientation='h',
                    title="Top 10 Rutas Más Utilizadas"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay rutas registradas aún. Complete algunas entregas primero.")
        
        with col2:
            st.subheader("🌳 Visualización del Árbol AVL")
            avl_fig = st.session_state.simulation.get_avl_visualization()
            
            if avl_fig:
                st.pyplot(avl_fig)
            else:
                st.info("El árbol AVL está vacío.")

# =================== PESTAÑA 5: GENERAL STATISTICS ===================
elif tab_selection == "📈 General Statistics":
    st.header("📈 Estadísticas Generales")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero en la pestaña 'Run Simulation'.")
    else:
        # Obtener estadísticas de visitas
        storage_visits, charging_visits, client_visits = st.session_state.simulation.get_visit_statistics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Nodos Más Visitados por Tipo")
            
            # Crear gráfico de barras comparativo
            all_visits = []
            
            # Top 5 de cada tipo
            top_storage = sorted(storage_visits.items(), key=lambda x: x[1], reverse=True)[:5]
            top_charging = sorted(charging_visits.items(), key=lambda x: x[1], reverse=True)[:5]
            top_client = sorted(client_visits.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for node, visits in top_storage:
                all_visits.append({"Nodo": node, "Visitas": visits, "Tipo": "Almacenamiento"})
            
            for node, visits in top_charging:
                all_visits.append({"Nodo": node, "Visitas": visits, "Tipo": "Recarga"})
            
            for node, visits in top_client:
                all_visits.append({"Nodo": node, "Visitas": visits, "Tipo": "Cliente"})
            
            if all_visits:
                df_visits = pd.DataFrame(all_visits)
                
                fig = px.bar(
                    df_visits, 
                    x="Visitas", 
                    y="Nodo", 
                    color="Tipo",
                    orientation='h',
                    title="Nodos Más Visitados por Categoría",
                    color_discrete_map={
                        "Almacenamiento": "#FF6B6B",
                        "Recarga": "#4ECDC4", 
                        "Cliente": "#45B7D1"
                    }
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de visitas aún. Calcule algunas rutas primero.")
        
        with col2:
            st.subheader("🥧 Distribución de Nodos por Tipo")
            
            # Obtener estadísticas de la red
            stats = st.session_state.simulation.get_network_stats()
            
            if stats:
                # Gráfico de torta
                labels = ['📦 Almacenamiento', '🔋 Recarga', '👤 Clientes']
                values = [
                    stats['storage']['count'],
                    stats['charging']['count'],
                    stats['client']['count']
                ]
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels, 
                    values=values,
                    marker=dict(colors=colors),
                    hole=0.4
                )])
                
                fig.update_layout(
                    title="Proporción de Nodos por Rol",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas adicionales
                st.subheader("📊 Métricas del Sistema")
                
                col2a, col2b, col2c = st.columns(3)
                
                with col2a:
                    st.metric("Total Nodos", stats['total_nodes'])
                    st.metric("Total Aristas", stats['total_edges'])
                
                with col2b:
                    st.metric("Total Órdenes", stats['total_orders'])
                    completed_orders = len([o for o in st.session_state.simulation.graph.orders if o.status == "Entregado"])
                    st.metric("Órdenes Completadas", completed_orders)
                
                with col2c:
                    total_visits = sum(storage_visits.values()) + sum(charging_visits.values()) + sum(client_visits.values())
                    st.metric("Total Visitas", total_visits)
                    
                    if stats['total_orders'] > 0:
                        completion_rate = (completed_orders / stats['total_orders']) * 100
                        st.metric("Tasa de Completitud", f"{completion_rate:.1f}%")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        🚁 Simulación Logística de Drones - Correos Chile | 
        Desarrollado con ❤️ usando Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)

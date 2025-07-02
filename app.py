import streamlit as st
import pandas as pd
from utils.simulation import DroneSimulation
from utils.api_integration import save_simulation_to_api

# Configuración de la página
st.set_page_config(
    page_title="Simulación Drones - Correos Chile",
    page_icon="🚁",
    layout="wide"
)

# Inicializar simulación en session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = DroneSimulation()

# Título principal
st.title("🚁 Simulación Logística de Drones - Correos Chile")

# Navegación
tab_selection = st.selectbox(
    "Seleccionar Pestaña:",
    ["🔄 Run Simulation", "🌍 Explore Network", "🌐 Clients & Orders", 
     "📋 Route Analytics", "📈 General Statistics"]
)

# =================== PESTAÑA 1: RUN SIMULATION ===================
if tab_selection == "🔄 Run Simulation":
    st.header("🔄 Configuración e Inicio de Simulación")
    
    # Sliders para configuración
    n_nodes = st.slider("🔹 Número de Nodos", min_value=10, max_value=150, value=15)
    min_edges = n_nodes - 1
    m_edges = st.slider("🔹 Número de Aristas", min_value=min_edges, max_value=300, value=20)
    n_orders = st.slider("🔹 Número de Órdenes", min_value=10, max_value=300, value=10)
    
    # Información de distribución
    n_storage = max(1, int(n_nodes * 0.20))
    n_charging = max(1, int(n_nodes * 0.20))
    n_clients = n_nodes - n_storage - n_charging
    
    st.info(f"""
    **Distribución de Nodos:**
    - 📦 Almacenamiento: {n_storage} ({n_storage/n_nodes*100:.1f}%)
    - 🔋 Recarga: {n_charging} ({n_charging/n_nodes*100:.1f}%)
    - 👤 Clientes: {n_clients} ({n_clients/n_nodes*100:.1f}%)
    """)
    
    # Botón para iniciar simulación
    if st.button("📊 Start Simulation", type="primary"):
        with st.spinner("Generando red de drones..."):
            success = st.session_state.simulation.initialize_simulation(n_nodes, m_edges, n_orders)
            if success:
                # Guardar datos para la API
                save_simulation_to_api(st.session_state.simulation)
                st.success("🎉 Simulación inicializada exitosamente!")
                st.info("📡 Datos guardados para acceso desde la API")

# =================== PESTAÑA 2: EXPLORE NETWORK ===================
elif tab_selection == "🌍 Explore Network":
    st.header("🌍 Exploración de la Red")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero.")
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
        
        with col2:
            st.subheader("🛣️ Calculadora de Rutas")
            
            node_options = st.session_state.simulation.get_node_options()
            
            if node_options:
                selected_origin = st.selectbox(
                    "📍 Nodo Origen:",
                    options=[id for id, _ in node_options],
                    format_func=lambda x: next(label for id, label in node_options if id == x)
                )
                
                selected_destination = st.selectbox(
                    "📍 Nodo Destino:",
                    options=[id for id, _ in node_options],
                    format_func=lambda x: next(label for id, label in node_options if id == x)
                )
                
                # Botón para calcular ruta
                if st.button("✈️ Calculate Route", type="primary"):
                    if selected_origin != selected_destination:
                        route_info = st.session_state.simulation.calculate_route(
                            selected_origin, selected_destination
                        )
                        
                        if route_info:
                            st.session_state.current_path = route_info['path']
                            st.session_state.current_route_info = route_info
                            st.session_state.current_origin = selected_origin
                            st.session_state.current_destination = selected_destination
                            st.rerun()
                    else:
                        st.error("El origen y destino deben ser diferentes.")
                
                # Botón Kruskal
                if st.button("🌳 Kruskal", type="secondary"):
                    st.info("Algoritmo de Kruskal ejecutado")
                
                # Mostrar información de la ruta actual
                if 'current_route_info' in st.session_state and st.session_state.current_route_info:
                    route_info = st.session_state.current_route_info
                    
                    st.text_area(
                        "Ruta Encontrada:",
                        f"Path: {route_info['path_string']} | Cost: {route_info['cost']}",
                        height=70
                    )
                    
                    # Botón para completar entrega
                    if st.button("Complete Delivery and Create Order ✅"):
                        success = st.session_state.simulation.complete_delivery(
                            route_info, 
                            st.session_state.current_origin, 
                            st.session_state.current_destination
                        )
                        if success:
                            st.session_state.current_path = None
                            st.session_state.current_route_info = None
                            st.success("✅ Entrega completada!")
                            st.rerun()

# =================== PESTAÑA 3: CLIENTS & ORDERS ===================
elif tab_selection == "🌐 Clients & Orders":
    st.header("🌐 Clientes y Órdenes")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Lista de Clientes")
            clients_data = st.session_state.simulation.get_clients_data()
            st.json(clients_data)
        
        with col2:
            st.subheader("📦 Lista de Órdenes")
            orders_data = st.session_state.simulation.get_orders_data()
            st.json(orders_data)

# =================== PESTAÑA 4: ROUTE ANALYTICS ===================
elif tab_selection == "📋 Route Analytics":
    st.header("📋 Análisis de Rutas")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Rutas Más Frecuentes")
            frequent_routes = st.session_state.simulation.get_route_analytics()
            
            if frequent_routes:
                for route, freq in frequent_routes:
                    st.text(f"{route} - Frecuencia: {freq}")
            else:
                st.info("No hay rutas registradas.")
        
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
        st.warning("⚠️ Debe inicializar la simulación primero.")
    else:
        # Obtener estadísticas de visitas
        storage_visits, charging_visits, client_visits = st.session_state.simulation.get_visit_statistics()
        
        # Solo mostrar gráficos si hay datos de visitas
        if storage_visits or charging_visits or client_visits:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Nodos Más Visitados por Tipo")
                
                # Preparar datos para el gráfico de barras
                fig_bar = st.session_state.simulation.get_visit_comparison_chart()
                if fig_bar:
                    st.pyplot(fig_bar)
                else:
                    st.info("No hay suficientes datos de visitas para mostrar el gráfico.")
            
            with col2:
                st.subheader("🥧 Proporción de Nodos por Rol")
                
                # Gráfico de torta para proporción de nodos
                fig_pie = st.session_state.simulation.get_node_proportion_chart()
                if fig_pie:
                    st.pyplot(fig_pie)
                else:
                    st.info("No hay datos de nodos para mostrar.")
        else:
            st.info("📋 No hay datos de visitas para mostrar. Complete algunas entregas primero.")
            
            # Mostrar al menos el gráfico de proporción de nodos
            st.subheader("🥧 Proporción de Nodos por Rol")
            fig_pie = st.session_state.simulation.get_node_proportion_chart()
            if fig_pie:
                st.pyplot(fig_pie)
        
        # Información textual de estadísticas
        stats = st.session_state.simulation.get_network_stats()
        if stats:
            st.subheader("📊 Resumen de la Red")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Nodos", stats['total_nodes'])
            
            with col2:
                st.metric("Total Aristas", stats['total_edges'])
            
            with col3:
                st.metric("Total Órdenes", stats['total_orders'])
            
            with col4:
                total_visits = sum(storage_visits.values()) + sum(charging_visits.values()) + sum(client_visits.values())
                st.metric("Total Visitas", total_visits)
            
            # Detalles por tipo de nodo
            st.write("**📦 Almacenamiento:** " + f"{stats['storage']['count']} nodos ({stats['storage']['percentage']:.1f}%)")
            st.write("**🔋 Recarga:** " + f"{stats['charging']['count']} nodos ({stats['charging']['percentage']:.1f}%)")
            st.write("**👤 Clientes:** " + f"{stats['client']['count']} nodos ({stats['client']['percentage']:.1f}%)")

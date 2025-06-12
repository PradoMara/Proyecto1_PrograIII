import streamlit as st
import matplotlib.pyplot as plt
from sim.simulation import Simulation
from visual.networkx_adapter import NetworkXAdapter
from visual.avl_visualizer import AVLVisualizer

# Configuración de la página
st.set_page_config(
    page_title="🚁 Drone Logistics Simulator - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498DB;
    }
    .success-message {
        background-color: #D4EDDA;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #C3E6CB;
    }
    .route-info {
        background-color: #E8F4FD;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar simulación en session_state
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()
    st.session_state.network_adapter = None
    st.session_state.last_calculated_route = None

# Header principal
st.markdown('<h1 class="main-header">🚁 Drone Logistics Simulator - Correos Chile</h1>', unsafe_allow_html=True)

# Información de proporciones de nodos
if st.session_state.simulation.simulation_active:
    node_info = st.session_state.simulation.get_node_info()
    if node_info:
        st.markdown("### Proporción de Tipos de Nodos:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h4>📦 Nodos de Almacenamiento: {node_info['storage_percent']}%</h4>
                <p>Cantidad: {node_info['storage_nodes']} nodos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h4>🔋 Nodos de Recarga: {node_info['recharge_percent']}%</h4>
                <p>Cantidad: {node_info['recharge_nodes']} nodos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h4>👤 Nodos Cliente: {node_info['client_percent']}%</h4>
                <p>Cantidad: {node_info['client_nodes']} nodos</p>
            </div>
            """, unsafe_allow_html=True)

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔄 Ejecutar Simulación", 
    "🌍 Explorar Red", 
    "🌐 Clientes y Órdenes", 
    "📊 Análisis de Rutas", 
    "📈 Estadísticas"
])

# TAB 1: Ejecutar Simulación
with tab1:
    st.header("⚙️ Inicializar Simulación")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Parámetros de Simulación")
        
        # Sliders para configuración
        n_nodes = st.slider(
            "Número de Nodos", 
            min_value=10, 
            max_value=150, 
            value=15,
            help="Cantidad total de nodos en la red (máximo 150)"
        )
        
        min_edges = n_nodes - 1
        n_edges = st.slider(
            "Número de Aristas", 
            min_value=min_edges, 
            max_value=300, 
            value=max(20, min_edges),
            help=f"Mínimo {min_edges} aristas para garantizar conectividad"
        )
        
        n_orders = st.slider(
            "Número de Órdenes", 
            min_value=1, 
            max_value=500, 
            value=10,
            help="Cantidad de órdenes de entrega a generar"
        )
        
        # Información calculada
        storage_nodes = max(1, int(n_nodes * 0.2))
        recharge_nodes = max(1, int(n_nodes * 0.2))
        client_nodes = n_nodes - storage_nodes - recharge_nodes
        
        st.info(f"""
        **Distribución Calculada:**
        - 📦 Nodos de Almacenamiento: {storage_nodes} ({storage_nodes/n_nodes*100:.1f}%)
        - 🔋 Nodos de Recarga: {recharge_nodes} ({recharge_nodes/n_nodes*100:.1f}%)
        - 👤 Nodos Cliente: {client_nodes} ({client_nodes/n_nodes*100:.1f}%)
        """)
    
    with col2:
        st.subheader("Control de Simulación")
        
        if st.button("📊 Iniciar Simulación", type="primary", use_container_width=True):
            with st.spinner("Generando red de drones..."):
                success = st.session_state.simulation.start_simulation(n_nodes, n_edges, n_orders)
                
                if success:
                    # Crear adaptador de red
                    st.session_state.network_adapter = NetworkXAdapter(
                        st.session_state.simulation.graph,
                        st.session_state.simulation.node_types
                    )
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ <strong>Simulación iniciada exitosamente!</strong><br>
                        Red generada con {n_nodes} nodos, {n_edges} aristas y {n_orders} órdenes.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                else:
                    st.error("❌ Error al inicializar la simulación")
        
        if st.session_state.simulation.simulation_active:
            st.success("✅ Simulación Activa")
        else:
            st.warning("⚠️ Simulación Inactiva")

# TAB 2: Explorar Red
with tab2:
    st.header("🌍 Explorar Red")
    
    if not st.session_state.simulation.simulation_active:
        st.warning("⚠️ Primero debe inicializar una simulación en la pestaña 'Ejecutar Simulación'")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Mostrar gráfico de red
            if st.session_state.network_adapter:
                highlight_path = st.session_state.last_calculated_route
                fig = st.session_state.network_adapter.plot_network(
                    figsize=(12, 8), 
                    highlight_path=highlight_path
                )
                st.pyplot(fig)
                plt.close()
                
                # Mostrar información de la ruta actual si existe
                if highlight_path:
                    path_names = [str(node) for node in highlight_path]
                    st.success(f"🛣️ **Ruta Actual:** {' → '.join(path_names)}")
                    
                    # Botón para limpiar la ruta
                    if st.button("🧹 Limpiar Ruta", key="clear_route_btn"):
                        st.session_state.last_calculated_route = None
                        st.rerun()
            else:
                st.info("⚠️ Genere una simulación para ver la red")
        
        with col2:
            st.subheader("Calculadora de Rutas")
            
            # Obtener opciones de nodos
            if st.session_state.network_adapter:
                node_options = st.session_state.network_adapter.get_node_options()
                node_names = [option[0] for option in node_options]
                node_labels = [option[1] for option in node_options]
                
                # Selectores de origen y destino
                origin_idx = st.selectbox(
                    "Nodo Origen:",
                    options=range(len(node_options)),
                    format_func=lambda x: node_labels[x] if x < len(node_labels) else "",
                    key="origin_select"
                )
                
                destination_idx = st.selectbox(
                    "Nodo Destino:",
                    options=range(len(node_options)),
                    format_func=lambda x: node_labels[x] if x < len(node_labels) else "",
                    key="destination_select"
                )
                
                if st.button("✈️ Calcular Ruta", type="primary", use_container_width=True):
                    if origin_idx != destination_idx:
                        origin_name = node_names[origin_idx]
                        destination_name = node_names[destination_idx]
                        
                        # Encontrar nodos originales
                        origin_vertex = None
                        destination_vertex = None
                        
                        for vertex in st.session_state.simulation.graph.vertices():
                            if str(vertex) == origin_name:
                                origin_vertex = vertex
                            elif str(vertex) == destination_name:
                                destination_vertex = vertex
                        
                        if origin_vertex and destination_vertex:
                            with st.spinner("Calculando ruta óptima..."):
                                path, cost = st.session_state.simulation.find_path_with_battery(
                                    origin_vertex, destination_vertex
                                )
                                
                                if path:
                                    # Actualizar la ruta en session_state
                                    st.session_state.last_calculated_route = path
                                    
                                    # Mostrar información de la ruta
                                    path_str = " → ".join([str(node) for node in path])
                                    
                                    st.markdown(f"""
                                    <div class="route-info">
                                        <h4>🛣️ Ruta Encontrada</h4>
                                        <p><strong>Camino:</strong> {path_str}</p>
                                        <p><strong>Costo Total:</strong> {cost} unidades</p>
                                        <p><strong>Batería Restante:</strong> {50 - cost} unidades</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.success("✅ Ruta calculada y mostrada en el gráfico")
                                    
                                else:
                                    st.error("❌ No se pudo encontrar una ruta viable (batería insuficiente)")
                    else:
                        st.warning("⚠️ El origen y destino deben ser diferentes")
                
                # Opción para completar entrega (solo si hay ruta calculada)
                if st.session_state.last_calculated_route:
                    st.divider()
                    if st.button("✅ Completar Entrega y Crear Orden", type="secondary", use_container_width=True):
                        # Obtener origen y destino de la ruta actual
                        current_route = st.session_state.last_calculated_route
                        if len(current_route) >= 2:
                            origin_vertex = current_route[0]
                            destination_vertex = current_route[-1]
                            cost = sum([
                                st.session_state.simulation.graph.get_edge(current_route[i], current_route[i+1]).element()
                                for i in range(len(current_route)-1)
                            ])
                            
                            success = st.session_state.simulation.complete_delivery(
                                origin_vertex, destination_vertex, current_route, cost
                            )
                            if success:
                                st.success("🎉 Entrega completada y orden registrada!")
                            else:
                                st.info("ℹ️ No se encontró orden pendiente para esta ruta")

# TAB 3: Clientes y Órdenes  
with tab3:
    st.header("🌐 Clientes y Órdenes")
    
    if not st.session_state.simulation.simulation_active:
        st.warning("⚠️ Primero debe inicializar una simulación")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Lista de Clientes")
            clients = st.session_state.simulation.get_clients_list()
            if clients:
                st.json(clients)
            else:
                st.info("No hay clientes registrados")
        
        with col2:
            st.subheader("📦 Lista de Órdenes")
            orders = st.session_state.simulation.get_orders_list()
            if orders:
                st.json(orders)
            else:
                st.info("No hay órdenes registradas")

# TAB 4: Análisis de Rutas
with tab4:
    st.header("📊 Análisis de Rutas")
    
    if not st.session_state.simulation.simulation_active:
        st.warning("⚠️ Primero debe inicializar una simulación")
    else:
        st.subheader("🌳 Árbol AVL - Rutas Más Frecuentes")
        
        if st.session_state.simulation.routes_avl:
            avl_viz = AVLVisualizer(st.session_state.simulation.routes_avl)
            fig = avl_viz.draw_avl_tree()
            if fig:
                st.pyplot(fig)
                plt.close()
        else:
            st.info("📈 Complete algunas entregas para ver el análisis de rutas frecuentes")

# TAB 5: Estadísticas
with tab5:
    st.header("📈 Estadísticas")
    
    if not st.session_state.simulation.simulation_active:
        st.warning("⚠️ Primero debe inicializar una simulación")
    else:
        col1, col2, col3 = st.columns(3)
        
        orders = st.session_state.simulation.get_orders_list()
        clients = st.session_state.simulation.get_clients_list()
        
        with col1:
            st.metric("Total de Clientes", len(clients))
        
        with col2:
            st.metric("Total de Órdenes", len(orders))
        
        with col3:
            completed_orders = len([o for o in orders if o['status'] == 'entregado'])
            st.metric("Órdenes Completadas", completed_orders)
        
        # Gráfico de estados de órdenes
        if orders:
            status_counts = {}
            for order in orders:
                status = order['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if len(status_counts) > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
                ax.set_title("Distribución de Estados de Órdenes")
                st.pyplot(fig)
                plt.close()

# Información en sidebar
with st.sidebar:
    st.header("🔧 Información del Sistema")
    
    st.markdown("""
    ### Parámetros del Dron
    - 🔋 **Autonomía Máxima:** 50 unidades
    - 🛣️ **Algoritmo de Ruta:** BFS Modificado
    - ⚡ **Recarga Automática:** Habilitada
    
    ### Tipos de Nodos
    - 📦 **Almacenamiento:** 20%
    - 🔋 **Recarga:** 20% 
    - 👤 **Cliente:** 60%
    """)
    
    if st.session_state.simulation.simulation_active:
        st.success("✅ Sistema Operativo")
    else:
        st.error("❌ Sistema Inactivo")

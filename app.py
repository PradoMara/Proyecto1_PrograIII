import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_folium import st_folium
from utils.simulation import DroneSimulation
from utils.api_integration import save_simulation_to_api, auto_sync_simulation

def is_simulation_active():
    """Verifica si la simulación está activa leyendo el archivo JSON"""
    try:
        if os.path.exists("simulation_state.json"):
            with open("simulation_state.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('is_active', False)
        return False
    except:
        return False

def stop_simulation():
    """Detiene la simulación cambiando is_active a False en el JSON"""
    try:
        if os.path.exists("simulation_state.json"):
            with open("simulation_state.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['is_active'] = False
            data['last_updated'] = datetime.now().isoformat()
            data['finished_at'] = datetime.now().isoformat()
            
            with open("simulation_state.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
    except Exception as e:
        st.error(f"Error al detener simulación: {str(e)}")
        return False

# Configuración de la página
st.set_page_config(
    page_title="Simulación Drones - Correos Chile",
    page_icon="🚁",
    layout="wide"
)

# Inicializar simulación en session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = DroneSimulation()

# Inicializar variables de estado para Kruskal
if 'show_kruskal' not in st.session_state:
    st.session_state.show_kruskal = False
if 'mst_data' not in st.session_state:
    st.session_state.mst_data = None

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
    
    # Botón para finalizar simulación (solo visible si está activa)
    if is_simulation_active():
        st.write("---")
        st.info("🔄 **Simulación Activa** - La simulación está corriendo actualmente")
        
        if st.button("🛑 Fin Simulación", type="secondary"):
            with st.spinner("Finalizando simulación..."):
                if stop_simulation():
                    st.success("✅ Simulación finalizada exitosamente!")
                    st.info("📡 Estado actualizado en el archivo de simulación")
                    # Rerun para actualizar la UI
                    st.rerun()
                else:
                    st.error("❌ Error al finalizar la simulación")

# =================== PESTAÑA 2: EXPLORE NETWORK ===================
elif tab_selection == "🌍 Explore Network":
    st.header("🌍 Exploración de la Red")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Mapa de Temuco")
            
            # Mostrar mapa de Folium directamente
            if 'current_path' not in st.session_state:
                st.session_state.current_path = None
            
            # Decidir qué mapa mostrar según el estado
            if st.session_state.show_kruskal and st.session_state.mst_data:
                # Mostrar mapa con MST
                folium_map = st.session_state.simulation.get_folium_map_with_mst(st.session_state.mst_data)
                if folium_map:
                    st_folium(folium_map, width=900, height=650)
                else:
                    st.error("Error al generar el mapa MST.")
            else:
                # Mostrar mapa normal
                folium_map = st.session_state.simulation.get_folium_map(st.session_state.current_path)
                if folium_map:
                    st_folium(folium_map, width=900, height=650)
                else:
                    st.error("Error al generar el mapa.")
        
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
                
                # Botones para Kruskal
                col_kr1, col_kr2 = st.columns(2)
                
                with col_kr1:
                    if st.button("🌳 Mostrar Kruskal MST", type="secondary"):
                        mst_data = st.session_state.simulation.execute_kruskal()
                        if mst_data:
                            st.session_state.show_kruskal = True
                            st.session_state.mst_data = mst_data
                            st.session_state.current_path = None  # Limpiar ruta actual
                            st.success(f"MST calculado: {len(mst_data['mst_edges'])} aristas, peso total: {mst_data['total_weight']:.2f}")
                            st.rerun()
                
                with col_kr2:
                    if st.button("🔄 Vista Normal", type="secondary"):
                        st.session_state.show_kruskal = False
                        st.session_state.mst_data = None
                        st.rerun()
                
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
                            # Sincronizar con API automáticamente
                            auto_sync_simulation(st.session_state.simulation)
                            st.session_state.current_path = None
                            st.session_state.current_route_info = None
                            st.success("✅ Entrega completada y sincronizada con API!")
                            st.rerun()

# =================== PESTAÑA 3: CLIENTS & ORDERS ===================
elif tab_selection == "🌐 Clients & Orders":
    st.header("🌐 Clientes y Órdenes")
    
    if not st.session_state.simulation.is_initialized:
        st.warning("⚠️ Debe inicializar la simulación primero.")
    else:
        # Información sobre sincronización con API
        st.info("💡 **Datos en Tiempo Real**: Esta información se sincroniza automáticamente con la API. Use los botones 'Recargar' para ver cambios de estado.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Header con botón de recargar para clientes
            subcol1, subcol2 = st.columns([3, 1])
            with subcol1:
                st.subheader("👥 Lista de Clientes")
            with subcol2:
                if st.button("🔄 Recargar", key="reload_clients", type="secondary"):
                    st.rerun()
            
            # Leer datos actualizados del JSON
            if os.path.exists("simulation_state.json"):
                try:
                    with open("simulation_state.json", 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    clients_data = data.get('clients', [])
                    
                    # Mostrar en formato tabla más legible
                    if clients_data:
                        clients_df = pd.DataFrame(clients_data)
                        st.dataframe(clients_df, use_container_width=True)
                        st.caption(f"📊 Total: {len(clients_data)} clientes")
                    else:
                        st.info("No hay clientes disponibles")
                except Exception as e:
                    st.error(f"Error al cargar clientes: {str(e)}")
                    # Fallback a datos de simulación
                    clients_data = st.session_state.simulation.get_clients_data()
                    st.json(clients_data)
            else:
                # Fallback a datos de simulación
                clients_data = st.session_state.simulation.get_clients_data()
                st.json(clients_data)
        
        with col2:
            # Header con botón de recargar para órdenes
            subcol1, subcol2 = st.columns([3, 1])
            with subcol1:
                st.subheader("📦 Lista de Órdenes")
            with subcol2:
                if st.button("🔄 Recargar", key="reload_orders", type="secondary"):
                    st.rerun()
            
            # Leer datos actualizados del JSON
            if os.path.exists("simulation_state.json"):
                try:
                    with open("simulation_state.json", 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    orders_data = data.get('orders', [])
                    
                    # Mostrar en formato tabla más legible
                    if orders_data:
                        orders_df = pd.DataFrame(orders_data)
                        
                        # Aplicar colores por estado
                        def color_status(val):
                            if val == 'Entregado':
                                return 'background-color: #d4edda; color: #155724'
                            elif val == 'Cancelado':
                                return 'background-color: #f8d7da; color: #721c24'
                            elif val == 'En Progreso':
                                return 'background-color: #fff3cd; color: #856404'
                            else:  # Pendiente
                                return 'background-color: #cce5ff; color: #004085'
                        
                        # Mostrar tabla con estilos
                        styled_df = orders_df.style.applymap(color_status, subset=['Status'])
                        st.dataframe(styled_df, use_container_width=True)
                        
                        # Estadísticas de órdenes
                        status_counts = orders_df['Status'].value_counts()
                        st.caption(f"📊 Total: {len(orders_data)} órdenes")
                        
                        # Mostrar conteo por estado
                        status_cols = st.columns(len(status_counts))
                        for i, (status, count) in enumerate(status_counts.items()):
                            with status_cols[i]:
                                if status == 'Entregado':
                                    st.success(f"✅ {status}: {count}")
                                elif status == 'Cancelado':
                                    st.error(f"❌ {status}: {count}")
                                elif status == 'En Progreso':
                                    st.warning(f"⏳ {status}: {count}")
                                else:
                                    st.info(f"⏸️ {status}: {count}")
                    else:
                        st.info("No hay órdenes disponibles")
                except Exception as e:
                    st.error(f"Error al cargar órdenes: {str(e)}")
                    # Fallback a datos de simulación
                    orders_data = st.session_state.simulation.get_orders_data()
                    st.json(orders_data)
            else:
                # Fallback a datos de simulación
                orders_data = st.session_state.simulation.get_orders_data()
                st.json(orders_data)
        
        # Sección de información sobre la API
        st.markdown("---")
        st.subheader("🔗 Integración con API")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.info("""
            **💻 Endpoints API Disponibles:**
            - `GET /clientes/` - Lista clientes
            - `GET /ordenes/` - Lista órdenes
            - `POST /ordenes/{id}/cancelar` - Cancelar orden
            - `POST /ordenes/{id}/completar` - Completar orden
            """)
        
        with col4:
            st.success("""
            **✅ Estados de Órdenes:**
            - 🔵 **Pendiente** - Orden creada
            - 🟡 **En Progreso** - Siendo procesada
            - 🟢 **Entregado** - Completada exitosamente
            - 🔴 **Cancelado** - Orden cancelada
            """)
        
        with col5:
            st.warning("""
            **⚡ Cambios en Tiempo Real:**
            - Los cambios desde la API se reflejan aquí
            - Use 'Recargar' para ver actualizaciones
            - Los datos se sincronizan automáticamente
            """)

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
        
        # Sección para generar reporte PDF
        st.markdown("---")
        st.subheader("📄 Generación de Reportes")
        
        col3, col4, col5 = st.columns([1, 1, 2])
        
        with col3:
            if st.button("📊 Generate PDF Report", type="primary"):
                with st.spinner("Generando reporte PDF..."):
                    try:
                        # Sincronizar datos antes de generar reporte
                        auto_sync_simulation(st.session_state.simulation)
                        
                        # Importar la utilidad de PDF
                        from utils.pdf_report import generate_pdf_report
                        
                        # Preparar datos para el reporte
                        simulation_data = {
                            'clients': st.session_state.simulation.get_clients_data(),
                            'orders': st.session_state.simulation.get_orders_data(),
                            'visit_statistics': {
                                'clients': [],
                                'recharges': [],
                                'storages': []
                            },
                            'summary': {
                                'network_stats': st.session_state.simulation.get_network_stats()
                            }
                        }
                        
                        # Obtener estadísticas de visitas
                        storage_visits, charging_visits, client_visits = st.session_state.simulation.get_visit_statistics()
                        
                        # Formatear estadísticas de visitas
                        simulation_data['visit_statistics'] = {
                            'clients': [
                                {'name': name, 'visits': visits}
                                for name, visits in sorted(client_visits.items(), key=lambda x: x[1], reverse=True)
                            ],
                            'recharges': [
                                {'name': name, 'visits': visits}
                                for name, visits in sorted(charging_visits.items(), key=lambda x: x[1], reverse=True)
                            ],
                            'storages': [
                                {'name': name, 'visits': visits}
                                for name, visits in sorted(storage_visits.items(), key=lambda x: x[1], reverse=True)
                            ]
                        }
                        
                        # Generar PDF
                        pdf_buffer = generate_pdf_report(simulation_data)
                        
                        # Botón de descarga
                        st.success("✅ Reporte PDF generado exitosamente!")
                        st.download_button(
                            label="📥 Descargar Reporte PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"reporte_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        
                    except Exception as e:
                        st.error(f"Error al generar el reporte PDF: {str(e)}")
        
        with col4:
            if st.button("🔄 Sync with API", type="secondary"):
                with st.spinner("Sincronizando datos con API..."):
                    try:
                        success = auto_sync_simulation(st.session_state.simulation)
                        if success:
                            st.success("✅ Datos sincronizados con API exitosamente!")
                        else:
                            st.error("❌ Error al sincronizar datos con API")
                    except Exception as e:
                        st.error(f"Error en la sincronización: {str(e)}")
        
        with col5:
            st.info("""
            **📋 Contenido del Reporte PDF:**
            - 📊 Tabla completa de clientes con ID, nombre, tipo y total de órdenes
            - 📦 Datos de órdenes en formato JSON (como respuesta de API)
            - 🥧 Gráfico de distribución de nodos por tipo (pastel)
            - 📈 Gráficos de barras de nodos más visitados por categoría:
              - 👤 Clientes más visitados
              - 🔋 Estaciones de recarga más visitadas  
              - 📦 Nodos de almacenamiento más visitados
            """)
            
            st.info("🔄 **Sincronización**: Los datos se sincronizan automáticamente al completar entregas. Usa el botón 'Sync with API' para forzar actualización manual.")

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

import streamlit as st
import matplotlib.pyplot as plt
from models.node import NodeType

class Dashboard:
    """Dashboard principal para mostrar estadísticas y métricas"""
    
    def __init__(self, simulation):
        self.simulation = simulation
    
    def show_network_stats(self):
        """Muestra estadísticas básicas de la red"""
        if not self.simulation.is_initialized:
            st.warning("Debe inicializar la simulación primero.")
            return
        
        stats = self.simulation.get_network_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Nodos", stats['total_nodes'])
            st.metric("📦 Almacenamiento", stats['storage']['count'])
        
        with col2:
            st.metric("Total Aristas", stats['total_edges'])
            st.metric("🔋 Recarga", stats['charging']['count'])
        
        with col3:
            st.metric("Total Órdenes", stats['total_orders'])
            st.metric("👤 Clientes", stats['client']['count'])
    
    def show_visit_charts(self):
        """Muestra gráficos de visitas por tipo de nodo"""
        storage_visits, charging_visits, client_visits = self.simulation.get_visit_statistics()
        
        if not any([storage_visits, charging_visits, client_visits]):
            st.info("No hay datos de visitas para mostrar.")
            return
        
        # Preparar datos para el gráfico
        all_visits = {}
        all_visits.update(storage_visits)
        all_visits.update(charging_visits)
        all_visits.update(client_visits)
        
        if all_visits:
            # Mostrar top 10 más visitados
            sorted_visits = sorted(all_visits.items(), key=lambda x: x[1], reverse=True)[:10]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            nodes, visits = zip(*sorted_visits)
            
            colors = []
            for node in nodes:
                if "📦" in node:
                    colors.append('#FF6B6B')
                elif "🔋" in node:
                    colors.append('#4ECDC4')
                else:
                    colors.append('#45B7D1')
            
            ax.bar(range(len(nodes)), visits, color=colors)
            ax.set_xlabel('Nodos')
            ax.set_ylabel('Número de Visitas')
            ax.set_title('Top 10 Nodos Más Visitados')
            ax.set_xticks(range(len(nodes)))
            ax.set_xticklabels(nodes, rotation=45, ha='right')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    def show_route_summary(self):
        """Muestra resumen de rutas más frecuentes"""
        frequent_routes = self.simulation.get_route_analytics()
        
        if not frequent_routes:
            st.info("No hay rutas registradas.")
            return
        
        st.subheader("🔄 Rutas Más Utilizadas")
        
        for i, (route, freq) in enumerate(frequent_routes[:5], 1):
            st.text(f"{i}. {route} - Frecuencia: {freq}")
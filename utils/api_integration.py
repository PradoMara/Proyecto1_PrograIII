"""
Módulo de integración entre la simulación de Streamlit y la API
"""
import json
import os
from datetime import datetime
from typing import Optional

def save_simulation_to_api(simulation_instance):
    """Guarda los datos de la simulación para que la API pueda accederlos"""
    try:
        if not simulation_instance or not simulation_instance.is_initialized:
            return False
        
        # Usar archivo tanto en directorio actual como en api/
        simulation_files = ["simulation_state.json", "api/simulation_state.json"]
        
        # Obtener datos de la simulación
        clients_data = simulation_instance.get_clients_data()
        orders_data = simulation_instance.get_orders_data()
        storage_visits, charging_visits, client_visits = simulation_instance.get_visit_statistics()
        network_stats = simulation_instance.get_network_stats()
        
        # Formatear estadísticas de visitas para la API
        visit_statistics = {
            "clients": [
                {"name": name, "visits": visits}
                for name, visits in sorted(client_visits.items(), key=lambda x: x[1], reverse=True)
            ],
            "recharges": [
                {"name": name, "visits": visits}
                for name, visits in sorted(charging_visits.items(), key=lambda x: x[1], reverse=True)
            ],
            "storages": [
                {"name": name, "visits": visits}
                for name, visits in sorted(storage_visits.items(), key=lambda x: x[1], reverse=True)
            ]
        }
        
        # Crear estructura de datos
        simulation_data = {
            "is_active": True,
            "initialized_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "config": {
                "total_nodes": len(simulation_instance.graph.nodes) if simulation_instance.graph else 0,
                "total_edges": len(simulation_instance.graph.edges) if simulation_instance.graph else 0,
                "total_orders": len(orders_data),
                "total_clients": len(clients_data)
            },
            "clients": clients_data,
            "orders": orders_data,
            "visit_statistics": visit_statistics,
            "summary": {
                "network_stats": network_stats,
                "total_visits": sum(client_visits.values()) + sum(charging_visits.values()) + sum(storage_visits.values()),
                "most_visited_client": max(client_visits.items(), key=lambda x: x[1])[0] if client_visits else "N/A",
                "most_visited_charging": max(charging_visits.items(), key=lambda x: x[1])[0] if charging_visits else "N/A",
                "most_visited_storage": max(storage_visits.items(), key=lambda x: x[1])[0] if storage_visits else "N/A",
                "simulation_active": True
            }
        }
        
        # Guardar en múltiples archivos para asegurar sincronización
        for file_path in simulation_files:
            try:
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(simulation_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error al guardar en {file_path}: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error al guardar datos de simulación: {e}")
        return False

def clear_simulation_data():
    """Limpia los datos de la simulación cuando se cierra"""
    try:
        simulation_data_file = "simulation_state.json"
        if os.path.exists(simulation_data_file):
            # En lugar de eliminar, marcar como inactiva
            with open(simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data["is_active"] = False
            data["deactivated_at"] = datetime.now().isoformat()
            
            with open(simulation_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error al limpiar datos de simulación: {e}")
        return False

def update_simulation_data(simulation_instance):
    """Actualiza los datos de la simulación (para llamar periódicamente)"""
    return save_simulation_to_api(simulation_instance)

def auto_sync_simulation(simulation_instance):
    """Función para sincronización automática cada vez que se modifica la simulación"""
    if simulation_instance and simulation_instance.is_initialized:
        return save_simulation_to_api(simulation_instance)
    return False

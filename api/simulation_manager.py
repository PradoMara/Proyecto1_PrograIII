"""
Módulo para acceder a los datos de la simulación desde la API
"""
import os
import json
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from utils.simulation import DroneSimulation

class SimulationDataManager:
    """Gestor de datos de la simulación para uso en la API"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Usar el archivo del directorio raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.simulation_data_file = os.path.join(project_root, "simulation_state.json")
        self.simulation = None
        self._initialized = True
    
    def is_simulation_running(self) -> bool:
        """Verifica si la simulación está activa"""
        try:
            # Verificar si existe archivo de estado de simulación
            if os.path.exists(self.simulation_data_file):
                with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('is_active', False)
            return False
        except:
            return False
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """Obtiene el estado general de la simulación"""
        if not self.is_simulation_running():
            return {
                "status": "inactive",
                "message": "Simulación no iniciada",
                "is_active": False
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "status": "active",
                    "message": "Simulación activa",
                    "is_active": True,
                    "initialized_at": data.get('initialized_at'),
                    "config": data.get('config', {})
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error al leer estado de simulación: {str(e)}",
                "is_active": False
            }
    
    def get_clients_data(self) -> Dict[str, Any]:
        """Obtiene datos de clientes desde la simulación"""
        if not self.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": []
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                clients = data.get('clients', [])
                return {
                    "status": "success",
                    "message": "Datos de clientes obtenidos exitosamente",
                    "data": clients
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al obtener clientes: {str(e)}",
                "data": []
            }
    
    def get_client_by_id(self, client_id: str) -> Dict[str, Any]:
        """Obtiene un cliente específico por ID"""
        clients_data = self.get_clients_data()
        
        if clients_data["status"] != "success":
            return clients_data
        
        # Buscar por ID (puede ser string hasheado o numérico)
        for client in clients_data["data"]:
            # Manejar tanto IDs string como numéricos
            client_stored_id = client.get("ID")
            if str(client_stored_id) == str(client_id):
                return {
                    "status": "success",
                    "message": "Cliente encontrado",
                    "data": client
                }
        
        return {
            "status": "error",
            "message": f"Cliente con ID {client_id} no encontrado",
            "data": None
        }
    
    def get_orders_data(self) -> Dict[str, Any]:
        """Obtiene datos de órdenes desde la simulación"""
        if not self.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": []
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                orders = data.get('orders', [])
                return {
                    "status": "success",
                    "message": "Datos de órdenes obtenidos exitosamente",
                    "data": orders
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al obtener órdenes: {str(e)}",
                "data": []
            }
    
    def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """Obtiene una orden específica por ID"""
        orders_data = self.get_orders_data()
        
        if orders_data["status"] != "success":
            return orders_data
        
        # Buscar por ID (puede ser string hasheado o numérico)
        for order in orders_data["data"]:
            # Manejar tanto IDs string como numéricos
            order_stored_id = order.get("ID")
            if str(order_stored_id) == str(order_id):
                return {
                    "status": "success",
                    "message": "Orden encontrada",
                    "data": order
                }
        
        return {
            "status": "error",
            "message": f"Orden con ID {order_id} no encontrada",
            "data": None
        }
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancela una orden específica"""
        if not self.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "success": False
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            orders = data.get('orders', [])
            for order in orders:
                # Manejar tanto IDs string como numéricos
                order_stored_id = order.get("ID")
                if str(order_stored_id) == str(order_id):
                    if order.get("Status") in ["Pendiente", "En Progreso"]:
                        order["Status"] = "Cancelado"
                        order["Fecha Cancelacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Guardar cambios
                        with open(self.simulation_data_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        return {
                            "status": "success",
                            "message": f"Orden {order_id} cancelada exitosamente",
                            "success": True,
                            "data": order
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"La orden {order_id} no puede ser cancelada (estado: {order.get('Status')})",
                            "success": False
                        }
            
            return {
                "status": "error",
                "message": f"Orden {order_id} no encontrada",
                "success": False
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al cancelar orden: {str(e)}",
                "success": False
            }
    
    def complete_order(self, order_id: str) -> Dict[str, Any]:
        """Marca una orden como completada"""
        if not self.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "success": False
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            orders = data.get('orders', [])
            for order in orders:
                # Manejar tanto IDs string como numéricos
                order_stored_id = order.get("ID")
                if str(order_stored_id) == str(order_id):
                    if order.get("Status") in ["Pendiente", "En Progreso"]:
                        order["Status"] = "Entregado"
                        order["Fecha Entrega"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Guardar cambios
                        with open(self.simulation_data_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        return {
                            "status": "success",
                            "message": f"Orden {order_id} completada exitosamente",
                            "success": True,
                            "data": order
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"La orden {order_id} no puede ser completada (estado: {order.get('Status')})",
                            "success": False
                        }
            
            return {
                "status": "error",
                "message": f"Orden {order_id} no encontrada",
                "success": False
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al completar orden: {str(e)}",
                "success": False
            }
    
    def get_visit_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de visitas desde la simulación"""
        if not self.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": {
                    "clients": [],
                    "recharges": [],
                    "storages": []
                }
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                visits = data.get('visit_statistics', {})
                
                return {
                    "status": "success",
                    "message": "Estadísticas de visitas obtenidas exitosamente",
                    "data": visits
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al obtener estadísticas: {str(e)}",
                "data": {
                    "clients": [],
                    "recharges": [],
                    "storages": []
                }
            }
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Obtiene resumen general de la simulación"""
        if not self.is_simulation_running():
            return {
                "status": "error",
                "message": "Simulación no iniciada",
                "data": {}
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                summary = data.get('summary', {})
                return {
                    "status": "success",
                    "message": "Resumen de simulación obtenido exitosamente",
                    "data": summary
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error al obtener resumen: {str(e)}",
                "data": {}
            }

    def stop_simulation(self) -> Dict[str, Any]:
        """Detiene la simulación cambiando is_active a False"""
        if not os.path.exists(self.simulation_data_file):
            return {
                "status": "error",
                "message": "Archivo de simulación no encontrado",
                "success": False
            }
        
        try:
            with open(self.simulation_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cambiar is_active a False
            data['is_active'] = False
            data['last_updated'] = datetime.now().isoformat()
            data['finished_at'] = datetime.now().isoformat()
            
            # Guardar cambios
            with open(self.simulation_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": "Simulación finalizada exitosamente",
                "success": True,
                "data": {
                    "is_active": False,
                    "finished_at": data['finished_at']
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al finalizar simulación: {str(e)}",
                "success": False
            }

# Instancia global del gestor
simulation_manager = SimulationDataManager()

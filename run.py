#!/usr/bin/env python3
"""
Script para ejecutar automáticamente la aplicación Streamlit
Uso: python run.py
"""

import subprocess
import sys
import os
import socket

def find_free_port(start_port=8501, max_port=8510):
    """Encuentra un puerto libre comenzando desde start_port"""
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Función principal para ejecutar la aplicación"""
    # Obtener la ruta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(current_dir, "app.py")
    
    print("🚁 Iniciando Simulación Logística de Drones - Correos Chile...")
    
    # Buscar un puerto libre
    port = find_free_port()
    if not port:
        print("❌ Error: No se pudo encontrar un puerto libre (8501-8510)")
        return 1
    
    print(f"📍 Ejecutando aplicación Streamlit en puerto {port}...")
    print(f"🌐 La aplicación estará disponible en: http://localhost:{port}")
    
    try:
        # Ejecutar streamlit run con app.py
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.address", "localhost",
            "--server.port", str(port),
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar Streamlit: {e}")
        print("💡 Asegúrate de que Streamlit esté instalado: pip install streamlit")
        return 1
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por el usuario.")
        return 0
        
    except FileNotFoundError:
        print("❌ Error: No se pudo encontrar Python o Streamlit.")
        print("💡 Verifica que Python y Streamlit estén instalados correctamente.")
        return 1
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

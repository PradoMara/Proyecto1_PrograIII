#!/usr/bin/env python3
"""
Script para ejecutar automáticamente la aplicación Streamlit y la API
Uso: python run.py
"""

import subprocess
import sys
import os
import socket
import threading
import time

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

def run_streamlit(port):
    """Ejecuta la aplicación Streamlit en un hilo separado"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(current_dir, "app.py")
    
    try:
        print(f"🌐 Streamlit iniciado en http://localhost:{port}")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.address", "localhost",
            "--server.port", str(port),
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en Streamlit: {e}")
        print("💡 Verifica que Streamlit esté instalado: pip install streamlit")
    except Exception as e:
        print(f"❌ Error inesperado en Streamlit: {e}")

def run_api():
    """Ejecuta la API en un hilo separado"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    api_file = os.path.join(current_dir, "api", "run_api.py")
    
    try:
        # Esperar un poco para que Streamlit se inicie primero
        print("⏳ Esperando que Streamlit se inicie...")
        time.sleep(3)
        print("🚀 Iniciando API...")
        subprocess.run([sys.executable, api_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en API: {e}")
        print("💡 Verifica que FastAPI esté instalado: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Error inesperado en API: {e}")

def check_files():
    """Verifica que todos los archivos necesarios existan"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        "app.py",
        "api/run_api.py",
        "api/main.py",
        "utils/simulation.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Todos los archivos necesarios están presentes")
    return True

def main():
    """Función principal para ejecutar la aplicación"""
    print("🚁 Iniciando Simulación Logística de Drones - Correos Chile...")
    print("� Iniciando Streamlit y API en paralelo...")
    
    # Verificar archivos necesarios
    if not check_files():
        print("❌ Error: Faltan archivos necesarios para ejecutar la aplicación.")
        return 1
    
    # Buscar un puerto libre para Streamlit
    port = find_free_port()
    if not port:
        print("❌ Error: No se pudo encontrar un puerto libre (8501-8510)")
        return 1
    
    print(f"📍 Streamlit se ejecutará en: http://localhost:{port}")
    print(f"📡 API se ejecutará en: http://localhost:8000")
    print(f"📚 Documentación API: http://localhost:8000/docs")
    print("🛑 Para detener ambos servicios: Ctrl+C")
    print("-" * 60)
    
    try:
        # Crear hilos para ejecutar Streamlit y API en paralelo
        streamlit_thread = threading.Thread(target=run_streamlit, args=(port,), daemon=True)
        api_thread = threading.Thread(target=run_api, daemon=True)
        
        # Iniciar ambos hilos
        print("🚀 Iniciando Streamlit...")
        streamlit_thread.start()
        
        print("🚀 Iniciando API (esperando 3 segundos)...")
        api_thread.start()
        
        # Mantener el proceso principal activo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servicios...")
            return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar los servicios: {e}")
        print("💡 Asegúrate de que Streamlit y FastAPI estén instalados")
        return 1
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación cerrada por el usuario.")
        return 0
        
    except FileNotFoundError:
        print("❌ Error: No se pudo encontrar Python, Streamlit o los archivos necesarios.")
        print("💡 Verifica que Python, Streamlit y FastAPI estén instalados correctamente.")
        return 1
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

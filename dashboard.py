#!/usr/bin/env python3
"""
Drone Logistics Simulator - Correos Chile
Simulador de logística autónoma para drones

Para ejecutar: python dashboard.py
"""

import sys
import os
import subprocess

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Función principal que ejecuta la aplicación Streamlit"""
    try:
        # Verificar si streamlit está instalado
        import streamlit
        
        # Obtener la ruta del archivo dashboard real
        dashboard_path = os.path.join(project_root, "visual", "dashboard.py")
        
        # Ejecutar streamlit con el archivo dashboard
        cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.headless", "false"]
        
        print("🚁 Iniciando Drone Logistics Simulator - Correos Chile...")
        print("📡 La aplicación se abrirá en su navegador web...")
        print("🔗 URL: http://localhost:8501")
        print("⚠️  Para detener la aplicación presione Ctrl+C")
        print("-" * 60)
        
        # Ejecutar el comando
        subprocess.run(cmd)
        
    except ImportError:
        print("❌ Error: Streamlit no está instalado.")
        print("💡 Instale las dependencias ejecutando: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

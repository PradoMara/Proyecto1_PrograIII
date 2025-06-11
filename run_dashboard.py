#!/usr/bin/env python3
"""
Script de lanzamiento para el Dashboard de Streamlit

Ejecuta la interfaz web del Sistema de Grafos Conectados
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Función principal para lanzar el dashboard"""
    
    # Obtener el directorio del proyecto
    proyecto_dir = Path(__file__).parent
    
    # Cambiar al directorio del proyecto
    os.chdir(proyecto_dir)
    
    # Ruta al archivo del dashboard
    dashboard_path = proyecto_dir / "visual" / "dashboard.py"
    
    if not dashboard_path.exists():
        print("❌ Error: No se encontró el archivo dashboard.py")
        print(f"Buscado en: {dashboard_path}")
        return 1
    
    print("🚀 Iniciando Dashboard del Sistema de Grafos Conectados...")
    print(f"📁 Directorio del proyecto: {proyecto_dir}")
    print(f"🌐 El dashboard se abrirá en tu navegador web")
    print("=" * 50)
    
    try:
        # Ejecutar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--theme.base", "light",
            "--theme.primaryColor", "#4ECDC4",
            "--theme.backgroundColor", "#FFFFFF",
            "--theme.secondaryBackgroundColor", "#F0F2F6",
            "--theme.textColor", "#262730"
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Dashboard detenido por el usuario")
        return 0
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
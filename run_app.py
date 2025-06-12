#!/usr/bin/env python3
"""
Drone Logistics Simulator - Correos Chile
Ejecutor directo con Streamlit integrado

Para ejecutar: python run_app.py
"""

import sys
import os

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Ejecuta la aplicación directamente importando y ejecutando streamlit"""
    try:
        # Cambiar el directorio de trabajo
        os.chdir(project_root)
        
        # Configurar argumentos de streamlit
        sys.argv = [
            "streamlit", 
            "run", 
            "visual/dashboard.py",
            "--server.headless=false",
            "--server.port=8501",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        print("🚁 Iniciando Drone Logistics Simulator - Correos Chile...")
        print("📡 La aplicación se está cargando...")
        print("🔗 Se abrirá automáticamente en: http://localhost:8501")
        print("⚠️  Para detener presione Ctrl+C en esta terminal")
        print("-" * 60)
        
        # Importar y ejecutar streamlit
        from streamlit.web import cli as stcli
        stcli.main()
        
    except ImportError as e:
        print("❌ Error de importación:", e)
        print("💡 Asegúrese de tener streamlit instalado: pip install streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

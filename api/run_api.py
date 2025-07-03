import uvicorn
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Función principal para ejecutar la API"""
    try:
        print("🚀 Iniciando API de Drones...")
        print("📍 URL: http://localhost:8000")
        print("📚 Documentación: http://localhost:8000/docs")
        print("🔄 Documentación alternativa: http://localhost:8000/redoc")
        print("💚 Health check: http://localhost:8000/health")
        print("ℹ️  Información: http://localhost:8000/info")
        print("🛑 Para detener: Ctrl+C")
        print("-" * 60)
        
        # Cambiar el directorio de trabajo al directorio raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Recarga automática en desarrollo
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 API detenida por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar la API: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

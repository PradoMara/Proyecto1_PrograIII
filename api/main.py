"""
API principal para el sistema de gestión de rutas de drones
"""
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers con imports absolutos
from api.routers import clients, orders, reports, info, routes, graph, drones, charging_stations
from api.config import settings

# Crear instancia de FastAPI
app = FastAPI(
    title="Proyecto Drones API",
    description="API para gestión de rutas de drones con limitaciones de batería",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(reports.router)
app.include_router(info.router)
app.include_router(routes.router)
app.include_router(graph.router)
app.include_router(drones.router)
app.include_router(charging_stations.router)

# Ruta de bienvenida
@app.get("/")
async def root():
    return {
        "message": "¡API de Drones funcionando correctamente!",
        "version": "1.0.0",
        "status": "active",
        "documentation": "/docs"
    }

# Ruta de health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "drones-api",
        "version": "1.0.0"
    }

# Ruta de información de la API
@app.get("/info")
async def api_info():
    return {
        "api_name": "Drones Route Management API",
        "description": "API para gestión de rutas de drones con BFS modificado",
        "features": [
            "Generación de grafos conectados",
            "Gestión de drones y batería",
            "Búsqueda de rutas con limitaciones energéticas",
            "Estaciones de recarga",
            "Almacenamiento AVL de rutas"
        ],
        "endpoints": {
            "documentation": "/docs",
            "alternative_docs": "/redoc",
            "health": "/health",
            "info": "/info",
            "drones": "/drones",
            "routes": "/routes",
            "charging_stations": "/charging-stations",
            "graph": "/graph"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

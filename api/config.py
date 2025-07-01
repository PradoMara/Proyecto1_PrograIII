
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Configuración de la aplicación
    app_name: str = "Drones API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Configuración de CORS
    cors_origins: List[str] = ["*"]
    
    # Configuración de logging
    log_level: str = "info"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia global de configuración
settings = Settings()

import os
from fastapi.middleware.cors import CORSMiddleware

# URL USUARIOS API
USUARIOS_API_BASE_URL = os.getenv(
    "USUARIOS_API_BASE_URL",
    "http://localhost:3000/api/usuarios"
)
USUARIOS_API_TOKEN = os.getenv("USUARIOS_API_TOKEN", "")  

# --- CAMBIO AQUÍ ---
# Antes tenías: MS_USUARIOS_BASE_URL = "http://localhost:3000"
# Ahora ponemos esto para que lea la variable de Docker:
MS_USUARIOS_BASE_URL = os.getenv(
    "MS_USUARIOS_BASE_URL", 
    "http://localhost:3000"
)
# -------------------

CONTENIDO_API_BASE_URL = os.getenv(
    "MS_CONTENIDO_BASE_URL", 
    "http://localhost:8083/api"
)

COMUNIDAD_API_BASE_URL = os.getenv(
    "MS_COMUNIDAD_BASE_URL",
    "http://localhost:8084"
)

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
import os
from fastapi.middleware.cors import CORSMiddleware

# URLs de otros microservicios por ENV
MS_USUARIOS_BASE_URL = os.getenv("MS_USUARIOS_BASE_URL", "http://localhost:8001")
MS_CONTENIDO_BASE_URL = os.getenv("MS_CONTENIDO_BASE_URL", "http://localhost:8002")
MS_COMUNIDAD_BASE_URL = os.getenv("MS_COMUNIDAD_BASE_URL", "http://localhost:8003")

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

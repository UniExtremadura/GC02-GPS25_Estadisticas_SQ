from fastapi import FastAPI
from controller.config import setup_cors
from view.view import router as estadisticas_router

app = FastAPI(title="Microservicio Estadísticas")
setup_cors(app)
app.include_router(estadisticas_router)

@app.get("/")
def root():
    return {"message": "Microservicio de Estadísticas activo ✅"}

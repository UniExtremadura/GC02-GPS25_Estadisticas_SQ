from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

# Importaciones de tu backend
from backend.controller.endpoints import router as estadisticas_router
from backend.controller.endpoints import model  # Importar el modelo

# --- 1. DEFINICIÓN DEL SCHEDULER Y FUNCIONES ---
scheduler = BackgroundScheduler()

def actualizar_mensualmente():
    print("🔄 Actualizando oyentes mensuales...", flush=True)
    try:
        model.sync_todos_los_artistas()
        print("✅ Actualización mensual completada", flush=True)
    except Exception as e:
        print(f"❌ Error actualización mensual: {str(e)}", flush=True)

def actualizar_contenido_mensualmente():
    print("🔄 Actualizando CONTENIDOS...", flush=True)
    try:
        model.sync_todos_los_contenidos()
        print("✅ Contenidos actualizados", flush=True)
    except Exception as e:
        print(f"❌ Error contenidos: {str(e)}", flush=True)
        
def actualizar_comunidades_mensualmente():
    print("🔄 Actualizando COMUNIDADES...", flush=True)
    try:
        model.sync_todas_las_comunidades()
        print("✅ Comunidades actualizadas", flush=True)
    except Exception as e:
        print(f"❌ Error comunidades: {str(e)}", flush=True)
        

        

# --- 2. CONFIGURACIÓN DEL LIFESPAN (Ciclo de Vida) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # === AL INICIAR (STARTUP) ===
    print("🚀 Iniciando aplicación y planificador...", flush=True)
    
    if not scheduler.running:
        # Jobs mensuales
        scheduler.add_job(actualizar_mensualmente, trigger="cron", day=1, hour=0, minute=0)
        scheduler.add_job(actualizar_contenido_mensualmente, trigger="cron", day=1, hour=0, minute=2)
        scheduler.add_job(actualizar_comunidades_mensualmente, trigger="cron", day=1, hour=0, minute=3)
        
        # Job de PRUEBA (Cada 30 segundos) - Para ver si funciona ahora
        # scheduler.add_job(
        #     actualizar_comunidades_mensualmente, 
        #     trigger="interval", 
        #     seconds=5,
        #     id="job_prueba_comunidades", # ID para evitar duplicados
        #     replace_existing=True
        # )
        
        # scheduler.add_job(
        #     actualizar_mensualmente, 
        #     trigger="interval", 
        #     seconds=10,
        #     id="job_prueba_artistas", # ID para evitar duplicados
        #     replace_existing=True
        # )
        
        
        # scheduler.add_job(
        #     actualizar_contenido_mensualmente, 
        #     trigger="interval", 
        #     seconds=20,
        #     id="job_prueba_contenidos", # ID para evitar duplicados
        #     replace_existing=True
        # )
        

        scheduler.start()
        print("🗓️ Scheduler iniciado correctamente", flush=True)
        scheduler.print_jobs() # Imprime en consola qué trabajos hay programados

    app.state.model = model
    
    yield # <--- Aquí la app se queda corriendo
    
    # === AL APAGAR (SHUTDOWN) ===
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler detenido", flush=True)

# --- 3. INICIALIZAR LA APP (UNA SOLA VEZ) ---
app = FastAPI(
    title="Microservicio de Estadísticas",
    lifespan=lifespan # Aquí vinculamos el ciclo de vida
)

# --- 4. CONFIGURAR MIDDLEWARE (CORS) ---
# Nota: He quitado 'setup_cors(app)' porque chocaba con esto. 
# Es mejor configurar CORS explícitamente aquí.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- 5. INCLUIR RUTAS ---
app.include_router(estadisticas_router)

@app.get("/")
def root():
    return {"message": "Microservicio de Estadísticas activo"}
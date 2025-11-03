from fastapi import APIRouter, HTTPException, Query
from model.factory.model import Model

router = APIRouter(prefix="/v1/estadisticas", tags=["Estadísticas"])
model = Model()

# ============================================================
# GET /comunidades/activas/{id}
# Devuelve datos actuales de una comunidad activa
# ============================================================
@router.get("/comunidades/activas/{id}")
def get_comunidad_activa(id: int):
    """
    Devuelve la información actual de una comunidad activa almacenada en la BD.
    """
    data = model.get_comunidad_activa(id_comunidad=id)
    if not data:
        raise HTTPException(status_code=404, detail="Comunidad no encontrada o sin datos.")
    return data


# ============================================================
# PUT /comunidades/activas
# Sincroniza con el microservicio de Comunidad (Django)
# ============================================================
@router.put("/comunidades/activas")
def put_comunidad_activa(payload: dict):
    """
    Sincroniza la comunidad indicada con el microservicio de Comunidad
    y actualiza la información almacenada.
    """
    id_comunidad = payload.get("idComunidad")
    if not id_comunidad:
        raise HTTPException(status_code=400, detail="Se requiere 'idComunidad' en el body.")
    try:
        data = model.sync_comunidad_activa(id_comunidad=id_comunidad)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sincronizar comunidad: {e}")


# ============================================================
# GET /contenidos/valoracion/{id}
# Devuelve la valoración actual de un contenido (álbum o canción)
# ============================================================
@router.get("/contenidos/valoracion/{id}")
def get_contenido_valoracion(id: int, esAlbum: bool = Query(..., description="True si es álbum, False si es canción")):
    """
    Devuelve los datos actuales de valoración de un contenido.
    """
    data = model.get_contenido_valoracion(id_contenido=id, es_album=esAlbum)
    if not data:
        raise HTTPException(status_code=404, detail="Contenido no encontrado o sin datos.")
    return data


# ============================================================
# PUT /contenidos/valoracion
# Sincroniza datos con el microservicio de Contenido (Spring)
# ============================================================
@router.put("/contenidos/valoracion")
def put_contenido_valoracion(id: int = Query(..., description="ID del contenido"),
                             esAlbum: bool = Query(..., description="True si es álbum, False si es canción")):
    """
    Sincroniza un contenido específico con el microservicio de Contenido
    y actualiza su valoración en la BD local.
    """
    try:
        data = model.sync_contenido_valoracion(id_contenido=id, es_album=esAlbum)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sincronizar contenido: {e}")

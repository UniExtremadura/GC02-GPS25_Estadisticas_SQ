from fastapi import APIRouter, HTTPException, Request
from backend.model.model import Model

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])
model = Model()

USUARIOS_API = "http://localhost:3000"   # API USUARIOS

# ========================= ARTISTAS =========================

@router.get("/artistas/oyentes/{id_artista}")
async def get_oyentes_artista(id_artista: int, request: Request):
    """
    Obtiene los oyentes de un artista.
    Maneja errores comunes:
    - 400: ID inválido
    - 404: Artista no encontrado
    - 422: Parámetros no válidos
    - 500: Error interno de servidor
    """
    try:
        # 400 - Validación manual del parámetro (ID <= 0 no tiene sentido)
        if id_artista <= 0:
            raise HTTPException(
                status_code=400,
                detail="El ID del artista debe ser un número entero positivo."
            )

        # Llamada al modelo
        data = model.get_artista_oyentes(id_artista)

        # 404 - No existe ese artista
        if not data:
            raise HTTPException(
                status_code=404,
                detail="No hay estadísticas para ese artista."
            )

        return data

    # 422 - (FastAPI los lanza solo, pero puedes capturarlos si quieres)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="El parámetro proporcionado no es válido."
        )

    # Error de base de datos (SQLAlchemy)
    except Exception as e:
        # Log del error para depuración
        print(f"❌ Error en get_oyentes_artista: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener los oyentes: {str(e)}"
        )


@router.put("/artistas/oyentes")
async def sync_oyentes_artista(request: Request):
    """
    Sincroniza los oyentes de un artista.
    Manejo de errores:
    - 400: Falta idArtista o valor inválido
    - 404: Artista no encontrado
    - 422: Datos mal formados
    - 500: Error interno
    """
    try:
        # Obtener JSON del body
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=422,
                detail="El cuerpo de la solicitud no es un JSON válido."
            )

        id_artista = body.get("idArtista")

        # Validación del parámetro
        if id_artista is None:
            raise HTTPException(
                status_code=400,
                detail="Falta el campo obligatorio 'idArtista'."
            )

        if not isinstance(id_artista, int) or id_artista <= 0:
            raise HTTPException(
                status_code=400,
                detail="'idArtista' debe ser un entero positivo."
            )

        # Llamada al modelo
        data = model.sync_artista_oyentes(id_artista)

        # Si devuelve None → artista no existe
        if data is None:
            raise HTTPException(
                status_code=404,
                detail="No se pudo sincronizar: el artista no existe."
            )

        return data

    except HTTPException:
        raise

    except Exception as e:
        print(f"❌ Error interno en sync_oyentes_artista: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al sincronizar oyentes: {str(e)}"
        )

@router.delete("/artistas/{id_artista}")
async def delete_artista_stats(id_artista: int, request: Request):
    """
    Elimina las estadísticas de un artista.
    Maneja errores comunes:
    - 400: ID inválido
    - 404: Artista no encontrado en estadísticas
    - 500: Error interno de servidor
    """
    try:
        # 400 - Validación manual del parámetro
        if id_artista <= 0:
            raise HTTPException(
                status_code=400,
                detail="El ID del artista debe ser un número entero positivo."
            )

        # Llamada al modelo
        # (Asumiendo que 'model' está disponible en request.app.state o globalmente)
        # model = request.app.state.model  <-- Descomenta si lo obtienes del state
        data = model.delete_artista_estadisticas(id_artista)

        # 404 - No se encontró registro para borrar
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron estadísticas para el artista con ID {id_artista}."
            )

        return data

    # 422 - Validación de tipos (FastAPI suele capturarlo antes, pero por consistencia)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="El parámetro proporcionado no es válido."
        )

    # 500 - Error interno (Base de datos, etc.)
    except Exception as e:
        print(f"❌ Error en delete_artista_stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al eliminar el artista: {str(e)}"
        )

@router.get("/artistas/ranking/oyentes")
async def ranking_oyentes(request: Request):
    """
    Devuelve el ranking de artistas por oyentes mensuales.
    Manejo de errores:
    - 404: No hay datos de ranking
    - 500: Error interno del servidor
    """
    try:
        ranking = model.get_ranking_artistas_oyentes()

        if ranking is None or len(ranking) == 0:
            raise HTTPException(
                status_code=404,
                detail="No hay datos de ranking disponibles."
            )

        return ranking

    except HTTPException:
        raise

    except Exception as e:
        print(f"❌ Error interno en ranking_oyentes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener ranking: {str(e)}"
        )


@router.put("/artistas/busqueda")
async def registrar_busqueda_artista(request: Request):
    """
    Registra una búsqueda de un artista cada vez que un usuario busque o haga clic en el perfil de un artista.
    Manejo de errores:
    - 400: Falta idArtista o es inválido
    - 422: Cuerpo no es JSON válido
    - 500: Error interno
    """
    try:
        # Intentamos leer el JSON del body
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=422,
                detail="El cuerpo de la solicitud no es un JSON válido."
            )

        id_artista = body.get("idArtista")
        id_usuario = body.get("idUsuario")  # opcional

        # Validación de idArtista (obligatorio)
        if id_artista is None:
            raise HTTPException(
                status_code=400,
                detail="Falta el campo obligatorio 'idArtista'."
            )

        if not isinstance(id_artista, int) or id_artista <= 0:
            raise HTTPException(
                status_code=400,
                detail="'idArtista' debe ser un entero positivo."
            )

        # Validación opcional de idUsuario (si viene)
        if id_usuario is not None:
            if not isinstance(id_usuario, int) or id_usuario <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="'idUsuario', si se proporciona, debe ser un entero positivo."
                )

        # Registrar/actualizar la búsqueda
        model.registrar_o_actualizar_busqueda_artista(id_artista, id_usuario)

        return {"msg": "Búsqueda registrada correctamente."}

    except HTTPException:
        # Re-lanzamos las que ya están controladas
        raise

    except Exception as e:
        print(f"❌ Error interno en registrar_busqueda_artista: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al registrar la búsqueda."
        )
    
# ==========================================
# DELETE BÚSQUEDAS POR ARTISTA
# ==========================================
@router.delete("/artistas/busqueda/artista/{id_artista}")
async def delete_busquedas_por_artista(id_artista: int, request: Request):
    """
    Elimina el historial de búsquedas asociado a un artista.
    Útil cuando se elimina un artista del sistema.
    """
    try:
        # Validación manual
        if id_artista <= 0:
            raise HTTPException(status_code=400, detail="El ID del artista debe ser positivo.")

        # Llamada al modelo
        # model = request.app.state.model (Si lo usas desde state)
        resultado = model.delete_busquedas_artista(id_artista)

        # Nota: No devolvemos 404 si borra 0 filas, porque el objetivo es "limpiar".
        # Si ya estaba limpio, misión cumplida (200 OK).
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando búsquedas de artista: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# ==========================================
# DELETE BÚSQUEDAS POR USUARIO
# ==========================================
@router.delete("/artistas/busqueda/usuario/{id_usuario}")
async def delete_busquedas_por_usuario(id_usuario: int, request: Request):
    """
    Elimina el historial de búsquedas realizado por un usuario.
    Útil cuando se elimina un usuario del sistema (GDPR/Limpieza).
    """
    try:
        # Validación manual
        if id_usuario <= 0:
            raise HTTPException(status_code=400, detail="El ID del usuario debe ser positivo.")

        # Llamada al modelo
        resultado = model.delete_busquedas_usuario(id_usuario)

        return resultado

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando búsquedas de usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/artistas/top")
async def get_top_artistas(request: Request, limit: int = 10):
    """
    Devuelve el top de artistas más buscados del mes.
    Manejo de errores:
    - 400: 'limit' inválido
    - 404: No hay datos
    - 500: Error interno
    """
    try:
        # Validación de 'limit'
        if limit <= 0:
            raise HTTPException(
                status_code=400,
                detail="'limit' debe ser un entero positivo."
            )

        # (Opcional) límite máximo razonable para no reventar la API
        if limit > 100:
            raise HTTPException(
                status_code=400,
                detail="'limit' no puede ser mayor que 100."
            )

        top = model.get_top_artistas_busquedas(limit=limit)

        if not top or len(top) == 0:
            raise HTTPException(
                status_code=404,
                detail="No hay datos de artistas más buscados para este periodo."
            )

        return top

    except HTTPException:
        raise

    except Exception as e:
        print(f"❌ Error interno en get_top_artistas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener el top de artistas."
        )

@router.get("/contenido")
async def get_todos_los_contenidos(request: Request):
    """
    Obtiene todos los contenidos con sus estadísticas.

    Posibles errores:
    - 404: No se encontraron contenidos
    - 500: Error interno del servidor o de la base de datos
    """
    try:
        # Llamada al modelo
        contenidos = model.get_todos_los_contenidos()

        # Si el modelo devuelve None o una lista vacía
        if contenidos is None:
            print("⚠️ El modelo devolvió None en get_todos_los_contenidos()")
            raise HTTPException(
                status_code=500,
                detail="El servicio no devolvió datos válidos."
            )

        if isinstance(contenidos, list) and len(contenidos) == 0:
            print("ℹ️ No hay contenidos registrados en la base de datos.")
            raise HTTPException(
                status_code=404,
                detail="No se encontraron contenidos."
            )

        # Todo OK
        return {
            "status": "success",
            "count": len(contenidos) if isinstance(contenidos, list) else None,
            "data": contenidos
        }

    except HTTPException as http_error:
        # Errores lanzados manualmente
        print(f"⚠️ Error controlado: {http_error.detail}")
        raise http_error

    except ConnectionError as ce:
        # Error típico de DB o API externa
        print(f"❌ Error de conexión con la base de datos: {ce}")
        raise HTTPException(
            status_code=500,
            detail="Error de conexión con la base de datos."
        )

    except Exception as e:
        # Error inesperado
        print(f"❌ Error interno no controlado en get_todos_los_contenidos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener los contenidos."
        )

@router.put("/contenido")
async def sincronizar_contenido(request: Request):
    """
    Sincroniza un contenido específico trayendo datos frescos de las APIs externas.
    Body: { "idContenido": 123 }
    """
    try:
        body = await request.json()
        id_contenido = body.get("idContenido")

        if not id_contenido or not isinstance(id_contenido, int):
            raise HTTPException(status_code=400, detail="JSON inválido: Falta 'idContenido' (int).")

        # Llamada al modelo
        resultado = model.sincronizar_desde_api_externa(id_contenido)

        return {
            "status": "success",
            "message": "Sincronización completada",
            "data": resultado
        }
    
    except Exception as e:
        print(f"❌ Error interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
    
@router.get("/contenido/{id_contenido}")
async def get_estadisticas_contenido(id_contenido: int, request: Request):
    """ Obtiene las estadísticas (ventas, comentarios, etc.) """
    try:
        if id_contenido <= 0:
            raise HTTPException(status_code=400, detail="El ID debe ser positivo.")

        data = model.get_contenido_detalle(id_contenido)

        if not data:
            raise HTTPException(status_code=404, detail=f"No existen estadísticas para ID {id_contenido}.")

        return data

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error GET contenido: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete("/contenido/{id_contenido}")
async def delete_estadisticas_contenido(id_contenido: int, request: Request):
    """ Elimina el registro de estadísticas """
    try:
        if id_contenido <= 0:
            raise HTTPException(status_code=400, detail="El ID debe ser positivo.")

        resultado = model.delete_contenido(id_contenido)

        if not resultado:
            raise HTTPException(status_code=404, detail=f"No encontrado ID {id_contenido}.")

        return resultado

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error DELETE contenido: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
# ==========================================
# 1. TOP VALORACIÓN
# ==========================================
@router.get("/contenidos/valoracion/top")
async def get_top_valoracion(request: Request, limit: int = 10):
    """
    Devuelve el top de contenidos mejor valorados.
    """
    try:
        # Validación de 'limit'
        if limit <= 0:
            raise HTTPException(
                status_code=400, 
                detail="'limit' debe ser un entero positivo."
            )
        
        if limit > 100:
            raise HTTPException(
                status_code=400, 
                detail="'limit' no puede ser mayor que 100."
            )

        # Llamada al modelo
        top = model.get_top_contenidos_valoracion(limit=limit)

        # 404 - Si la lista está vacía
        if not top or len(top) == 0:
            raise HTTPException(
                status_code=404, 
                detail="No hay datos de valoración para este periodo."
            )

        return top

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error interno en get_top_valoracion: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno al obtener el top de valoraciones."
        )


# ==========================================
# 2. TOP COMENTARIOS
# ==========================================
@router.get("/contenidos/comentarios/top")
async def get_top_comentarios(request: Request, limit: int = 10):
    """
    Devuelve el top de contenidos con más comentarios.
    """
    try:
        if limit <= 0:
            raise HTTPException(status_code=400, detail="'limit' debe ser positivo.")
        if limit > 100:
            raise HTTPException(status_code=400, detail="'limit' no puede ser mayor que 100.")

        top = model.get_top_contenidos_comentarios(limit=limit)

        if not top or len(top) == 0:
            raise HTTPException(
                status_code=404, 
                detail="No hay datos de comentarios para este periodo."
            )

        return top

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error interno en get_top_comentarios: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno al obtener el top de comentarios."
        )


# ==========================================
# 3. TOP VENTAS
# ==========================================
@router.get("/contenidos/ventas/top")
async def get_top_ventas(request: Request, limit: int = 10):
    """
    Devuelve el top de contenidos más vendidos.
    """
    try:
        if limit <= 0:
            raise HTTPException(status_code=400, detail="'limit' debe ser positivo.")
        if limit > 100:
            raise HTTPException(status_code=400, detail="'limit' no puede ser mayor que 100.")

        top = model.get_top_contenidos_ventas(limit=limit)

        if not top or len(top) == 0:
            raise HTTPException(
                status_code=404, 
                detail="No hay datos de ventas para este periodo."
            )

        return top

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error interno en get_top_ventas: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno al obtener el top de ventas."
        )
        
@router.get("/contenidos/genero/top")
async def get_top_generos(request: Request, limit: int = 5):
    """
    Devuelve los géneros musicales con más ventas acumuladas.
    Ejemplo: Rock (1500 ventas), Pop (1200 ventas).
    """
    try:
        model = request.app.state.model
        
        if limit <= 0 or limit > 100:
            limit = 5  # Valor por defecto seguro
            
        ranking = model.get_top_generos(limit=limit)

        if not ranking:
            # Opción A: Devolver 404
            # raise HTTPException(status_code=404, detail="No hay datos de géneros.")
            # Opción B: Devolver lista vacía (a veces es mejor para frontend)
            return []

        return ranking

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
# ==========================================
#  COMUNIDADES 
# ==========================================

@router.put("/comunidad")
async def sincronizar_comunidad(request: Request):
    """
    Sincroniza una comunidad específica trayendo datos frescos de la API externa.
    Body: { "idComunidad": "1" }
    Ruta final: /estadisticas/comunidad
    """
    try:
        body = await request.json()
        id_comunidad = body.get("idComunidad")

        if not id_comunidad:
            raise HTTPException(status_code=400, detail="JSON inválido: Falta 'idComunidad'.")

        # Llamada al modelo (instancia global definida arriba)
        resultado = model.sincronizar_comunidad_desde_api(id_comunidad)

        return {
            "status": "success",
            "message": "Sincronización de comunidad completada",
            "data": resultado
        }
    
    except Exception as e:
        print(f"❌ Error interno comunidad: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
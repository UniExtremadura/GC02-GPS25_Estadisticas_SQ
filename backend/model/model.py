import requests
from model.dao.postgresql.postgresDAOFactory import PostgreSQLDAOFactory
from controller.config import MS_COMUNIDAD_BASE_URL, MS_CONTENIDO_BASE_URL

class Model:
    def __init__(self):
        # Crear fábrica de DAOs de PostgreSQL
        self.factory = PostgreSQLDAOFactory()
        # Instancias de los DAOs que se usan en este microservicio
        self.artistasMensualesDAO = self.factory.get_artistas_mensuales_dao()
        self.comunidadesMensualesDAO = self.factory.get_comunidades_mensuales_dao()
        self.contenidosMensualesDAO = self.factory.get_contenidos_mensuales_dao()

    # ==========================================================
    # GET públicos (consultan la BD local actualizada)
    # ==========================================================

    def get_comunidad_activa(self, id_comunidad: int):
        """Obtiene los datos actuales de una comunidad activa."""
        fila = self.comunidadesMensualesDAO.obtener_por_id(id_comunidad)
        if not fila:
            return None
        return {
            "idComunidad": fila.idComunidad,
            "nombre": None,  # Podrías traerlo del MS de Comunidad si quieres
            "numPublicaciones": int(fila.numPublicaciones),
            "numMiembros": int(fila.numMiembros)
        }

    def get_contenido_valoracion(self, id_contenido: int, es_album: bool):
        """Obtiene la valoración media actual de un contenido."""
        fila = self.contenidosMensualesDAO.obtener_por_id(id_contenido)
        if not fila:
            return None
        total_val = int(fila.numValoraciones or 0)
        media = float(fila.sumaValoraciones) / total_val if total_val > 0 else 0.0
        return {
            "idElemento": fila.idContenido,
            "nombre": None,  # Puedes completarlo con datos del MS Contenido
            "esAlbum": bool(fila.esAlbum),
            "valoracionMedia": round(media, 2),
            "totalValoraciones": total_val,
            "numComentarios": int(fila.numComentarios or 0),
            "numReproducciones": int(fila.numReproducciones or 0)
        }

    # ==========================================================
    # PUT (sincronización con otros microservicios)
    # ==========================================================

    def sync_comunidad_activa(self, id_comunidad: int):
        """
        Llama al microservicio de Comunidad (Django) para obtener la actividad actual
        y actualiza la tabla comunidadesMensual.
        """
        url = f"{MS_COMUNIDAD_BASE_URL}/v1/comunidades/{id_comunidad}/actividad"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        # Espera recibir algo como: {"numPublicaciones": 245, "numMiembros": 1892, "nombre": "Fans Rock"}
        fila = self.comunidadesMensualesDAO.upsert(
            id_comunidad=id_comunidad,
            num_publicaciones=int(data.get("numPublicaciones", 0)),
            num_miembros=int(data.get("numMiembros", 0))
        )

        return {
            "idComunidad": fila.idComunidad,
            "nombre": data.get("nombre"),
            "numPublicaciones": int(fila.numPublicaciones),
            "numMiembros": int(fila.numMiembros)
        }

    def sync_contenido_valoracion(self, id_contenido: int, es_album: bool):
        """
        Llama al microservicio de Contenido (Spring/Oracle) para obtener
        los datos de valoraciones, comentarios y reproducciones,
        y actualiza la tabla contenidosMensual.
        """
        tipo = "album" if es_album else "cancion"
        url = f"{MS_CONTENIDO_BASE_URL}/v1/{tipo}s/{id_contenido}/valoraciones"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        # Ejemplo de respuesta esperada:
        # {"sumaValoraciones": 1500, "numValoraciones": 300, "numComentarios": 45, "numReproducciones": 12000}
        fila = self.contenidosMensualesDAO.upsert(
            id_contenido=id_contenido,
            es_album=bool(es_album),
            suma_val=float(data.get("sumaValoraciones", 0)),
            num_val=int(data.get("numValoraciones", 0)),
            num_com=int(data.get("numComentarios", 0)),
            num_rep=int(data.get("numReproducciones", 0))
        )

        total_val = int(fila.numValoraciones or 0)
        media = float(fila.sumaValoraciones) / total_val if total_val > 0 else 0.0

        return {
            "idElemento": fila.idContenido,
            "nombre": data.get("nombre"),
            "esAlbum": bool(fila.esAlbum),
            "valoracionMedia": round(media, 2),
            "totalValoraciones": total_val,
            "numComentarios": int(fila.numComentarios or 0),
            "numReproducciones": int(fila.numReproducciones or 0)
        }

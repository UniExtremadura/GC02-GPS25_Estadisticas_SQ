from fastapi import HTTPException
import requests
from backend.model.dao.postgresql.postgresDAOFactory import PostgreSQLDAOFactory
from backend.controller.config import MS_USUARIOS_BASE_URL, CONTENIDO_API_BASE_URL, COMUNIDAD_API_BASE_URL
from backend.model.dto.contenidoDTO import ContenidoDTO
from backend.model.dto.comunidadMensualDTO import ComunidadDTO


class Model:
    def __init__(self):
        # Crear fábrica de DAOs de PostgreSQL
        self.factory = PostgreSQLDAOFactory()
        # Instancias de los DAOs que se usan en este microservicio
        self.artistasMensualesDAO = self.factory.get_artistas_mensuales_dao()
        self.busquedasArtistasDAO = self.factory.get_busquedas_artistas_dao()
        self.contenidoDAO = self.factory.get_contenido_dao()      
        self.comunidadDAO = self.factory.get_comunidad_dao()
        self.URL_CONTENIDOS = f"{CONTENIDO_API_BASE_URL}/elementos" 
        self.URL_VALORACIONES = f"{CONTENIDO_API_BASE_URL}/usuarioValoraElem"
        self.URL_COMUNIDAD = f"{COMUNIDAD_API_BASE_URL}/comunidad"
        
        # IMPORTANTE: Asignamos la sesión de DB para poder hacer rollbacks
        # Asumo que tu factory tiene la propiedad 'db' o 'session'. 
        # Si se llama diferente en tu factory, cámbialo aquí.
        self.db = self.factory.db 

    def get_artista_oyentes(self, id_artista: int):
        self.db.rollback()  # Limpieza preventiva
        try:
            fila = self.artistasMensualesDAO.obtener_por_id(id_artista)
            if not fila:
                return None
            return {
                "idArtista": fila.idArtista,
                "numOyentes": int(fila.numOyentes or 0),
                "valoracionMedia": int(fila.valoracionMedia or 0),
            }
        except Exception as e:
            print(f"❌ Error DB en get_artista_oyentes: {e}")
            self.db.rollback()
            raise e
        

    def get_ranking_artistas_oyentes(self):
        self.db.rollback() # Limpieza preventiva
        try:
            filas = self.artistasMensualesDAO.obtener_ranking_oyentes()
            return [
                {
                    "idArtista": f.idArtista,
                    "numOyentes": int(f.numOyentes or 0),
                    "valoracionMedia": int(f.valoracionMedia or 0),
                }
                for f in filas
            ]
        except Exception as e:
            print(f"❌ Error DB en get_ranking_artistas_oyentes: {e}")
            self.db.rollback()
            raise e

    # ================== ARTISTAS (PUT: sincronización mensual) ==============

    def sync_artista_oyentes(self, id_artista: int):
        self.db.rollback()  # Limpieza preventiva
        
        try:
            url = f"{MS_USUARIOS_BASE_URL}/api/usuarios/artistas/{id_artista}"

            resp = requests.get(url, timeout=20)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Artista no encontrado en MS Usuarios")

            resp.raise_for_status()
            data = resp.json()

            # Accedemos directamente a los campos del JSON
            oyentes = data.get("oyentes", 0)
            valoracion = data.get("valoracion", 0)

            # Llamamos a 'upsert'
            self.artistasMensualesDAO.upsert(
                id_artista=id_artista,
                num_oyentes=oyentes,
                valoracion_media=valoracion
            )
            
            # Confirmamos cambios
            self.db.commit()

            return {
                "idArtista": id_artista,
                "numOyentes": oyentes,
                "valoracionMedia": valoracion
            }
        except Exception as e:
            print(f"❌ Error en sync_artista_oyentes: {e}")
            self.db.rollback() # Rollback en caso de error
            raise e

    
    def obtener_artistas_desde_api(self):
        # Aquí no hay DB, no hace falta rollback, pero no estorba
        url = f"{MS_USUARIOS_BASE_URL}/api/usuarios/artistas" 

        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            return resp.json() 
        except Exception as e:
            print("❌ Error obteniendo artistas desde MS Usuarios:", e)
            return []
        
    def sync_todos_los_artistas(self):
        self.db.rollback() # Limpieza inicial
        artistas = self.obtener_artistas_desde_api()

        if not artistas:
            print("⚠️ No se pudo obtener la lista de artistas")
            return

        print(f"🔄 Sincronizando {len(artistas)} artistas...")

        resultados = []
        for artista in artistas:
            id_artista = artista.get("id") # Uso .get para seguridad
            try:
                # sync_artista_oyentes ya tiene sus propios rollbacks internos
                resultado = self.sync_artista_oyentes(id_artista)
                resultados.append(resultado)
            except Exception as e:
                print(f"❌ Error sincronizando artista {id_artista}:", e)
                # Importante: aseguramos rollback aquí por si acaso
                self.db.rollback() 

        print("✅ Sincronización completa")
        return resultados
    
    def delete_artista_estadisticas(self, id_artista: int):
        self.db.rollback()  # Limpieza preventiva
        try:
            # Llamamos al DAO
            eliminado = self.artistasMensualesDAO.eliminar(id_artista)
            
            if not eliminado:
                return None
            
            # Si se eliminó correctamente, confirmamos los cambios en BD
            self.db.commit()
            
            return {
                "idArtista": id_artista,
                "mensaje": "Estadísticas del artista eliminadas correctamente."
            }
            
        except Exception as e:
            print(f"❌ Error DB en delete_artista_estadisticas: {e}")
            self.db.rollback()  # Revertimos si hubo error
            raise e

    # ================== BUSQUEDAS ARTISTAS ==================
    def registrar_o_actualizar_busqueda_artista(self, id_artista: int, id_usuario: int | None = None):
        self.db.rollback() # Limpieza preventiva
        print(f"✅ Registrando o actualizando búsqueda para el artista {id_artista} y el usuario {id_usuario}")
        
        try:
            self.busquedasArtistasDAO.insertar_o_actualizar_busqueda(id_artista, id_usuario)
            self.db.commit()
        except Exception as e:
            print(f"❌ Error en registrar busqueda: {e}")
            self.db.rollback()
            raise e


    def get_top_artistas_busquedas(self, limit: int = 10):
        self.db.rollback() 
        try:
            filas = self.busquedasArtistasDAO.get_top_artistas_busquedas(limit)
            return [
                {
                    "idArtista": f.idArtista,
                    "numBusquedas": int(f.numBusquedas or 0)
                }
                for f in filas
            ]
        except Exception as e:
            self.db.rollback()
            raise e
        
    # ================== DELETE BÚSQUEDAS ==================

    def delete_busquedas_artista(self, id_artista: int):
        self.db.rollback() # Limpieza preventiva
        try:
            # Llamamos al DAO
            filas_borradas = self.busquedasArtistasDAO.eliminar_busquedas_por_artista(id_artista)
            
            # Confirmamos cambios
            self.db.commit()
            
            return {
                "idArtista": id_artista,
                "filasEliminadas": filas_borradas,
                "mensaje": f"Se eliminaron {filas_borradas} registros de búsqueda para este artista."
            }
        except Exception as e:
            print(f"❌ Error en delete_busquedas_artista: {e}")
            self.db.rollback()
            raise e

    def delete_busquedas_usuario(self, id_usuario: int):
        self.db.rollback() # Limpieza preventiva
        try:
            # Llamamos al DAO
            filas_borradas = self.busquedasArtistasDAO.eliminar_busquedas_por_usuario(id_usuario)
            
            # Confirmamos cambios
            self.db.commit()
            
            return {
                "idUsuario": id_usuario,
                "filasEliminadas": filas_borradas,
                "mensaje": f"Se eliminaron {filas_borradas} registros de búsqueda de este usuario."
            }
        except Exception as e:
            print(f"❌ Error en delete_busquedas_usuario: {e}")
            self.db.rollback()
            raise e
        
    # ================== CONTENIDO ==================    
    def get_todos_los_contenidos(self):
        self.db.rollback() 
        try:
            filas = self.contenidoDAO.obtener_todos()
            return [
                {
                    "idContenido": f.idContenido,
                    "numVentas": int(f.numVentas or 0),
                    "esAlbum": f.esAlbum,
                    "sumaValoraciones": int(f.sumaValoraciones or 0),
                    "numComentarios": int(f.numComentarios or 0),
                    "genero": f.genero,
                    "esNovedad": f.esNovedad
                }
                for f in filas
            ]
        except Exception as e:
            self.db.rollback()
            raise e

    def sincronizar_desde_api_externa(self, id_contenido: int):
        self.db.rollback() 
        print(f"🔄 Sincronizando contenido ID: {id_contenido}...")

        try:
            # 1. API Elementos
            resp_elem = requests.get(f"{self.URL_CONTENIDOS}/{id_contenido}", timeout=10)
            resp_elem.raise_for_status()
            data_elem = resp_elem.json()

            # Extracción de campos básicos
            num_ventas = data_elem.get("numventas", 0)
            valoracion_media = data_elem.get("valoracion", 0.0)
            es_album = data_elem.get("esalbum", False)
            es_novedad = data_elem.get("esnovedad", False) # <--- Nuevo campo booleano

            # Extracción del Género (Objeto -> String)
            nombre_genero = "Desconocido"
            obj_genero = data_elem.get("genero")
            if obj_genero and isinstance(obj_genero, dict):
                # Si viene null el nombre, ponemos "Desconocido"
                nombre_genero = obj_genero.get("nombre") or "Desconocido"
            elif obj_genero is None:
                nombre_genero = "Desconocido"

            # 2. API Comentarios
            num_comentarios = 0
            try:
                url_coments = f"{self.URL_VALORACIONES}/{id_contenido}"
                resp_com = requests.get(url_coments, timeout=10)
                if resp_com.status_code == 200:
                    lista = resp_com.json()
                    reales = [c for c in lista if c.get("comentario") and str(c.get("comentario")).strip() != ""]
                    num_comentarios = len(reales)
            except Exception:
                num_comentarios = 0

            # 3. Guardar DTO
            dto = ContenidoDTO(
                idcontenido=id_contenido,
                numventas=int(num_ventas),
                esalbum=bool(es_album),
                sumavaloraciones=float(valoracion_media),
                numcomentarios=int(num_comentarios),
                genero=str(nombre_genero),
                esnovedad=bool(es_novedad) # <--- Pasamos el booleano
            )

            self.contenidoDAO.actualizar_o_insertar(dto)
            self.db.commit() 
            
            print(f"✅ ID {id_contenido} | Gen: {nombre_genero} | Nov: {es_novedad}")

            return {
                "id": id_contenido,
                "esAlbum": es_album,
                "esNovedad": es_novedad, # <--- Devolvemos para confirmar
                "genero": nombre_genero,
                "ventas": num_ventas
            }

        except Exception as e:
            print(f"❌ Error procesando datos: {e}")
            self.db.rollback()
            raise e
    
    def obtener_lista_contenidos_api(self):
            """
            Obtiene la lista de TODOS los elementos (IDs) desde la API externa.
            Asumimos que GET /elementos devuelve una lista de objetos [{"id": 1, ...}, ...]
            """
            # No requiere transacción DB, solo petición HTTP
            try:
                # Usamos la URL base que ya definiste: .../api/elementos
                resp = requests.get(self.URL_CONTENIDOS, timeout=20)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                print("❌ Error obteniendo lista de contenidos desde API externa:", e)
                return []

    def sync_todos_los_contenidos(self):
        """
        Recorre todos los contenidos de la API externa y actualiza sus estadísticas localmente.
        """
        self.db.rollback() # Limpieza inicial preventiva
        
        # 1. Obtenemos la lista de contenidos existentes en el otro microservicio
        contenidos = self.obtener_lista_contenidos_api()

        if not contenidos:
            print("⚠️ No se pudo obtener la lista de contenidos para sincronizar.")
            return

        print(f"🔄 Sincronizando estadísticas de {len(contenidos)} contenidos...")

        resultados = []
        for item in contenidos:
            # Asumimos que el JSON tiene un campo "id". Si es diferente, cámbialo aquí.
            id_contenido = item.get("id") 
            
            if not id_contenido:
                continue

            try:
                # Reutilizamos tu método individual que YA TIENE la protección try/except/rollback
                resultado = self.sincronizar_desde_api_externa(id_contenido)
                resultados.append(resultado)
            except Exception as e:
                # Este print es por si falla algo fuera del try interno de sincronizar_desde_api_externa
                print(f"❌ Error crítico sincronizando contenido {id_contenido}:", e)
                self.db.rollback() 

        print("✅ Sincronización masiva de contenidos completada.")
        return resultados    

# ================== GESTIÓN MANUAL DE CONTENIDO (GET, DELETE) ==================

    def get_contenido_detalle(self, id_contenido: int):
        self.db.rollback() 
        try:
            fila = self.contenidoDAO.obtener_por_id(id_contenido)
            if not fila:
                return None
            
            # Devolvemos el objeto con la clave 'numVentas'
            return {
                "idContenido": fila.idContenido,
                "numVentas": fila.numVentas,       # <--- Dato correcto
                "esAlbum": fila.esAlbum,
                "sumaValoraciones": fila.sumaValoraciones,
                "numComentarios": fila.numComentarios, 
                "genero": fila.genero,
                "esNovedad": fila.esNovedad
            }
        except Exception as e:
            print(f"❌ Error en get_contenido: {e}")
            self.db.rollback()
            raise e

    def delete_contenido(self, id_contenido: int):
        self.db.rollback()
        try:
            eliminado = self.contenidoDAO.eliminar(id_contenido)
            
            if not eliminado:
                return None
            
            self.db.commit()
            
            return {
                "idContenido": id_contenido,
                "mensaje": "Contenido eliminado de las estadísticas correctamente"
            }
        except Exception as e:
            print(f"❌ Error eliminando contenido: {e}")
            self.db.rollback()
            raise e

# ================== TOPS / RANKINGS DE CONTENIDO ==================

    def get_top_contenidos_valoracion(self, limit: int = 10):
        self.db.rollback() # Limpieza preventiva
        try:
            filas = self.contenidoDAO.get_top_valorados(limit)
            
            return [
                {
                    "idContenido": row.idcontenido,
                    "esAlbum": row.esalbum,
                    "sumaValoraciones": float(row.sumavaloraciones or 0),
                    "numVentas": int(row.numventas or 0)
                }
                for row in filas
            ]
        except Exception as e:
            print(f"❌ Error en get_top_contenidos_valoracion: {e}")
            self.db.rollback()
            raise e

    def get_top_contenidos_comentarios(self, limit: int = 10):
        self.db.rollback()
        try:
            filas = self.contenidoDAO.get_top_comentados(limit)
            
            return [
                {
                    "idContenido": row.idcontenido,
                    "esAlbum": row.esalbum,
                    "numComentarios": int(row.numcomentarios or 0),
                    "numVentas": int(row.numventas or 0)
                }
                for row in filas
            ]
        except Exception as e:
            print(f"❌ Error en get_top_contenidos_comentarios: {e}")
            self.db.rollback()
            raise e

    def get_top_contenidos_ventas(self, limit: int = 10):
        self.db.rollback()
        try:
            filas = self.contenidoDAO.get_top_vendidos(limit)
            
            return [
                {
                    "idContenido": row.idcontenido,
                    "esAlbum": row.esalbum,
                    "numVentas": int(row.numventas or 0),
                    "sumaValoraciones": float(row.sumavaloraciones or 0)
                }
                for row in filas
            ]
        except Exception as e:
            print(f"❌ Error en get_top_contenidos_ventas: {e}")
            self.db.rollback()
            raise e
        
    # ================== TOP GÉNEROS ==================

    def get_top_generos(self, limit: int = 5):
        self.db.rollback()
        try:
            # Llamamos al método de agregación del DAO
            ranking = self.contenidoDAO.get_top_generos_por_ventas(limit)
            return ranking
        except Exception as e:
            print(f"❌ Error en get_top_generos: {e}")
            self.db.rollback()
            raise e
        
    def sincronizar_comunidad_desde_api(self, id_comunidad):
        """
        Sincroniza una comunidad específica buscando en la lista completa de la API externa.
        """
        try:
            self.db.rollback() 
        except:
            pass
            
        print(f"🔄 Sincronizando comunidad ID: {id_comunidad}...")

        try:
            # 1. API Comunidad
            # Probamos CON barra al final porque dijiste que así funcionaba en el navegador
            url_llamada = f"{self.URL_COMUNIDAD}/"
            
            # TRUCO DEL HOST:
            # Forzamos el Host a 'localhost' para que el servidor de destino no rechace 'host.docker.internal'
            headers = {
                "Accept": "application/json",
                "User-Agent": "PostmanRuntime/7.26.8", # Imitamos a Postman/Navegador
                "Host": "localhost" 
            }
            
            print(f"📡 GET {url_llamada}")
            resp = requests.get(url_llamada, headers=headers, timeout=10)
            
            # Si da error 400, IMPRIMIMOS EL PORQUÉ
            if resp.status_code >= 400:
                print(f"⚠️ El servidor devolvió {resp.status_code}. Cuerpo del error:")
                print(f"➡️ {resp.text}") # <--- ESTO ES CRUCIAL PARA VER EL ERROR REAL
            
            resp.raise_for_status()
            
            lista_comunidades = resp.json()

            # 2. Búsqueda manual en la lista
            datos_comunidad = None
            target_id = str(id_comunidad)
            
            if isinstance(lista_comunidades, list):
                for item in lista_comunidades:
                    # Comparamos IDs (string vs string para evitar errores de tipo)
                    if str(item.get("idComunidad")) == target_id:
                        datos_comunidad = item
                        break
            
            if not datos_comunidad:
                print(f"⚠️ Comunidad ID {id_comunidad} no encontrada en la lista externa.")
                # No lanzamos excepción para no romper el flujo, devolvemos None o un error controlado
                return None

            # 3. Extracción y Mapeo
            raw_id = datos_comunidad.get("idComunidad")
            num_pubs = datos_comunidad.get("numPublicaciones", 0)
            num_users = datos_comunidad.get("numUsuarios", 0)

            # 4. Guardar
            dto = ComunidadDTO(
                idcomunidad=raw_id,
                numpublicaciones=int(num_pubs),
                nummiembros=int(num_users)
            )

            self.comunidadDAO.actualizar_o_insertar_comunidad(dto)
            self.db.commit()
            
            print(f"✅ Comunidad {id_comunidad} sincronizada | Pubs: {num_pubs} | Miembros: {num_users}")

            return {
                "id": raw_id,
                "numPublicaciones": num_pubs,
                "numMiembros": num_users
            }

        except Exception as e:
            print(f"❌ Error procesando comunidad: {e}")
            try:
                self.db.rollback()
            except:
                pass
            raise e
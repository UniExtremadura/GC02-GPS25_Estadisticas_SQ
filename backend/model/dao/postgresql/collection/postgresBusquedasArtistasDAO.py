from sqlalchemy import text
from backend.model.dto.busquedaArtistaDTO import BusquedaArtistaDTO
from backend.model.dao.interfaceBusquedasArtistasDao import InterfaceBusquedasArtistasDao

class BusquedasArtistasDAO(InterfaceBusquedasArtistasDao):
    def __init__(self, db):
        self.db = db

    def insertar_o_actualizar_busqueda(self, id_artista: int, id_usuario: int | None = None):
        """
        Registra una nueva búsqueda en el historial.
        Como es un log, siempre hacemos INSERT (no update).
        """
        try:
            # Simplemente insertamos una nueva fila con la fecha actual (NOW)
            sql_insert = text("""
                INSERT INTO busquedasartistas (idartista, idusuario, fecha)
                VALUES (:idartista, :idusuario, NOW())
            """)
            
            self.db.execute(sql_insert, {"idartista": id_artista, "idusuario": id_usuario})
            
            # El commit lo suele hacer el modelo, pero si aquí controlas la transacción:
            # self.db.commit() 
            
        except Exception as e:
            print(f"❌ Error DAO Registrando Búsqueda: {e}")
            self.db.rollback()
            raise e

    def get_top_artistas_busquedas(self, limit: int = 10) -> list[BusquedaArtistaDTO]:
            try:
                # MAGIA SQL: "WHERE fecha >= primer_dia_de_este_mes"
                # Esto hace que solo cuente las búsquedas del mes actual.
                sql = text("""
                    SELECT idartista, COUNT(*) AS num_busquedas
                    FROM busquedasartistas
                    WHERE fecha >= DATE_TRUNC('month', CURRENT_DATE)
                    GROUP BY idartista
                    ORDER BY num_busquedas DESC
                    LIMIT :limit
                """)
                
                rows = self.db.execute(sql, {"limit": limit}).fetchall()

                return [
                    BusquedaArtistaDTO(
                        idartista=r.idartista,
                        numBusquedas=r.num_busquedas
                    )
                    for r in rows
                ]
            except Exception as e:
                print(f"❌ Error DAO Top Busquedas: {e}")
                raise e

    def eliminar_busquedas_por_artista(self, id_artista: int) -> int:
        sql = text("DELETE FROM busquedasartistas WHERE idartista = :id")
        result = self.db.execute(sql, {"id": id_artista})
        return result.rowcount

    def eliminar_busquedas_por_usuario(self, id_usuario: int) -> int:
        sql = text("DELETE FROM busquedasartistas WHERE idusuario = :id")
        result = self.db.execute(sql, {"id": id_usuario})
        return result.rowcount
    
    def eliminar_todas_las_busquedas(self):
        """
        Borra todos los registros de búsquedas para iniciar un nuevo periodo.
        """
        try:
            # Opción A: DELETE (Borra las filas) - Ideal si es una tabla temporal mensual
            sql = text("DELETE FROM busquedasartistas")
            
            # Opción B: TRUNCATE (Más rápido y resetea IDs)
            # sql = text("TRUNCATE TABLE busquedasartistas RESTART IDENTITY")
            
            self.db.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print(f"❌ Error DAO Eliminando todas las búsquedas: {e}")
            self.db.rollback()
            raise e
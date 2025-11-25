from sqlalchemy import text
from backend.model.dao.interfaceComunidadesMensualesDao import InterfaceComunidadesMensualesDAO

class PostgresComunidadesMensualesDAO(InterfaceComunidadesMensualesDAO):
    def __init__(self, db):
        self.db = db

    def actualizar_o_insertar_comunidad(self, dto) -> bool:
        try:
            # 1. Comprobar si existe
            sql_check = text("SELECT idcomunidad FROM comunidadesmensual WHERE idcomunidad = :id")
            existe = self.db.execute(sql_check, {"id": dto.idComunidad}).fetchone()

            if existe:
                # 2. UPDATE
                sql_update = text("""
                    UPDATE comunidadesmensual
                    SET numpublicaciones = :np,
                        nummiembros = :nm
                    WHERE idcomunidad = :id
                """)
                self.db.execute(sql_update, {
                    "id": dto.idComunidad,
                    "np": dto.numPublicaciones,
                    "nm": dto.numMiembros
                })
            else:
                # 3. INSERT
                sql_insert = text("""
                    INSERT INTO comunidadesmensual (idcomunidad, numpublicaciones, nummiembros)
                    VALUES (:id, :np, :nm)
                """)
                self.db.execute(sql_insert, {
                    "id": dto.idComunidad,
                    "np": dto.numPublicaciones,
                    "nm": dto.numMiembros
                })
            
            return True

        except Exception as e:
            print(f"❌ Error DB DAO Comunidad: {e}")
            raise e
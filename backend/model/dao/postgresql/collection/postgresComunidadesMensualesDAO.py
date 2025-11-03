from sqlalchemy.orm import Session
from model.dto.comunidadMensualDTO import ComunidadMensual

class PostgresComunidadesMensualesDAO:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, id_comunidad: int):
        return self.db.query(ComunidadMensual).filter_by(idComunidad=id_comunidad).first()

    def upsert(self, id_comunidad: int, num_publicaciones: int, num_miembros: int):
        fila = self.obtener_por_id(id_comunidad)
        if fila:
            fila.numPublicaciones = num_publicaciones
            fila.numMiembros = num_miembros
        else:
            fila = ComunidadMensual(
                idComunidad=id_comunidad,
                numPublicaciones=num_publicaciones,
                numMiembros=num_miembros
            )
            self.db.add(fila)
        self.db.commit()
        self.db.refresh(fila)
        return fila

from sqlalchemy.orm import Session
from model.dto.contenidoMensualDTO import ContenidoMensual

class PostgresContenidosMensualesDAO:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, id_contenido: int):
        return self.db.query(ContenidoMensual).filter_by(idContenido=id_contenido).first()

    def upsert(self, id_contenido: int, es_album: bool, suma_val: float, num_val: int, num_com: int, num_rep: int):
        fila = self.obtener_por_id(id_contenido)
        if fila:
            fila.esAlbum = es_album
            fila.sumaValoraciones = suma_val
            fila.numValoraciones = num_val
            fila.numComentarios = num_com
            fila.numReproducciones = num_rep
        else:
            fila = ContenidoMensual(
                idContenido=id_contenido,
                esAlbum=es_album,
                sumaValoraciones=suma_val,
                numValoraciones=num_val,
                numComentarios=num_com,
                numReproducciones=num_rep
            )
            self.db.add(fila)
        self.db.commit()
        self.db.refresh(fila)
        return fila

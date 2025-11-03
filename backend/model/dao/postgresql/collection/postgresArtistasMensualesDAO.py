from sqlalchemy.orm import Session
from model.dto.artistaMensualDTO import ArtistaMensual
from model.dao.interfaceArtistasMensualesDao import InterfaceArtistasMensualesDao

class PostgresArtistasMensualesDAO(InterfaceArtistasMensualesDao):
    """
    Implementación concreta de la interfaz InterfaceArtistasMensualesDao
    para PostgreSQL usando SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, id_artista: int):
        return self.db.query(ArtistaMensual).filter_by(idArtista=id_artista).first()

    def listar_todos(self):
        return self.db.query(ArtistaMensual).all()

    def insertar(self, id_artista: int, num_oyentes: int, num_seguidores: int):
        nuevo = ArtistaMensual(
            idArtista=id_artista,
            numOyentes=num_oyentes,
            numSeguidores=num_seguidores
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar(self, id_artista: int, num_oyentes: int, num_seguidores: int):
        artista = self.db.query(ArtistaMensual).filter_by(idArtista=id_artista).first()
        if artista:
            artista.numOyentes = num_oyentes
            artista.numSeguidores = num_seguidores
            self.db.commit()
            self.db.refresh(artista)
            return artista
        return None

    def eliminar(self, id_artista: int):
        artista = self.db.query(ArtistaMensual).filter_by(idArtista=id_artista).first()
        if artista:
            self.db.delete(artista)
            self.db.commit()
            return True
        return False

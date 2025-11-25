from sqlalchemy.orm import Session
from backend.model.dao.postgresql.collection.postgresBusquedasArtistasDAO import BusquedasArtistasDAO
from backend.model.dao.postgresql.collection.postgresArtistasMensualesDAO import PostgresArtistasMensualesDAO
from backend.model.dao.postgresql.collection.postgresContenidoDAO import PostgresContenidoDAO
from backend.model.dao.postgresql.collection.postgesComunidadesMensualesDAO import PostgresComunidadesMensualesDAO

class DAOFactory:

    def __init__(self, db: Session):
        self.connector = db  # Usamos la sesión de base de datos de PostgreSQL
        self.busquedas_artistas_dao = BusquedasArtistasDAO(self.connector)
        self.artistas_mensuales_dao = PostgresArtistasMensualesDAO(self.connector)
        self.contenido_dao = PostgresContenidoDAO(self.connector)
        self.comunidad_dao = PostgresComunidadesMensualesDAO(self.connector)

    def get_artistas_mensuales_dao(self):
        return self.artistas_mensuales_dao

    def get_busquedas_artistas_dao(self):
        return self.busquedas_artistas_dao
    
    def get_contenido_dao(self):
        return self.contenido_dao
    
    def get_comunidad_dao(self):
        return self.comunidad_dao

    def close(self):
        """Cierra la conexión a la base de datos."""
        self.connector.close()  

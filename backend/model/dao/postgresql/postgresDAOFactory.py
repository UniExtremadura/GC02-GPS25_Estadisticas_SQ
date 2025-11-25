from backend.model.dao.postgresql.posgresConnector import PostgreSQLConnector
from backend.model.dao.postgresql.collection.postgresArtistasMensualesDAO import PostgresArtistasMensualesDAO
from backend.model.dao.postgresql.collection.postgresBusquedasArtistasDAO import BusquedasArtistasDAO
from backend.model.dao.postgresql.collection.postgresContenidoDAO import PostgresContenidoDAO
from backend.model.dao.postgresql.collection.postgesComunidadesMensualesDAO import PostgresComunidadesMensualesDAO

class PostgreSQLDAOFactory:

    def __init__(self):
        """Inicializa el conector a la base de datos PostgreSQL"""
        self.connector = PostgreSQLConnector()  # Usamos el conector para crear una conexión con la base de datos
        self.db = self.connector.get_db()  # SOLO UNA CONEXIÓN, que se reutiliza
        
    def get_artistas_mensuales_dao(self):
        return PostgresArtistasMensualesDAO(self.db)
    
    def get_busquedas_artistas_dao(self):
        return BusquedasArtistasDAO(self.db)
    
    def get_contenido_dao(self):
        return PostgresContenidoDAO(self.db)
    
    def get_comunidad_dao(self):
        return PostgresComunidadesMensualesDAO(self.db)



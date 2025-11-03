from model.dao.postgresql.collection.postgresArtistasMensualesDAO import PostgresArtistasMensualesDAO
from model.dao.postgresql.collection.postgresComunidadesMensualesDAO import PostgresComunidadesMensualesDAO
from model.dao.postgresql.collection.postgresContenidosMensualesDAO import PostgresContenidosMensualesDAO
from model.dao.postgresql.posgresConnector import PostgreSQLConnector

class PostgreSQLDAOFactory:
    def __init__(self):
        self.connector = PostgreSQLConnector()
        self.db_session = self.connector.get_session()

    def get_artistas_mensuales_dao(self):
        return PostgresArtistasMensualesDAO(self.db_session)

    def get_comunidades_mensuales_dao(self):
        return PostgresComunidadesMensualesDAO(self.db_session)

    def get_contenidos_mensuales_dao(self):
        return PostgresContenidosMensualesDAO(self.db_session)

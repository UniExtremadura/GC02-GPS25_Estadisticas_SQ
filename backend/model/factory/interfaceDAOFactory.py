from model.dao.estadisticasDAO import EstadisticasDAO

class DAOFactory:
    """
    Clase factoría para obtener los objetos DAO necesarios.
    Centraliza la creación de instancias de acceso a datos.
    """

    @staticmethod
    def get_estadisticas_dao(db_session):
        """
        Devuelve una instancia del DAO de estadísticas.
        """
        return EstadisticasDAO(db_session)

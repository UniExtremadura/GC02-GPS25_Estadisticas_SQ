from abc import ABC, abstractmethod

class InterfaceArtistasMensualesDao(ABC):
    """
    Interfaz que define los métodos que debe implementar cualquier
    DAO encargado de gestionar los datos de artistas mensuales.
    """

    @abstractmethod
    def obtener_por_id(self, id_artista: int):
        """Devuelve el artista mensual con el ID especificado."""
        pass

    @abstractmethod
    def listar_todos(self):
        """Devuelve la lista de todos los artistas mensuales."""
        pass

    @abstractmethod
    def insertar(self, id_artista: int, num_oyentes: int, num_seguidores: int):
        """Inserta un nuevo registro de artista mensual."""
        pass

    @abstractmethod
    def actualizar(self, id_artista: int, num_oyentes: int, num_seguidores: int):
        """Actualiza un registro existente de artista mensual."""
        pass

    @abstractmethod
    def eliminar(self, id_artista: int):
        """Elimina un artista mensual por ID."""
        pass

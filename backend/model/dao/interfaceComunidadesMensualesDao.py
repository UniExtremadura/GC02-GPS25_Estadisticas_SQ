from abc import ABC, abstractmethod
from typing import List, Optional
from backend.model.dto.comunidadMensualDTO import ComunidadDTO


class InterfaceComunidadesMensualesDAO(ABC):
    """
    Interfaz para la gestión de comunidades mensuales.
    """
    @abstractmethod
    def actualizar_o_insertar_comunidad(self, dto) -> bool:
        """Inserta o actualiza una comunidad mensual."""
        pass 


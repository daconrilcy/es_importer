from typing import Dict, Any, Optional
import logging

from config import Config
from models.mapping_management.fields_management import FieldsManager

logger = logging.getLogger(__name__)


class Mapping:
    """
    Représente un mapping complet, incluant un nom, une entité liée,
    et un ensemble de champs instanciés via un FieldsManager.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None, config: Optional[Config] = None) -> None:
        """
        Initialise un objet Mapping à partir d'un dictionnaire JSON.

        :param data: Dictionnaire représentant le mapping complet.
        :param config: Configuration optionnelle.
        """
        data = data or {}
        self._config: Config = config or Config()

        self._mapping_name: str = data.get("mapping_name", "")
        self._related_to: str = data.get("related_to", "")
        self._fields: Dict[str, Any] = {}

        self._initialize_fields(data)

    def _initialize_fields(self, data: Dict[str, Any]) -> None:
        """
        Initialise les champs à partir des données fournies.
        """
        if not data:
            return
        if not isinstance(data, dict):
            logger.error("Invalid data type for Mapping initialization: %s", type(data))
            return

        manager = FieldsManager(data, self._config)
        self._fields = manager.fields

    def __repr__(self) -> str:
        return (
            f"<Mapping name={self._mapping_name}, related_to={self._related_to}, "
            f"fields={list(self._fields.keys())}>"
        )

    # --- GETTERS ---
    @property
    def mapping_name(self) -> str:
        """Retourne le nom du mapping."""
        return self._mapping_name

    @property
    def related_to(self) -> str:
        """Retourne l'entité liée au mapping."""
        return self._related_to

    @property
    def fields(self) -> Dict[str, Any]:
        """Retourne le dictionnaire des champs instanciés."""
        return self._fields

    # --- SETTERS ---
    @mapping_name.setter
    def mapping_name(self, value: str) -> None:
        """Définit le nom du mapping."""
        self._mapping_name = value

    @related_to.setter
    def related_to(self, value: str) -> None:
        """Définit l'entité liée au mapping."""
        self._related_to = value

    @fields.setter
    def fields(self, new_fields: Dict[str, Any]) -> None:
        """Met à jour les champs via le FieldsManager."""
        self._initialize_fields(new_fields)

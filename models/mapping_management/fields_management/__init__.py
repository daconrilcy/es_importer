from typing import Dict, Any, Optional, Type

from config import Config
import logging

from models.mapping_management.fields_management.phonetic import PhoneticField
from models.mapping_management.fields_management.remplacement import ReplacementField
from models.mapping_management.fields_management.source_fields import MappingSourceField

logger = logging.getLogger(__name__)

FieldClassType = Type["BaseMappingField"]


class FieldsManager:
    """
    Gère la création des champs de mapping à partir d'un dictionnaire de configuration.
    """

    FIELD_CLASS_MAP: Dict[str, FieldClassType] = {
        "source_field": MappingSourceField,
        "phonetic": PhoneticField,
        "remplacement_fields": ReplacementField,
    }

    def __init__(self, mapping: Dict[str, Dict[Any]], config: Optional[Config] = None) -> None:
        """
        Initialise le gestionnaire de champs à partir du mapping brut.

        :param mapping: Dictionnaire de configuration du mapping.
        :param config: Configuration optionnelle.
        """
        self._config: Config = config or Config()
        self._fields: Dict[str, Any] = {}
        self._initialize_fields(mapping)

    def _initialize_fields(self, mapping: Dict[str, Dict[Any]]) -> None:
        """
        Valide et instancie les champs à partir du mapping brut.

        :param mapping: Dictionnaire contenant une clé 'mapping' avec les champs.
        """
        if not isinstance(mapping, dict):
            logger.error("Invalid mapping data: %s", mapping)
            return

        raw_fields = mapping.get("mapping")
        if not isinstance(raw_fields, dict):
            logger.error("Invalid or missing 'mapping' key in data: %s", mapping)
            return

        for key, field_data in raw_fields.items():
            self._add_field(key, field_data)

    def _add_field(self, key: str, field_data: Dict[str, Any]) -> None:
        """
        Ajoute un champ au gestionnaire à partir de sa configuration.

        :param key: Nom du champ.
        :param field_data: Dictionnaire de configuration du champ.
        """
        if not isinstance(field_data, dict):
            logger.error("Invalid field data (not a dict): %s", field_data)
            return

        category = field_data.get("category")
        if not category:
            logger.error("Missing category in field data: %s", field_data)
            return

        field_class = self.FIELD_CLASS_MAP.get(category)
        if not field_class:
            logger.error("Unknown field category: %s", category)
            return

        try:
            self._fields[key] = field_class(key, field_data, self._config)
        except ValueError as e:
            logger.error("Error creating field [%s]: %s", key, e)

    @property
    def fields(self) -> Dict[str, Any]:
        """
        Retourne les champs instanciés.

        :return: Dictionnaire des champs.
        """
        return self._fields

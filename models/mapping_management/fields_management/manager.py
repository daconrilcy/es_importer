from typing import Dict, Any, Optional, Type, Union

from config import Config
import logging

from models.mapping_management.fields_management.fixed import FixedValueMappingField
from models.mapping_management.fields_management.phonetic import PhoneticField
from models.mapping_management.fields_management.remplacement import ReplacementField
from models.mapping_management.fields_management.source import MappingSourceField

logger = logging.getLogger(__name__)

FieldClassType = Type["BaseMappingField"]


class FieldsManager:
    """
    Gère la création des champs de mapping à partir d'un dictionnaire de configuration.
    """

    FIELD_CLASS_MAP: Dict[str, FieldClassType] = {
        "source": MappingSourceField,
        "phonetic": PhoneticField,
        "remplacement": ReplacementField,
        "fixed_value": FixedValueMappingField
    }

    def __init__(self, mapping: Dict[str, Union[str, Dict[str, Any]]], config: Optional[Config] = None) -> None:
        """
        Initialise le gestionnaire de champs à partir du mapping brut.

        :param mapping: Dictionnaire de configuration du mapping.
        :param config: Configuration optionnelle.
        """
        self._config: Config = config or Config()
        self._fields: Dict[str, Any] = {}
        self._initialize_fields(mapping)

    def _initialize_fields(self, mapping: Dict[str, Union[str, Dict[str, Any]]]) -> None:
        """
        Valide et instancie les champs à partir du mapping brut.

        :param mapping: Dictionnaire contenant une clé 'mapping' avec les champs.
        """
        if not isinstance(mapping, dict):
            logger.error("FieldsManager: Invalid mapping data: %s", mapping)
            return

        raw_fields = mapping.get("mapping")
        if not isinstance(raw_fields, dict):
            print(f"raw_fields := {raw_fields}")
            logger.error("FieldsManager: Invalid or missing 'mapping' key in data: %s", mapping)
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
            logger.error("FieldsManager : Invalid field data (not a dict): %s", field_data)
            return

        category = field_data.get("category")
        if not category:
            logger.error("FieldsManager : Missing category in field data: %s", field_data)
            return

        if category not in self.FIELD_CLASS_MAP:
            logger.error("FieldsManager : Unknown category: %s", category)
            return

        field_class = self.FIELD_CLASS_MAP[category]
        field = field_class(key, field_data, self._config)
        self._fields[key] = field

    @property
    def fields(self) -> Dict[str, Any]:
        """
        Retourne les champs instanciés.

        :return: Dictionnaire des champs.
        """
        return self._fields


if __name__ == "__main__":
    mapping_test_data = {
        "related_to": "curiexplore-pays.csv",
        "mapping": {
            "iso2": {
                "category": "source",
                "source_field": "iso2",
                "description": "Code ISO alpha-2 du pays",
                "mapped": True,
                "type": "keyword",
                "analyzer": None,
            },
            "iso3": {
                "category": "source",
                "source_field": "iso3",
                "description": "Code ISO alpha-3 du pays",
                "mapped": True,
                "type": "keyword",
                "analyzer": None,
            },
            "country_name": {
                "category": "fixed_value",
                "description": "Nom du pays",
                "value": "France"
            },
            "flag": {
                "category": "source",
                "source_field": "flag",
                "name": "flag",
                "type": "text",
                "mapped": True,
                "analyzer": "standard",
                "description": "URL de l'image du drapeau du pays"
            }
        }
    }

    fields_manager_test = FieldsManager(mapping_test_data)
    print(fields_manager_test.fields)

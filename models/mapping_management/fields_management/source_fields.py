from typing import Any

from config import Config
from models.mapping_management.fields_management.base import BaseMappingField
import logging

logger = logging.getLogger(__name__)


class MappingSourceField(BaseMappingField):
    """
    Représente un champ de mapping pour un index Elasticsearch ou un fichier de configuration.
    Permet d'encapsuler les propriétés liées à ce champ et d'y accéder proprement via des getters/setters.
    """

    def __init__(self, name: str, data: dict, config: Config = None):
        """
        Initialise le champ à partir d'un nom et d'un dictionnaire de données.

        :param data: Dictionnaire contenant les propriétés du champ.
        """
        config = config or Config()
        super().__init__(name, data, config)
        self._source_field: str = None
        self._mapped: bool = False
        self._type: str = None
        self._analyzer: str = None
        self._fixed_value: bool = False
        self._value: Any = None
        self._set(data)

    def _set(self, data: dict):
        if self.category != "source_field":
            raise ValueError("SourceField : Le champ 'category' doit avoir la valeur 'source_field'.")
        self.source_field = data.get("source_field")
        self.mapped = data.get("mapped", False)
        self.type = data.get("type")
        self.analyzer = data.get("analyzer")
        self.fixed_value = data.get("fixed_value", False)
        self.value = data.get("value", None)

    def __repr__(self):
        return (f"<MappingField name={self._name}, category={self._category}, source_field={self._source_field}, "
                f"description={self._description}, type={self._type}, mapped={self._mapped}>")

    # --- GETTERS ---
    @property
    def source_field(self) -> str:
        """Champ source d'où provient la donnée."""
        return self._source_field

    @property
    def mapped(self) -> bool:
        """Indique si le champ est effectivement mappé."""
        return self._mapped

    @property
    def type(self) -> str:
        """Type de champ (ex : 'keyword', 'text', etc.)."""
        return self._type

    @property
    def analyzer(self) -> str:
        """Nom de l’analyseur à utiliser (si applicable)."""
        return self._analyzer

    @property
    def fixed_value(self) -> bool:
        """Indique si le champ utilise une valeur fixe."""
        return self._fixed_value

    @property
    def value(self):
        """Valeur fixe définie pour le champ (si fixed_value=True)."""
        return self._value

    # --- SETTERS ---
    @source_field.setter
    def source_field(self, value: str):
        self._source_field = value

    @mapped.setter
    def mapped(self, value: bool):
        self._mapped = value

    @type.setter
    def type(self, value: str):
        self._type = value

    @analyzer.setter
    def analyzer(self, value: str):
        self._analyzer = value

    @fixed_value.setter
    def fixed_value(self, value: bool):
        self._fixed_value = value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def dict(self):
        """Retourne un dictionnaire contenant les propriétés du champ."""
        base_dict = super().dict
        base_dict["source_field"] = self.source_field
        base_dict["mapped"] = self.mapped
        base_dict["type"] = self.type
        base_dict["analyzer"] = self.analyzer
        base_dict["fixed_value"] = self.fixed_value
        base_dict["value"] = self.value
        return base_dict

    def __str__(self):
        return self.dict.__str__()
from typing import Optional, Any
from models.elastic_specifiques import EsFieldType
from models.elastic_specifiques.collection import EsTypes


class ModelField:
    """
    Représente un champ Elasticsearch avec un nom, un type, une valeur et une description.
    Permet également de convertir le champ en dictionnaire ou en affichage texte.
    """

    def __init__(self, field_name: Optional[str] = None,
                 field_type: Optional[EsFieldType | str] = None,
                 value: Optional[Any] = None,
                 description: Optional[str] = None):
        """
        Initialise le champ avec les métadonnées principales.
        """
        self._es_types = EsTypes()
        self._excluded_keys = ["_config", "_excluded_keys", "excluded_keys", "_es_types", "es_types",
                               "_dict", "dict", "_keys", "keys", "type"]
        self._field_name: str = ""
        self._value = value
        self._description = description
        self._dict = {}
        self._keys = None

        self.field_name = field_name
        self.type = field_type

    @property
    def field_name(self) -> str:
        """Retourne le nom du champ."""
        return self._field_name

    @field_name.setter
    def field_name(self, field_name: Optional[str]):
        """Définit le nom du champ (ou 'unknown_field' si invalide)."""
        if not isinstance(field_name, str) or not field_name:
            field_name = "unknown_field"
        self._field_name = field_name

    @property
    def type(self) -> EsFieldType:
        """Retourne le type du champ."""
        return self._type

    @type.setter
    def type(self, field_type: EsFieldType | str):
        """
        Définit le type du champ à partir d'une chaîne ou d'une instance EsFieldType.
        Défaut : "text".
        """
        if not field_type:
            field_type = "text"
        if isinstance(field_type, str):
            field_type = self._es_types.get_type(field_type)
        if not isinstance(field_type, EsFieldType):
            field_type = self._es_types.get_type("text")
        self._type = field_type

    @property
    def type_name(self) -> str:
        """Retourne le nom du type Elasticsearch."""
        return self._type.name if isinstance(self._type, EsFieldType) else "unknown"

    @property
    def value(self) -> Any:
        """Retourne la valeur du champ."""
        return self._value

    @value.setter
    def value(self, value: Any):
        """Définit la valeur du champ."""
        self._value = value

    @property
    def description(self) -> Optional[str]:
        """Retourne la description du champ."""
        return self._description

    @description.setter
    def description(self, description: Optional[str]):
        """Définit la description du champ."""
        self._description = description

    @property
    def keys(self) -> list:
        """Retourne la liste des attributs accessibles en dictionnaire."""
        if self._keys is None:
            self._set_keys()
        return self._keys

    @keys.setter
    def keys(self, keys_to_add: list[str]):
        """Définit manuellement les clés accessibles (rarement utilisé)."""
        if not isinstance(keys_to_add, list):
            self._set_keys()
            return
        self._keys = keys_to_add

    @property
    def excluded_keys(self) -> list:
        """Retourne la liste des attributs exclus du dict."""
        return self._excluded_keys

    def _set_keys(self):
        """Identifie uniquement les attributs privés sans propriétés."""
        self._keys = [
            attr.lstrip("_") for attr in self.__dict__
            if not callable(getattr(self, attr))
        ]

    @property
    def dict(self) -> dict:
        """
        Retourne un dictionnaire des attributs du champ,
        en excluant les attributs vides ou ignorés.
        """
        result = {}
        for key in self.keys:
            if key in self._excluded_keys:
                continue
            value = getattr(self, key)
            if isinstance(value, str) and not value:
                continue
            if isinstance(value, list) and not value:
                continue
            if isinstance(value, EsFieldType):
                value = value.name
            result[key] = value
        self._dict = result
        return result

    @dict.setter
    def dict(self, data: Optional[dict]):
        """
        Initialise un champ à partir d’un dictionnaire.
        Ignore les clés non reconnues.
        """
        if not isinstance(data, dict):
            print("❌ ModelField.dict: data is not a dict")
            return
        for key in data:
            if key in self.keys:
                setattr(self, key, data[key])
            else:
                print(f"❌ ModelField.dict: key {key} not in keys")
        self._dict = data

    @property
    def base_dict(self) -> dict:
        """
        Retourne un dictionnaire standardisé contenant les infos principales.
        """
        return {
            "field_name": self.field_name,
            "type": self.type.name,
            "value": self.value,
            "description": self.description,
        }

    @base_dict.setter
    def base_dict(self, base_dict: dict):
        """
        Initialise les métadonnées à partir d’un dictionnaire simple.
        """
        if not isinstance(base_dict, dict):
            print("❌ ModelField.base_dict: base_dict is not a dict")
            return
        self.field_name = base_dict.get("field_name")
        self.type = base_dict.get("type")
        self.value = base_dict.get("value")
        self.description = base_dict.get("description")

    def __str__(self):
        """
        Retourne une chaîne lisible du champ, avec ses attributs principaux.
        """
        parts = []
        for key in self.keys:
            if key in self._excluded_keys:
                continue
            value = getattr(self, key)
            if isinstance(value, str) and not value:
                continue
            if isinstance(value, list) and not value:
                continue
            parts.append(f"{key}: {value}")
        parts.append(f"type: {self.type_name}")
        return f"ModelField({', '.join(parts)})"


if __name__ == "__main__":
    # Example usage
    field = ModelField(field_name="example_field", field_type="text", value="example_value")
    print(field.base_dict)
    field.dict = {"field_name": "new_field", "type": "keyword", "value": "new_value"}
    print(field)
    print(field.type_name)

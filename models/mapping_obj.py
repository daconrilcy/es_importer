from config import Config
from utils import manage_filepath, get_csv_headers


class MappingField:
    """
    Représente un champ de mapping pour un fichier Elasticsearch.
    """

    def __init__(self, config: Config = None):
        self._config = config or Config()
        self._field_name = None
        self._source_field_name = None
        self._type_field = None
        self._analyzer = None
        self._mapped = True
        self._description = None
        self._fixed = False
        self._value = None
        self._keys = None
        self._excluded_keys = ["_config", "_excluded_keys"]
        self._set_keys()

    # Propriétés avec getter/setter pour encapsulation propre
    @property
    def field_name(self) -> str:
        """Nom du champ Elasticsearch."""
        return self._field_name

    @field_name.setter
    def field_name(self, value: str):
        self._field_name = value

    @property
    def source_field_name(self) -> str:
        """Nom du champ source dans le fichier d’origine."""
        return self._source_field_name

    @source_field_name.setter
    def source_field_name(self, value: str):
        self._source_field_name = value

    @property
    def type_field(self) -> str:
        """Type Elasticsearch (text, keyword, geo_point...)."""
        return self._type_field

    @type_field.setter
    def type_field(self, value: str):
        self._type_field = value

    @property
    def analyzer(self) -> str:
        """Analyseur utilisé (english, french...)."""
        return self._analyzer

    @analyzer.setter
    def analyzer(self, value: str):
        self._analyzer = value

    @property
    def mapped(self) -> bool:
        """Champ mappé ou non dans Elasticsearch."""
        return self._mapped

    @mapped.setter
    def mapped(self, value: bool):
        self._mapped = value

    @property
    def description(self) -> str:
        """Description humaine du champ."""
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def fixed(self) -> bool:
        """Champ à valeur fixe ou dynamique."""
        return self._fixed

    @fixed.setter
    def fixed(self, value: bool):
        self._fixed = value

    @property
    def value(self) -> str:
        """Valeur fixe, si définie."""
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def keys(self) -> list[str]:
        """Clé(s) du champ, si définie."""
        return self._keys

    @keys.setter
    def keys(self, value: list[str]):
        self._keys = value

    def _set_keys(self):
        """
        Définit les clés du champ à partir d'une chaîne de caractères.
        """
        self.keys = []
        for attr in self.__dict__:
            clean_attr = attr.lstrip("_")
            if attr in self._excluded_keys or clean_attr in self._excluded_keys:
                continue
            self.keys.append(clean_attr)

    def from_dict(self, field_name: str, data: dict) -> 'MappingField':
        """
        Initialise un champ à partir d’un dictionnaire JSON.
        :param field_name: nom du champ (clé)
        :param data: données associées
        :return: instance de MappingField
        """
        self.field_name = field_name
        self.source_field_name = data.get("source_field")
        self.description = data.get("description")
        self.mapped = data.get("mapped", True)
        self.type_field = data.get("type")
        self.analyzer = data.get("analyzer")
        self.fixed = data.get("fixed_value", False)
        self.value = data.get("value")
        return self

    def __str__(self):
        """
        Représentation sous forme de chaîne de caractères.
        :return: Chaîne de caractères représentant le champ
        """
        return (f"MappingField(field_name={self.field_name}, source_field_name={self.source_field_name}, "
                f"type_field={self.type_field})")


import json
import os
from datetime import datetime
from config import Config
from typing import Optional


class MappingSchema:
    """
    Classe représentant un schéma de mapping pour un fichier Elasticsearch.
    Contient plusieurs champs de type MappingField et permet de les charger, valider,
    convertir en JSON ou sauvegarder/charger depuis un fichier.
    """

    def __init__(self, related_to: Optional[str] = None,
                 file_type: Optional[str] = "mappings",
                 es_id: Optional[str] = None,
                 front_name: Optional[str] = None,
                 config: Optional[Config] = None):
        """
        Initialise un nouveau schéma de mapping.
        :param related_to: fichier source auquel ce mapping est lié (ex : CSV)
        :param front_name: nom du mapping
        :param config: configuration globale (contient dossier de sauvegarde)
        """
        self.config = config or Config()
        self._id = es_id
        self._file_type = file_type
        self._related_to = related_to
        self._front_name = front_name
        self._filename = None
        self.fields = {}  # Clé = nom du champ, valeur = instance de MappingField
        self.folder_path = self.config.mapping_folder
        self._created_at = None

    # Propriété : nom du fichier associé au mapping
    @property
    def filename(self) -> str:
        """
        Nom du fichier de mapping.
        :return:
        """
        return self._filename or (self.front_name + ".json" if self.front_name else "mapping.json")

    @filename.setter
    def filename(self, value: str):
        if not value.endswith(".json"):
            value += ".json"
        self._filename = value

    @property
    def id(self) -> str:
        """
        Identifiant Elasticsearch du mapping.
        :return:
        """
        return self._id

    @id.setter
    def id(self, es_id: str):
        """
        Définit l'identifiant Elasticsearch du mapping.
        :param es_id: Identifiant Elasticsearch
        """
        if es_id is None or es_id == "":
            print(f"❌ MappingSchema.id : id est vide")
            return
        self._id = es_id

    @property
    def front_name(self) -> str:
        """
        Nom du mapping.
        :return: str
        """
        return self._front_name

    @front_name.setter
    def front_name(self, value: str):
        self._front_name = value

    @property
    def related_to(self) -> str:
        """
        Nom du fichier source auquel ce mapping est lié (ex : pays.csv).
        :return:
        """
        return self._related_to

    @related_to.setter
    def related_to(self, file_name: str):
        self._related_to = file_name

    @property
    def created_at(self) -> str:
        """
        Date de création du mapping.
        :return:
        """
        return self._created_at

    @created_at.setter
    def created_at(self, date: str | datetime):
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d %H:%M:%S")
        self._created_at = date

    @property
    def file_type(self) -> str:
        """
        Type de fichier associé au mapping (ex : CSV, JSON).
        :return:
        """
        return self._file_type

    @file_type.setter
    def file_type(self, value: str):
        """
        Définit le type de fichier associé au mapping.
        :param value: Type de fichier (ex : CSV, JSON)
        """
        self._file_type = value

    def load_from_json(self, json_data: dict, name: Optional[str] = None):
        """
        Charge les champs de mapping depuis un objet JSON.
        :param json_data: Dictionnaire issu d'un fichier JSON
        :param name: nom du mapping (optionnel)
        """
        self.front_name = name or json_data["mapping_name"]
        self.related_to = json_data.get("related_to")
        for field_name, field_info in json_data.get("mapping", {}).items():
            field = MappingField().from_dict(field_name, field_info)
            self.fields[field_name] = field

    def to_json(self) -> dict:
        """
        Convertit l'objet MappingSchema en dictionnaire JSON exportable.
        :return: Dictionnaire contenant les données du mapping
        """
        return {
            "related_to": self.related_to,
            "mapping_name": self.front_name,
            "mapping": {
                name: {
                    "source_field": field.source_field_name,
                    "description": field.description,
                    "mapped": field.mapped,
                    "type": field.type_field,
                    "analyzer": field.analyzer,
                    "fixed_value": field.fixed,
                    "value": field.value
                } for name, field in self.fields.items()
            }
        }

    def to_web_json(self) -> dict:
        """
        Convertit l'objet MappingSchema en dictionnaire JSON pour une utilisation web.
        :return:
        """
        dict_data = self.to_json()
        dict_data["created_at"] = self.created_at
        dict_data["filename"] = self.filename

        return dict_data

    def save_to_file(self, filename: Optional[str] = None) -> bool:
        """
        Sauvegarde le mapping dans un fichier JSON sur disque.
        :param filename: Nom du fichier de sortie (optionnel)
        :return: True si succès, False sinon
        """
        self.filename = filename or self.filename
        file_path = os.path.join(self.folder_path, self.filename)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.to_json(), file, indent=4)  # type: ignore[arg-type]
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {file_path} → {e}")
            return False

    def load_from_filename(self, filename: Optional[str] = None) -> bool:
        """
        Charge un fichier JSON de mapping et initialise l'objet.
        :param filename: Nom du fichier à charger
        :return: True si succès, False sinon
        """
        self.filename = filename or self.filename
        file_path = os.path.join(self.folder_path, self.filename)

        try:
            with open(file_path, encoding="utf-8") as file:
                json_data = json.load(file)
                self.load_from_json(json_data)

            # Tente de récupérer la date de création du fichier (si dispo)
            try:
                timestamp = os.path.getctime(file_path)
                self.created_at = datetime.fromtimestamp(timestamp)
            except  (OSError, ValueError) as e:
                print(f"❌ MappingSchema.load_from_file : Erreur lors de la récupération de la date de création : {e}")
                self.created_at = datetime.now()
            return True
        except FileNotFoundError:
            print(f"❌ Fichier introuvable : {file_path}")
            return False

    def validate(self) -> list[str]:
        """
        Valide la structure du mapping.
        :return: liste des erreurs trouvées (vide si tout est OK)
        """
        errors = []

        # Vérifie que le mapping est bien lié à un fichier source
        if not self.related_to:
            errors.append("Le champ 'related_to' est obligatoire.")

        # Vérifie chaque champ individuellement
        for field_name, field in self.fields.items():
            if not field.source_field_name:
                errors.append(f"[{field_name}] → 'source_field' manquant.")
            if not field.type_field:
                errors.append(f"[{field_name}] → 'type' manquant.")

        return errors

    def get_missing_fields(self) -> list[str]:
        """
        Liste les champs source manquants dans le mapping.
        :return:
        """
        from models.file_infos import FileInfos
        file_path = manage_filepath(self.config.data_folder, self.related_to)
        if not os.path.isfile(file_path):
            print(f"❌ Fichier source introuvable : {file_path}")
            return []
        missing_fields = []
        fi = FileInfos(file_path)
        try:
            total_list_source_fields = get_csv_headers(file_path, fi.separator)
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des champs source : {e}")
            return []
        listed_fields = self.get_fields_source_names()
        for field in total_list_source_fields:
            if field not in listed_fields:
                missing_fields.append(field)
        return missing_fields

    def get_fields_source_names(self) -> list[str]:
        """
        Récupère la liste des noms de champs source.
        :return: Liste des noms de champs source
        """
        return [field.source_field_name for field in self.fields.values()]

    def __str__(self):
        """
        Représentation sous forme de chaîne de caractères.
        :return: Chaîne de caractères représentant le mapping
        """
        str_fields = ", ".join([f"{name}: {field}" for name, field in self.fields.items()])
        return (f"MappingSchema(related_to={self.related_to}, name={self.front_name}, "
                f"fields={str_fields}")


if __name__ == "__main__":
    # Exemple d'utilisation
    mapping = MappingSchema()
    mapping.load_from_filename("mapping_pays.json")
    print(mapping.to_json())
    mapping.name = "mapping pays (copy)"
    mapping.save_to_file("mapping_pays_copy.json")
    print(mapping.validate())
    print(mapping.to_web_json())

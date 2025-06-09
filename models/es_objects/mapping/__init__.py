import json
import os
from datetime import datetime
from typing import Optional

from config import Config
from utils import get_csv_headers, manage_filepath
from models.es_objects.mapping.field import MappingField
from models.es_objects._base_obj import BaseObject


class EsMapping(BaseObject):
    """
    Représente un schéma de mapping Elasticsearch, composé de plusieurs champs.
    Hérite de BaseObject.
    """

    def __init__(self,
                 es_id: Optional[str] = None,
                 filepath: Optional[str] = None,
                 filename: Optional[str] = None,
                 front_name: Optional[str] = None,
                 description: Optional[str] = None,
                 created_at: Optional[str | datetime] = None,
                 related_to: Optional[str] = None,
                 fields: Optional[dict] = None,
                 config: Optional[Config] = None):

        super().__init__(es_id=es_id, filepath=filepath, filename=filename,
                         front_name=front_name, description=description,
                         created_at=created_at, fields=fields)
        config = config or Config()
        self.index_name = config.index_files_name
        self.file_type = self.fileTypes.mappings
        self.related_to = related_to
        self._data_folder = config.data_folder

    @property
    def related_to(self) -> str:
        """Fichier source lié au mapping."""
        return self._related_to

    @related_to.setter
    def related_to(self, value: str):
        self._related_to = value

    def field_by_name(self, field_name: str) -> dict:
        """
        Retourne un champ par son nom.
        :param field_name: Nom du champ
        :return: dict
        """
        if field_name not in self.fields:
            print(f"❌ Champ '{field_name}' introuvable dans le mapping.")
            return None
        return self.fields[field_name]

    def add_field(self, field_to_add: dict, name: Optional[str] = None) -> bool:
        """
        Ajoute un champ au mapping.
        :param field_to_add: Dictionnaire de champs
        :param name: Nom du champ
        :return: bool
        """
        if not isinstance(field_to_add, dict):
            print("❌ add_field : l'entrée n'est pas un dictionnaire")
            return False

        if name is None:
            name = field_to_add.get("source_field_name")
            if not name:
                print("❌ add_field : le nom du champ est manquant")
                return False

        self.fields[name] = MappingField().dict(field_to_add)

        return True

    def load_from_json(self, json_string: str) -> bool:
        """
        Transforme une chaîne JSON en dictionnaire Python.
        :param json_string: Chaîne JSON valide
        :return: dict si succès, None sinon
        """
        if not isinstance(json_string, str):
            print("❌ json_to_dict : l'entrée n'est pas une chaîne de caractères")
            return False

        try:
            self.dict = json.loads(json_string)
            return True
        except json.JSONDecodeError as e:
            print(f"❌ json_to_dict : erreur de parsing JSON → {e}")
            return False

    @property
    def dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire JSON exportable.
        :return: dict
        """
        base_dict = self.base_dict
        base_dict["related_to"] = self.related_to
        base_dict["mapping_name"] = self.front_name
        base_dict["mapping"] = {
            name: field_obj.dict for name, field_obj in self.fields.items()
        }
        return base_dict

    @dict.setter
    def dict(self, data: dict):
        """
        Initialise l'objet à partir d'un dictionnaire JSON.
        :param data: Dictionnaire JSON
        :return: bool
        """
        if not data:
            print("❌ EsMapping.dict: data is None")
            return
        if not isinstance(data, dict):
            print("❌ EsMapping.dict: data is not a dict")
            return
        if not data.get("mapping_name"):
            print("❌ EsMapping.dict: mapping_name is None")
            return
        if not data.get("mapping"):
            print("❌ EsMapping.dict: mapping is None")
            return
        if not data.get("related_to"):
            print("❌ EsMapping.dict: related_to is None")
            return
        if not isinstance(data.get("mapping"), dict) or not isinstance(data.get("mapping"), list):
            print("❌ EsMapping.dict: mapping is not a dict or list")
            return

        self.base_dict = data
        self.related_to = data.get("related_to", None)
        self.front_name = data.get("mapping_name", None)
        self.fields = {name: MappingField().dict(field_data)
                       for name, field_data in data.get("mapping", {}).items()}

    @property
    def fields_dict(self) -> dict:
        """
        Retourne le dictionnaire de champs.
        :return: dict
        """
        return {name: field_obj.dict for name, field_obj in self.fields.items()}

    @property
    def dict_file(self) -> dict:
        """
        Convertit l'objet en dictionnaire JSON exportable.
        :return: dict
        """
        return {
            "related_to": self.related_to,
            "mapping_name": self.front_name,
            "mapping": {
                name: {
                    "source_field": field_obj.source_field_name,
                    "description": field_obj.description,
                    "mapped": field_obj.mapped,
                    "type": field_obj.type_field,
                    "analyzer": field_obj.analyzer,
                    "fixed_value": field_obj.fixed,
                    "value": field_obj.value
                } for name, field_obj in self.fields.items()
            }
        }

    def validate(self) -> list[str]:
        """
        Valide le contenu du mapping.
        :return: liste d'erreurs
        """
        errors = []
        if not self.related_to:
            errors.append("Le champ 'related_to' est obligatoire.")

        for field_name, obj_field in self.fields.items():
            if not obj_field.source_field_name:
                errors.append(f"[{field_name}] → 'source_field' manquant.")
            if not obj_field.type_field:
                errors.append(f"[{field_name}] → 'type' manquant.")
        return errors

    @property
    def get_missing_fields(self) -> list[str]:
        """
        Liste les champs manquants dans le fichier source.
        :return: Liste de noms de champs
        """
        from models.file_infos import FileInfos
        file_path = manage_filepath(self._data_folder, self.related_to)
        if not os.path.isfile(file_path):
            print(f"❌ Fichier source introuvable : {file_path}")
            return []

        missing_fields = []
        fi = FileInfos(file_path)
        try:
            total_list_source_fields = get_csv_headers(file_path, fi.separator)
        except Exception as e:
            print(f"❌ Erreur lecture CSV : {e}")
            return []

        listed_fields = self.get_fields_source_names
        for obj_field in total_list_source_fields:
            if obj_field not in listed_fields:
                missing_fields.append(obj_field)
        return missing_fields

    @property
    def get_fields_source_names(self) -> list[str]:
        """
        Retourne la liste des noms de champs source mappés.
        :return: List[str]
        """
        return [obj_field.source_field_name for obj_field in self.fields.values()]

    def __str__(self):
        """
        Représentation textuelle.
        :return: Str
        """
        str_fields = ", ".join([f"{name}: {obj_field}" for name, obj_field in self.fields.items()])
        return f"EsMapping(related_to={self.related_to}, name={self.front_name}, fields={str_fields})"

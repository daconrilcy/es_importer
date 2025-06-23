from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union
import logging

from config import Config
from elastic_manager import ElasticManager
from models.file_management.file_infos import FileInfos
from models.file_management.filepath_codec import FilePathCodec
from models.mapping_management.fields_management import FieldsManager
from models.mapping_management.request_manager import MappingRequestManager
from models.mapping_management.saver import MappingSaver

logger = logging.getLogger(__name__)


class Mapping:
    """
    Représente un mapping complet incluant un nom, une entité liée,
    et un ensemble de champs instanciés via FieldsManager.
    Gère aussi l'identifiant, le chemin du fichier et l'intégration avec la transformation de requête de mapping.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None, config: Optional[Config] = None) -> None:
        """
        Initialise un objet Mapping à partir d'un dictionnaire JSON.
        :param data: Dictionnaire représentant le mapping complet.
        :param config: Configuration optionnelle.
        """
        data = data
        self._config: Config = config or Config()

        self._mapping_name: str = None
        self._related_to: str = None
        self._fields: Dict[str, Any] = {}
        self._filepath: Optional[str] = None
        self._id: Optional[str] = None
        self._new_file: bool = False
        self._description: Optional[str] = None

        self._set(data)

    def _set(self, data: dict) -> None:
        if data is None:
            return
        self._mapping_name = data.get("mapping_name", "")
        self._related_to = data.get("related_to", "")
        self._filepath = data.get("filepath")
        self._id = data.get("file_id")
        self._initialize_fields(data)

    def _initialize_fields(self, data: Dict[str, Any]) -> None:
        """
        Initialise les champs à partir des données fournies.
        """
        if not data or not isinstance(data, dict):
            logger.error("Invalid data for Mapping initialization: %s", type(data))
            return
        manager = FieldsManager(data, self._config)
        self._fields = manager.fields

    def __repr__(self) -> str:
        return (
            f"<Mapping name={self._mapping_name!r}, related_to={self._related_to!r}, "
            f"fields={list(self._fields.keys())}>"
        )

    def set_from_mapping_preview(self, mapping_preview_request: Dict[str, Any]) -> bool:
        """
        Met à jour le mapping à partir d'une requête de prévisualisation de mapping.
        Valide et transforme la requête via MappingRequestManager.
        :param mapping_preview_request: Dictionnaire de la requête de mapping.
        :return: True si succès, False sinon.
        """
        rm = MappingRequestManager(self._config)
        transformed = rm.validate_and_transform(mapping_preview_request)
        if not transformed:
            logger.error("Mapping: Failed to transform mapping preview request.")
            return False
        transformer = rm.transformer

        # Attribution
        self.mapping_name = transformer.mapping_name
        self.filepath = transformer.filepath
        self.related_to = transformer.related_to
        self.id = transformer.id
        self._new_file = transformer.new_file
        if transformer.fields:
            self._fields = transformer.fields
        return True

    def save(self) -> Tuple[Union[str, bool], bool]:
        """
        Sauvegarde le mapping dans un fichier JSON.
        :return: Chemin du fichier sauvegardé, ou None en cas d'échec.
        """
        print(f"Saving mapping: {self.mapping_name}")
        try:
            mapping_saver = MappingSaver(config=self._config)
            filepath, new = mapping_saver.save_from_dict(self.dict, self.filepath)
            if new:
                self.filepath = filepath
                self._new_file = True
        except Exception as e:
            logger.error(f"Mapping: Failed to save mapping: {e}")
            return False, False
        if self._new_file:
            try:
                result_index = self.add_file_to_index()
                if not result_index:
                    logger.error("Mapping: Failed to index mapping file.")
                    return False, False
            except Exception as e:
                logger.error(f"Mapping: Exception while indexing mapping file: {e}")
                return False, False
        return True, self._new_file

    def add_file_to_index(self) -> bool:
        """
        Ajoute le fichier de mapping au index Elasticsearch.
        :return: True si ajout reussi, False sinon.
        """
        file_infos = self.file_infos
        es_manager = ElasticManager(self._config)
        return es_manager.files_obj.add(file_infos)

    # --- GETTERS ---
    @property
    def mapping_name(self) -> str:
        """
        Retourne le nom du mapping.
        :return: str
        """
        return self._mapping_name

    @property
    def related_to(self) -> str:
        """
        Retourne l'entité liée au mapping.
        :return: str
        """
        return self._related_to

    @property
    def fields(self) -> Dict[str, Any]:
        """
        Retourne le dictionnaire des champs instanciés.
        :return: dict
        """
        return self._fields

    @property
    def filepath(self) -> Optional[str]:
        """
        Retourne le chemin du fichier de mapping.
        :return: Optional[str]
        """
        return self._filepath

    @property
    def id(self) -> Optional[str]:
        """
        Retourne l'identifiant du fichier de mapping.
        :return: Optional[str]
        """
        return self._id

    @property
    def description(self) -> Optional[str]:
        """
        Retourne la description du mapping.
        :return: Optional[str]
        """
        return self._description

    @property
    def file_infos_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "filename": Path(self.filepath).name,
            "filepath": self.filepath,
            "front_end_filename": self.mapping_name,
            "type": self._config.file_types.mappings.name,
            "extension": Path(self.filepath).suffix,
            "separator": None,
            "description": "Mapping File",
            "status": "saved",
            "encoded_filepath": FilePathCodec().encode(self.filepath),
        }

    @property
    def file_infos(self) -> FileInfos:
        return FileInfos(self.file_infos_dict)

    # --- SETTERS ---
    @mapping_name.setter
    def mapping_name(self, value: str) -> None:
        """
        Définit le nom du mapping.
        :param value: str
        """
        self._mapping_name = value

    @related_to.setter
    def related_to(self, value: str) -> None:
        """
        Définit l'entité liée au mapping.
        :param value: str
        """
        self._related_to = value

    @fields.setter
    def fields(self, value: Dict[str, Any]) -> None:
        """
        Met à jour les champs du mapping via FieldsManager.
        :param value: Dictionnaire au format mapping.
        """
        self._initialize_fields(value)

    @filepath.setter
    def filepath(self, value: Optional[str]) -> None:
        """
        Définit le chemin du fichier de mapping.
        :param value: Optional[str]
        """
        self._filepath = value

    @id.setter
    def id(self, value: Optional[str]) -> None:
        """
        Définit l'identifiant du fichier de mapping.
        :param value: Optional[str]
        """
        self._id = value

    @description.setter
    def description(self, value: Optional[str]) -> None:
        """
        Definit la description du mapping.
        :param value: Optional[str]
        """
        self._description = value

    @property
    def dict(self) -> Dict[str, Any]:
        """
        Retourne le mapping sous forme de dictionnaire.
        :return: Dictionnaire du mapping.
        """
        mapping_dict = {}
        for key, value in self._fields.items():
            clean_dict = value.dict.copy()
            del clean_dict["name"]
            mapping_dict[key] = clean_dict

        return {
            "mapping_name": self._mapping_name,
            "related_to": self._related_to,
            "mapping": mapping_dict,
            "filepath": self._filepath,
            "file_id": self._id
        }




if __name__ == "__main__":
    # noinspection LongLine
    request_test = {
        "mapping_name": "test pays",
        "file_id": "d5cKY5cBUmpRjBaYKbAU",
        "encoded_data_filepath": "hdXE55u81wRh77I7BJipV_sKgF_g4_fur913_VR05wxDOlxkZXZccHlcY3N2X2ltcG9ydGVyXGZpbGVzXGRhdGFzXDAzNTg5MmE1LTI4MzAtNGJmNC04MjJkLWNjNGY1YjI0NDM5Zi5jc3Y=",
        "mapping": {
            "iso2": {
                "category": "source",
                "source_field": "iso2",
                "name": "iso2",
                "type": "keyword",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Code ISO alpha-2 du pays"
            },
            "iso3": {
                "category": "source",
                "source_field": "iso3",
                "name": "iso3",
                "type": "keyword",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Code ISO alpha-3 du pays"
            },
            "status": {
                "category": "fixed_value",
                "name": "status",
                "value": "first status",
                "description": "first status"
            },
            "name_en": {
                "category": "source",
                "source_field": "name_en",
                "name": "name_en",
                "type": "text",
                "mapped": "True",
                "analyzer": "english",
                "description": "Nom du pays en anglais"
            },
            "name_en_completion": {
                "category": "remplacement",
                "type_completion": "synonymes",
                "original_field": "name_en",
                "name": "name_en_completion",
                "keep_original": "True",
                "filename": "2f38cb5f-2e78-47ad-a162-531b1ee10e51.csv",
                "use_first_column": "False",
                "description": "noms complementaires en anglais"
            },
            "name_en_phonetic": {
                "category": "phonetic",
                "original_field": "name_en",
                "type_completion": "phonetic",
                "name": "name_en_phonetic",
                "filename": "2f38cb5f-2e78-47ad-a162-531b1ee10e51.csv",
                "phonetic": {
                    "soundex": False,
                    "metaphone": True,
                    "metaphone3": True
                },
                "description": "Nom du pays en anglais phonétique"
            },
            "geo_point": {
                "category": "source",
                "source_field": "latlng",
                "name": "geo_point",
                "type": "geo_point",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Coordonnées géographiques du pays (latitude, longitude)"
            },
            "geo_shape": {
                "category": "source",
                "source_field": "geometry",
                "name": "geo_shape",
                "type": "geo_shape",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Géométrie du pays"
            },
            "flag": {
                "category": "source",
                "source_field": "flag",
                "name": "flag",
                "type": "text",
                "mapped": "True",
                "analyzer": "standard",
                "description": "URL de l'image du drapeau du pays"
            }
        }
    }

    mapping_test = Mapping()
    mapping_test.set_from_mapping_preview(request_test)
    mapping_test.filepath = r"C:\dev\py\csv_importer\files\mappings\test.json"
    print(mapping_test.dict)
    mapping_test.save()

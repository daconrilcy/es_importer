from datetime import datetime
from typing import Optional

from models.es_objects._base_obj import BaseObject


class EsImporter(BaseObject):
    """
    Classe pour gérer un objet d'importation de données vers Elasticsearch.
    Hérite de BaseObject.
    """

    def __init__(self,
                 es_id: Optional[str] = None,
                 filepath: Optional[str] = None,
                 filename: Optional[str] = None,
                 front_name: Optional[str] = None,
                 description: Optional[str] = None,
                 index_name: Optional[str] = None,
                 created_at: Optional[str | datetime] = None,
                 datas_filename: Optional[str] = None,
                 datas_separator: Optional[str] = None,
                 mapping_filename: Optional[str] = None,
                 ):
        super().__init__(es_id=es_id, filepath=filepath, filename=filename,
                         front_name=front_name, description=description, index_name=index_name,
                         created_at=created_at)
        self.file_type = self.fileTypes.importers
        self._datas_filename = datas_filename
        self._datas_separator = datas_separator
        self._mapping_filename = mapping_filename
        self.expected_keys = {"front_name", "datas_filename", "datas_separator", "mapping_filename", "index_name"}

    @property
    def datas_filename(self) -> str:
        """Nom du fichier de données à importer."""
        return self._datas_filename

    @datas_filename.setter
    def datas_filename(self, name: str):
        if not name:
            print("❌ EsImporter.datas_filename : valeur vide")
            return
        self._datas_filename = name

    @property
    def datas_separator(self) -> str:
        """Séparateur du fichier de données."""
        return self._datas_separator

    @datas_separator.setter
    def datas_separator(self, separator: str = ","):
        self._datas_separator = separator

    @property
    def mapping_filename(self) -> str:
        """Nom du fichier de mapping associé."""
        return self._mapping_filename

    @mapping_filename.setter
    def mapping_filename(self, name: str):
        if not name:
            print("❌ EsImporter.mapping_filename : valeur vide")
            return
        self._mapping_filename = name

    def to_dict_file(self):
        """
        Convertit l'objet en dictionnaire JSON exportable.
        :return: Dict
        """
        return {
            "front_name": self.front_name,
            "datas_filename": self.datas_filename,
            "datas_separator": self.datas_separator,
            "mapping_filename": self.mapping_filename,
            "index_name": self.index_name,
            "description": self.description,
        }

    @property
    def dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire.
        :return: Dict
        """
        base_dict = self.base_dict
        base_dict["datas_filename"] = self.datas_filename
        base_dict["datas_separator"] = self.datas_separator
        base_dict["mapping_filename"] = self.mapping_filename
        return base_dict

    @dict.setter
    def dict(self, data: dict):
        """
        Initialise l'objet à partir d'un dictionnaire.
        :param data: Dict
        :return: bool
        """
        if not data:
            print("❌ EsImporter.set_dict: data is None")
            return
        self.base_dict = data
        self.datas_filename = data.get("datas_filename", None)
        self.datas_separator = data.get("datas_separator", None)
        self.mapping_filename = data.get("mapping_filename", None)

    @property
    def dict_file(self) -> dict:
        """
        Convertit l'objet en dictionnaire JSON exportable.
        :return: Dict
        """
        return {
            "front_name": self.front_name,
            "datas_filename": self.datas_filename,
            "datas_separator": self.datas_separator,
            "mapping_filename": self.mapping_filename,
            "index_name": self.index_name,
            "description": self.description,
        }
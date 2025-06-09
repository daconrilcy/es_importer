from datetime import datetime
from typing import Optional

from config import Config
from models.es_objects._base_obj import BaseObject
from utils import set_datetime_in_str


class EsProcessor(BaseObject):
    """
    Spécialisation de BaseObject pour la gestion des fichiers d'import Elasticsearch.
    """

    def __init__(self,
                 es_id: Optional[str] = None,
                 filepath: Optional[str] = None,
                 filename: Optional[str] = None,
                 front_name: Optional[str] = None,
                 description: Optional[str] = None,
                 created_at: Optional[str | datetime] = None,
                 importer_list: Optional[list] = None,
                 last_used: Optional[str | datetime] = None,
                 config: Optional[Config] = None
                 ):
        super().__init__(
            es_id=es_id, filepath=filepath, filename=filename,
            front_name=front_name, description=description,
            created_at=created_at)
        config = config or Config()
        self.index_name = config.index_files_name
        self.file_type = self.fileTypes.processors
        self._importer_list = importer_list
        self._last_used = last_used

    @property
    def importer_list(self) -> list:
        """Retourne la liste des importateurs."""
        return self._importer_list

    @importer_list.setter
    def importer_list(self, importer_list: list):
        if not importer_list:
            print("❌ EsProcessor.importer_list : importer list is empty")
            return
        self._importer_list = importer_list

    @property
    def last_used(self) -> str:
        """Retourne la date de dernière utilisation."""
        return self._last_used

    @last_used.setter
    def last_used(self, last_used: str | datetime | None):
        self._last_used = set_datetime_in_str(last_used)

    @property
    def dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire.
        :return: Dict
        """
        base_dict = self.base_dict

        base_dict["importer_list"] = self.importer_list
        base_dict["last_used"] = self.last_used

        return base_dict

    @dict.setter
    def dict(self, data: dict):
        """
        Initialise l'objet à partir d'un dictionnaire.
        :param data: Dict
        :return: bool
        """
        if not data:
            print("❌ EsProcessor.set_dict: data is None")
            return
        self.base_dict = data
        self.importer_list = data.get("importer_list", [])
        self.last_used = data.get("last_used", set_datetime_in_str())

    @property
    def dict_file(self) -> dict:
        """
        Convertit l'objet en dictionnaire JSON exportable.
        :return: Dict
        """
        return {
            "front_name": self.front_name,
            "importer_list": self.importer_list,
            "last_used": self.last_used,
            "description": self.description,
        }
import pathlib
from datetime import datetime
from io import BytesIO
from typing import Optional, Union, List, Dict  # Utilisation de List pour plus de clarté

import pandas as pd
from werkzeug.datastructures import FileStorage
# Supposons que FileStorage, Config, CsvReader, BaseObject sont importés correctement
from config import Config
from models.file_type import FileTypes, FileType
from elastic_manager import ElasticSearchManager
from models.uploader import FileUploader
from models.readers.csv_file_reader import CsvFileReader  # Assurez-vous que CsvReader est importable
from models.es_objects._base_obj import BaseObject  # Assurez-vous que BaseObject est importable
from models.es_objects.datas.fields import DataFields
from models.web_viewer.csv_previewer import CsvPreview

# Ajout des imports manquants potentiels pour BaseObject si nécessaire


class EsDatas:
    """
    Classe représentant un objet de type 'datas', spécialisé pour les fichiers CSV.

    Hérite de BaseObject pour les métadonnées et fonctionnalités de fichier génériques
    (chemin, nom, id, date de création, etc.).
    Ajoute la gestion spécifique des fichiers CSV via CsvReader : lecture, analyse
    des champs, gestion du séparateur et sauvegarde du contenu CSV.
    """
    def __init__(self):
        self.file_uploader = FileUploader()
        self.file_reader = CsvFileReader()
        self.data_fields = DataFields()
        self.base_object = BaseObject()
        self.file_types = FileTypes()
        self.es_manager = ElasticSearchManager()
        self._file_type = self.file_types.datas
        self._id = None
        self._filepath = None
        self._filename = None
        self._front_end_filename = None
        self._original_filename = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def file_type(self) -> FileType:
        return self._file_type

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def front_end_filename(self) -> str:
        return self._front_end_filename
    
    @property
    def original_filename(self) -> str:
        return self._original_filename


    def save_file_from_uploader(self, file: FileStorage):
        self.file_uploader.save_file_from_upload(file, self.file_type)
        self._copy_infos_from_file_uploader()
        self.es_manager.add_file_to_index_files(self.to_dict())

    def get_infos_from_es(self, id: str):
        file_dict = self.es_manager.get_file_by_id(id)
        if file_dict is None:
            return False
        self.from_dict(file_dict)
        return True
    
    def save_separator(self, separator: str, id: str):
        self.es_manager.update_file_separator(separator, id)

    def save_front_end_filename(self, front_end_filename: str, id: str):
        self.es_manager.update_file_front_end_filename(front_end_filename, id)

    def save_basic_infos(self, id: str, **kwargs: Dict[str, str]):
        for key, value in kwargs.items():
            if key == "separator":
                self.save_separator(value, id)
            elif key == "front_end_filename":
                self.save_front_end_filename(value, id)
    
    def get_data_fields(self):
        self.data_fields.get_data_fields(self.file_reader.data)

    def _copy_infos_from_file_uploader(self):
        self._filepath = self.file_uploader.filepath
        self._filename = self.file_uploader.filename
        self._front_end_filename = self.file_uploader.front_end_filename
        self._original_filename = self.file_uploader.original_filename

    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "front_end_filename": self.front_end_filename,
            "original_filename": self.original_filename,
            "id": self.id,
            "file_type": self.file_type
        }
    
    def get_preview(self, chunk_index: int = 0, max_cols: int = 10):
        return CsvPreview(self.filepath, chunk_index, max_cols)
    
    def from_dict(self, dict_infos: dict):
        if dict_infos is None:
            return False
        self._id = dict_infos.get("id", None)
        self._filepath = dict_infos.get("filepath", None)
        self._filename = dict_infos.get("filename", None)
        self._front_end_filename = dict_infos.get("front_end_filename", None)
        self._original_filename = dict_infos.get("original_filename", None)


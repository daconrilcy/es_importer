from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

from config import Config
from models.file_management.file_infos import FileInfos
from models.file_management.filepath_codec import FilePathCodec


class BaseFilePreviewer(ABC):
    """Classe abstraite de base pour la prévisualisation de fichiers."""

    def __init__(self, list_files: Optional[list[FileInfos]] = None) -> None:
        self._encoded_filepath: Optional[str] = None
        self._file_infos: Optional[FileInfos] = None
        self._reader: Optional[Any] = None
        self._list_files: Optional[list[FileInfos]] = list_files

    def build_from_file_infos(self, file_infos: FileInfos) -> None:
        """Construit le previewer à partir d'un objet FileInfos."""
        self._file_infos = file_infos
        self._encoded_filepath = FilePathCodec.encode(file_infos.filepath)
        self._reader = self._create_reader_from_infos(file_infos)

    def build_from_dict(self, data: Dict[str, Any]) -> None:
        """Construit le previewer à partir d'un dictionnaire de données."""
        prepared_data = self._prepare_dict_data(data)
        self._file_infos = FileInfos(doc=prepared_data)
        self._encoded_filepath = prepared_data["encodedFilepath"]
        self._reader = self._create_reader_from_dict(prepared_data)

    @property
    def encoded_filepath(self) -> Optional[str]:
        """Renvoie le chemin encodé du fichier."""
        return self._encoded_filepath

    @property
    def file_infos(self) -> Optional[FileInfos]:
        """Renvoie les informations du fichier."""
        return self._file_infos

    @property
    def id(self) -> str:
        """Renvoie l'identifiant du fichier."""
        return self._file_infos.id if self._file_infos else ""

    @property
    def front_end_filename(self) -> Optional[str]:
        """Renvoie le nom de fichier pour le front-end."""
        return self._file_infos.front_end_filename if self._file_infos else None

    @property
    def type_name(self) -> Optional[str]:
        """Renvoie le nom du type du fichier."""
        return self._file_infos.type.name if self._file_infos else None

    @property
    def list_files(self) -> Optional[list[FileInfos]]:
        """Renvoie la liste des fichiers."""
        return self._list_files

    @property
    def list_file_front_end_names(self) -> Optional[list[str]]:
        """Renvoie la liste des noms de fichiers."""
        return [self.file_infos.front_end_filename for file_infos in self._list_files]

    @list_files.setter
    def list_files(self, list_files: list[FileInfos]):
        self._list_files = list_files

    def _prepare_dict_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les données du dictionnaire pour initialisation de FileInfos."""
        encoder = FilePathCodec()

        if "encodedFilepath" in data:
            data["filepath"] = encoder.decode(data["encodedFilepath"])
        elif "filepath" in data:
            data["encodedFilepath"] = encoder.encode(data["filepath"])
        else:
            raise ValueError("'filepath' ou 'encodedFilepath' est requis.")

        filepath = Path(data["filepath"])
        default_filename = filepath.stem

        data.setdefault("type", Config().file_types.mappings.name)
        data.setdefault("filename", default_filename)
        data.setdefault("sep")
        data.setdefault("front_end_filename", default_filename[:-4])
        data.setdefault("original_filename", default_filename)

        return data

    @abstractmethod
    def _create_reader_from_infos(self, file_infos: FileInfos) -> Any:
        """Crée un lecteur de fichier à partir de FileInfos."""
        pass

    @abstractmethod
    def _create_reader_from_dict(self, data: Dict[str, Any]) -> Any:
        """Crée un lecteur de fichier à partir d'un dictionnaire de données."""
        pass

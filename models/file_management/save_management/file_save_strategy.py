from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pandas import DataFrame
from werkzeug.datastructures import FileStorage

from models.file_management.file_utls import FileUtils
from models.file_type import FileTypes

import logging

logger = logging.getLogger(__name__)


class FileSaveStrategy(ABC):
    """
    Interface pour les stratégies de sauvegarde de fichiers.
    """

    @abstractmethod
    def save(self, *args: Any, **kwargs: Any) -> str:
        """
        Sauvegarde le contenu dans un fichier et retourne le chemin du fichier sauvegardé.
        """
        pass


class BaseLocalSaveStrategy(FileSaveStrategy):
    """
    Classe de base pour les stratégies de sauvegarde locale.
    Initialise et gère le dossier de destination.
    """

    def __init__(self, folder_path: str) -> None:
        self.folder_path: Path = Path(folder_path)
        self.folder_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, filename: str) -> Path:
        """
        Retourne le chemin absolu complet du fichier à partir du nom de fichier.
        """
        return self.folder_path / filename

    @abstractmethod
    def save(self, *args: Any, **kwargs: Any) -> str:
        """
        Sauvegarde le contenu dans un fichier et retourne le chemin du fichier sauvegardé.
        """
        pass


class UploadedLocalFileSaveStrategy(BaseLocalSaveStrategy):
    """
    Stratégie de sauvegarde pour fichiers uploadés (type FileStorage).
    """

    def save(self, file: FileStorage, filename: str) -> str:
        file_path = self._get_file_path(filename)
        file.save(file_path)
        return str(file_path)


class DataFrameLocalSaveStrategy(BaseLocalSaveStrategy):
    """
    Stratégie de sauvegarde pour objets pandas DataFrame.
    """

    def save(self, df: DataFrame, filename: str) -> str:
        file_path = self._get_file_path(filename)
        df.to_csv(file_path, index=False)
        return str(file_path)


class TXTLocalFileSaveStrategy(BaseLocalSaveStrategy):
    """
    Stratégie de sauvegarde pour contenu texte brut (str).
    """

    def save(self, content: str, filename: str) -> str:
        file_path = self._get_file_path(filename)
        with file_path.open(mode='w', encoding='utf-8') as file:
            file.write(content)
        return str(file_path)


class MappingFileSaveStrategy(BaseLocalSaveStrategy):
    """
    Stratégie de sauvegarde pour fichiers JSON.
    """

    def __init__(self):
        folder_path = FileTypes().mappings.folder_path
        super().__init__(folder_path)

    def save(self, content: str, filename: str = None, filepath: str = None) -> str:
        file_path: Path = None
        if filename is None and filepath is None:
            logger.error("MappingFileSaveStrategy.save: filename or filepath is None")
            filename = FileUtils().generate_filename()
            file_path = self._get_file_path(filename)
        elif filepath is not None:
            file_path = Path(filepath)
            filename = file_path.name
            file_path = self._get_file_path(filename)
        elif filename is not None:
            file_path = self._get_file_path(filename)
        with file_path.open(mode='w', encoding='utf-8') as file:
            file.write(content)
        return str(file_path)

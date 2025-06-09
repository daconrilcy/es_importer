from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from config import Config
from utils import normalize_filepath


class BaseFileReader(ABC):
    """
    Interface abstraite pour les lecteurs de fichiers.
    Gère le chemin, l'encodage et la structure de base.
    """

    def __init__(self, filepath: str, encoding: str = "utf-8"):
        self.filepath = Path(normalize_filepath(filepath))
        self.encoding = encoding
        self.effective_encoding = self._normalize_encoding(encoding)
        self.max_size = Config().max_csv_file_size

        self.validate_path(self.filepath)
        if not self.validate_structure():
            raise ValueError(f"Le fichier '{self.filepath}' n'a pas une structure valide.")

    @staticmethod
    def _normalize_encoding(encoding: str) -> str:
        """Transforme 'utf-8' en 'utf-8-sig' pour gérer les fichiers avec BOM."""
        return encoding.replace("utf-8", "utf-8-sig")

    def validate_path(self, filepath: Path, max_size: int = None):
        """Vérifie que le fichier existe, est lisible et de taille raisonnable."""
        if max_size is None:
            max_size = self.max_size
        if not filepath.is_file() or not filepath.exists():
            raise FileNotFoundError(f"Le fichier '{filepath}' est introuvable.")
        if filepath.stat().st_size == 0:
            raise ValueError(f"Le fichier '{filepath}' est vide.")
        if filepath.stat().st_size > max_size:
            raise ValueError(f"Le fichier est trop volumineux (> {max_size // 1024 // 1024} Mo).")

    @abstractmethod
    def get_all(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def read_partial(self, start: int, size: int, **kwargs) -> Any:
        pass

    @abstractmethod
    def validate_structure(self) -> bool:
        return True

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class BasicEsModule(ABC):
    """
    Classe chargée de lire et d'encapsuler des définitions d'analyseurs
    depuis un fichier JSON et de les représenter sous forme d'objets AnalyzerBaseField.
    """

    def __init__(self, config_filepath: Optional[str] = None) -> None:
        self._config_filepath = config_filepath
        self._fields: Dict[str, Any] = {}
        self._fill_fields()

    @staticmethod
    def _load_data(filepath: str) -> Optional[List[Dict[str, str]]]:
        """
        Charge les données JSON du fichier spécifié.

        Args:
            filepath (str): Chemin vers le fichier JSON.

        Returns:
            Optional[List[Dict[str, str]]]: Liste de dictionnaires représentant les analyseurs,
            ou None en cas d'erreur.
        """
        path = Path(filepath)

        if not path.is_file() or path.suffix != ".json":
            logger.error(f"Invalid or missing file: {filepath}")
            return None

        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            return None

    def _pre_fill_fields(self) -> Optional[List[Dict[str, str]]]:
        """
        Convertit les données chargées en objets.
        """
        fields_raw = self._load_data(self._config_filepath)
        if not isinstance(fields_raw, list):
            logger.error(f"Data is not a list but {type(fields_raw)}")
            return None
        if fields_raw is None:
            logger.error("Data is None")
            return None
        if len(fields_raw) == 0:
            return None
        return fields_raw

    @abstractmethod
    def _fill_fields(self) -> None:
        field_raw = self._pre_fill_fields()

    def __str__(self) -> str:
        """
        Retourne une représentation textuelle de l'objet avec tous les analyseurs chargés.
        """
        lines = [f"{self.__class__.__name__}(filepath={self._config_filepath})"]
        lines.extend(f"\t{name}: {field}" for name, field in self._fields.items())
        return "\n".join(lines)

    @property
    def fields(self) -> Dict[str, Any]:
        """Accès direct au dictionnaire des fields indexés par nom."""
        return self._fields

    @property
    def fields_list(self) -> List[Any]:
        """Liste des objets fields."""
        return list(self._fields.values())

    @property
    def fields_names(self) -> List[str]:
        """Liste des noms des fields."""
        return list(self._fields.keys())

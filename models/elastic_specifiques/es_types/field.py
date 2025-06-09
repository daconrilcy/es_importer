import logging
from typing import Optional, Any

from models.utils_obj import MultiUtils
from utils import sanitaze_string

logger = logging.getLogger(__name__)


class EsFieldType:
    """
    Représente un type de champ Elasticsearch, incluant son nom, sa catégorie, et sa description.
    """

    def __init__(self, doc: dict[str, Any] = None):
        self._name: Optional[str] = None
        self._category: Optional[str] = None
        self._description: Optional[str] = None
        if doc is not None:
            self.set_from_df_row(doc)

    @property
    def name(self) -> str:
        """Retourne le nom du champ."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Définit le nom du champ, après nettoyage."""
        self._name = self._sanitize_or_none("name", value)

    @property
    def category(self) -> str:
        """Retourne la catégorie du champ."""
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        """Définit la catégorie du champ, après nettoyage."""
        self._category = self._sanitize_or_none("category", value)

    @property
    def description(self) -> str:
        """Retourne la description du champ."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Définit la description du champ sans nettoyage."""
        self._description = value or ""

    def is_this(self, name: str) -> bool:
        """
        Vérifie si le nom donné correspond à celui de l'objet (après nettoyage).
        """
        return self.name == sanitaze_string(name)

    def set_from_df_row(self, row: dict[str, Any]) -> None:
        """
        Initialise les attributs à partir d’une ligne de DataFrame (sous forme de dictionnaire).
        """
        required_keys = ["name", "category", "description"]
        for key in required_keys:
            if key not in row:
                logger.warning(f"EsFieldType - set_from_df_row - '{key}' manquant dans la ligne")
                return
            if row[key] is None:
                logger.warning(f"EsFieldType - set_from_df_row - '{key}' est None")
                return

        self.name = row["name"]
        self.category = row["category"]
        self.description = row["description"]

    def __str__(self) -> str:
        return f"{self.name} - {self.category} - {self.description}"

    @staticmethod
    def _sanitize_or_none(source: str, value: Optional[str]) -> str:
        """
        Nettoie une chaîne ou retourne une chaîne vide si None.
        """
        if value is None:
            logger.info(f"EsFieldType - {source} value is None")
            return ""
        return MultiUtils().sanitaze_string(value)

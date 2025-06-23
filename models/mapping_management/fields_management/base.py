from typing import Any, Dict

from models.elastic_specifiques import EsTypes
from config import Config


class BaseMappingField:
    """
    Classe de base pour représenter un champ de mapping générique avec un nom,
    une catégorie et une description. Doit être étendue par des classes concrètes.
    """

    def __init__(self, name: str, data: Dict[str, Any], config: Config = None) -> None:
        """
        Initialise un champ de mapping à partir d'un dictionnaire de données.

        :param data: Dictionnaire contenant les clés 'name', 'category', et optionnellement 'description'.
        :param config: Configuration utilisée pour l'initialisation d'EsTypes.
        """
        config = config or Config()
        self._es_types: EsTypes = EsTypes(config)
        self.name = name
        self._category: str = ""
        self._description: str = ""

        self._initialize_base_fields(data)
        self._set(data)

    def _initialize_base_fields(self, data: Dict[str, Any]) -> None:
        """
        Initialise les champs de base à partir du dictionnaire de données.

        :param data: Dictionnaire avec les clés 'name', 'category' et 'description'.
        :raises TypeError: Si data n'est pas un dictionnaire.
        :raises ValueError: Si les champs 'name' ou 'category' sont manquants.
        """
        if not isinstance(data, dict):
            raise TypeError("Le champ 'data' doit être un dictionnaire.")

        self._category: str = data.get("category", None)
        if not self._category:
            raise ValueError(
                f"La categorie du champ '{self.name}' est manquante ou vide."
                f"Veuillez fournir une categorie pour ce champ'."
            )
        self._description: str = data.get("description", "")

        if not self._name:
            raise ValueError("Le champ 'name' est obligatoire.")
        if not self._category:
            raise ValueError("Le champ 'category' est obligatoire.")

    def _set(self, data: Dict[str, Any]) -> None:
        """
        Méthode à implémenter dans les classes filles pour définir les champs spécifiques.
        """
        raise NotImplementedError("La méthode _set doit être implémentée dans la sous-classe.")

    def __repr__(self) -> str:
        return (
            f"<MappingField name={self._name}, "
            f"category={self._category}, "
            f"description={self._description}>"
        )

    def set(self, data: Dict[str, Any]) -> None:
        self._set(data)

    @property
    def dict(self) -> Dict[str, Any]:
        """
        Retourne un dictionnaire représentant le champ de mapping.
        """
        return {
            "name": self._name,
            "category": self._category,
            "description": self._description,
        }

    # --- GETTERS ---

    @property
    def name(self) -> str:
        """Retourne le nom du champ."""
        return self._name

    @property
    def category(self) -> str:
        """Retourne la catégorie du champ."""
        return self._category

    @property
    def description(self) -> str:
        """Retourne la description du champ."""
        return self._description

    # --- SETTERS ---

    @name.setter
    def name(self, value: str) -> None:
        """Définit le nom du champ."""
        if not value or not isinstance(value, str) or not value.strip() or value.strip() == "":
            raise ValueError("Le champ 'name' est obligatoire.")
        self._name = value

    @category.setter
    def category(self, value: str) -> None:
        """Définit la catégorie du champ."""
        self._category = value

    @description.setter
    def description(self, value: str) -> None:
        """Définit la description du champ."""
        self._description = value

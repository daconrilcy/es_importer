import json
from pathlib import Path
from typing import Optional, Dict, List

from config import Config
from models.mapping_management.es_types.single_type import EsType


class EsTypes:
    """Gère le chargement et l'accès aux types Elasticsearch définis dans un fichier JSON."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialise la classe avec les types chargés à partir du fichier JSON configuré.

        :param config: Instance optionnelle de Config contenant le chemin du fichier JSON.
        """
        config = config or Config()
        self._types: Dict[str, EsType] = {}
        self._es_types_list: List[EsType] = []
        self._load_es_types_from_json(config.es_types_filepath)

    def _load_es_types_from_json(self, json_path: str | Path) -> None:
        """
        Charge les types Elasticsearch à partir d'un fichier JSON.

        :param json_path: Chemin du fichier JSON
        :raises ValueError: si le fichier n'existe pas
        """
        json_path = Path(json_path)
        if not json_path.is_file():
            raise ValueError(
                f"EsTypes - Erreur de chargement - Le fichier JSON {json_path} n'existe pas."
            )

        with json_path.open(encoding='utf-8') as f:
            data = json.load(f)

        for entry in data:
            es_type = EsType(
                name=entry.get("name"),
                category=entry.get("category"),
                description=entry.get("description")
            )
            self._types[es_type.name] = es_type
            self._es_types_list.append(es_type)

    @property
    def types(self) -> Dict[str, EsType]:
        """Retourne le dictionnaire des types ES par nom."""
        return self._types

    @property
    def es_types_list(self) -> List[EsType]:
        """Retourne la liste des objets EsType."""
        return self._es_types_list

    @property
    def list_names(self) -> List[str]:
        """Retourne la liste des noms de types."""
        return [es_type.name for es_type in self._es_types_list]

    @property
    def list_categories(self) -> List[str]:
        """Retourne la liste des catégories de types."""
        return [es_type.category for es_type in self._es_types_list]

    def has_type(self, es_type_name: str) -> bool:
        """
        Indique si un type ES existe.

        :param es_type_name: Nom du type à vérifier
        :return: True si présent, False sinon
        """
        return es_type_name in self._types

    def get_es_type(self, es_type_name: str) -> EsType:
        """
        Retourne l'objet EsType correspondant à un nom.

        :param es_type_name: Nom du type à récupérer
        :raises KeyError: si le type n'existe pas
        """
        if es_type_name not in self._types:
            raise KeyError(f"Le type ES '{es_type_name}' n'existe pas.")
        return self._types[es_type_name]


if __name__ == '__main__':
    estypes_test = EsTypes()
    print(estypes_test.types)
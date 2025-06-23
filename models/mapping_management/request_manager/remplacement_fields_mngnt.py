from typing import Dict, Any, List, Union, Optional

from config import Config
import logging

from models.file_management.readers.csv_file_reader import CsvFileReader

logger = logging.getLogger(__name__)


class RequestRemplacementFieldsManager:
    """
    Gère la validation et l'enrichissement des mappings pour les requêtes de remplacement de champs.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialise le gestionnaire avec la configuration applicative.
        """
        self._config = config or Config()

    def check_modify_request(
            self, request: dict
    ) -> Union[bool, Dict[str, Any]]:
        """
        Vérifie et enrichit le dictionnaire de requête avec les colonnes nécessaires.

        Args:
            request (dict): La requête contenant les mappings à valider.

        Returns:
            bool | Dict[str, Any]: False si la requête est invalide, sinon le dictionnaire enrichi.
        """
        mappings = request.get("mapping")
        if not mappings or not isinstance(mappings, dict):
            logger.error("Mappings absent ou invalide dans la requête.")
            return False

        for key, mapping in mappings.items():
            if not isinstance(mapping, dict):
                logger.error("Le mapping pour '%s' n'est pas un dictionnaire.", key)
                return False

            category = mapping.get("category")
            if category not in {"remplacement", "phonetic"}:
                logger.info(
                    "Catégorie '%s' ignorée pour le mapping '%s'.", category, key
                )
                continue

            filename = mapping.get("filename")
            column_names = None
            if filename:
                column_names = self._get_column_names_with_file(mapping)
            else:
                column_names = self._get_column_names_without_file(mapping)

            if not column_names:
                logger.error(
                    "Impossible de déterminer les colonnes pour le mapping '%s'.", key
                )
                return False

            # Ajoute la liste des noms de colonnes au mapping concerné
            mappings[key]["column_names"] = column_names

        return request

    @staticmethod
    def _get_column_names_without_file(
            mapping: dict
    ) -> Optional[List[str]]:
        """
        Récupère les noms de colonnes à partir du mapping sans fichier CSV.

        Args:
            mapping (dict): Dictionnaire de mapping.

        Returns:
            Optional[List[str]]: Liste des noms de colonnes ou None si erreur.
        """
        category = mapping.get("category")
        original_field = mapping.get("original_field")
        if not original_field or category not in {"remplacement", "phonetic"}:
            return None

        column_names = [original_field]

        if category == "remplacement":
            column_names.append(f"{original_field}_new")
        elif category == "phonetic":
            phonetic_info = mapping.get("phonetic", {})
            if phonetic_info.get("soundex"):
                column_names.append(f"{original_field}_soundex")
            if phonetic_info.get("metaphone"):
                column_names.append(f"{original_field}_metaphone")
            if phonetic_info.get("metaphone3"):
                column_names.append(f"{original_field}_metaphone3_primary")
                column_names.append(f"{original_field}_metaphone3_secondary")

        return column_names

    def _get_column_names_with_file(
            self, mapping: dict
    ) -> Optional[List[str]]:
        """
        Récupère les noms de colonnes depuis un fichier CSV spécifié dans le mapping.

        Args:
            mapping (dict): Dictionnaire de mapping.

        Returns:
            Optional[List[str]]: Liste des noms de colonnes ou None si erreur.
        """
        category = mapping.get("category")
        filename = mapping.get("filename")
        if not filename or category not in {"remplacement", "phonetic"}:
            return None
        ft = self._config.file_types
        fpath = ft.completions.folder_path
        filepath = fpath / filename

        try:
            csv_reader = CsvFileReader(filepath=filepath, config=self._config)
            column_names = csv_reader.headers
            if not column_names:
                logger.error("Fichier CSV '%s' sans entêtes.", filename)
                return None
            return column_names
        except Exception as e:
            logger.error(
                "Erreur lors de la lecture du fichier CSV '%s': %s", filename, e
            )
            return None


if __name__ == "__main__":
    config = Config()
    request_manager = RequestRemplacementFieldsManager(config)
    # noinspection LongLine
    mapping_test = {
        "mapping_name": "test pays",
        "file_id": "d5cKY5cBUmpRjBaYKbAU",
        "encoded_data_filepath": "hdXE55u81wRh77I7BJipV_sKgF_g4_fur913_VR05wxDOlxkZXZccHlcY3N2X2ltcG9ydGVyXGZpbGVzXGRhdGFzXDAzNTg5MmE1LTI4MzAtNGJmNC04MjJkLWNjNGY1YjI0NDM5Zi5jc3Y=",
        "mapping": {
            "iso2": {
                "category": "source",
                "source_field": "iso2",
                "name": "iso2",
                "type": "keyword",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Code ISO alpha-2 du pays"
            },
            "iso3": {
                "category": "source",
                "source_field": "iso3",
                "name": "iso3",
                "type": "keyword",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Code ISO alpha-3 du pays"
            },
            "status": {
                "category": "fixed_value",
                "name": "status",
                "value": "first status",
                "description": "first status"
            },
            "name_en": {
                "category": "source",
                "source_field": "name_en",
                "name": "name_en",
                "type": "text",
                "mapped": "True",
                "analyzer": "english",
                "description": "Nom du pays en anglais"
            },
            "name_en_completion": {
                "category": "remplacement",
                "type_completion": "synonymes",
                "original_field": "name_en",
                "name": "name_en_completion",
                "keep_original": "True",
                "filename": "2f38cb5f-2e78-47ad-a162-531b1ee10e51.csv",
                "use_first_column": "False",
                "description": "noms complementaires en anglais"
            },
            "name_en_phonetic": {
                "category": "phonetic",
                "original_field": "name_en",
                "type_completion": "phonetic",
                "name": "name_en_phonetic",
                "filename": "97b52d22-3ac5-41ec-913a-b49f12200170.csv",
                "phonetic": {
                    "soundex": False,
                    "metaphone": True,
                    "metaphone3": True
                },
                "description": "Nom du pays en anglais phonétique"
            },
            "geo_point": {
                "category": "source",
                "source_field": "latlng",
                "name": "geo_point",
                "type": "geo_point",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Coordonnées géographiques du pays (latitude, longitude)"
            },
            "geo_shape": {
                "category": "source",
                "source_field": "geometry",
                "name": "geo_shape",
                "type": "geo_shape",
                "mapped": "True",
                "analyzer": "standard",
                "description": "Géométrie du pays"
            },
            "flag": {
                "category": "source",
                "source_field": "flag",
                "name": "flag",
                "type": "text",
                "mapped": "True",
                "analyzer": "standard",
                "description": "URL de l'image du drapeau du pays"
            }
        }
    }

    print(request_manager.check_modify_request(mapping_test))

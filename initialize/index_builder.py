import json
import logging
import os
from typing import Optional

from initialize.index_details import IndexDetails

logger = logging.getLogger(__name__)


class IndexDetailsBuilder:
    """Construit un objet IndexDetails à partir de données JSON et fichiers."""

    def __init__(self, base_folder: str):
        self.base_folder = base_folder

    def build(self, config_entry: Optional[dict]) -> Optional[IndexDetails]:
        """Construit un objet IndexDetails à partir de données JSON et fichiers."""
        if not config_entry:
            return None

        mapping = self._load_mapping(config_entry.get("mapping_file"))
        if mapping is None:
            return None

        datas_path = os.path.join(self.base_folder, config_entry.get("datas_file", ""))
        return IndexDetails(config_entry["index_name"], mapping, datas_path)

    def _load_mapping(self, filename: Optional[str]) -> Optional[dict]:
        """Charge un fichier JSON de mapping."""
        if not filename:
            logger.warning("Fichier de mapping manquant.")
            return None

        filepath = os.path.join(self.base_folder, filename)
        if not os.path.isfile(filepath):
            logger.error("Fichier mapping introuvable : %s", filepath)
            return None

        try:
            with open(filepath, encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Erreur lecture mapping %s : %s", filename, e)
            return None

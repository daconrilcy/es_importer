import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InfosFileReader:
    """Lit et parse un fichier JSON contenant les infos de configuration d’index."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._data = self._load()

    def _load(self) -> Optional[dict]:
        try:
            with open(self.filepath, encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Erreur lecture infos config : %s", e)
            return None

    def get(self, key: str) -> Optional[dict]:
        """
        Connaitre la valeur d’une clé dans le fichier infos configuration.
        :param key:
        :return:
        """
        if not self._data or key not in self._data:
            logger.warning("Clé '%s' absente des infos config", key)
            return None
        return self._data[key]

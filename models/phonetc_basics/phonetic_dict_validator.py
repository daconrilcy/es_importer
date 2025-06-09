from typing import Dict
import logging

logger = logging.getLogger(__name__)

class PhoneticDictValidator:

    def __init__(self, user_dict: Dict[str, bool]):
        self._default_dict = {"soundex": False, "metaphone": False, "metaphone3": False}
        self._user_dict = user_dict

    def validate(self) -> Dict[str, bool]:
        """Valide et nettoie le dictionnaire des algorithmes phonétiques."""
        if not isinstance(self._user_dict, dict):
            logger.error("PhoneticChunkTransformer - phonex_dict doit être un dictionnaire")
            return self._default_dict
        return {k: self._user_dict.get(k, False) for k in self._default_dict}
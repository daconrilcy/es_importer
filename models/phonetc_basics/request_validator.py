import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PhoneticRequestValidator:
    """
    Valide et extrait les paramètres nécessaires d'une requête phonétique.
    """

    _VALID_SEPARATORS = [",", ", ", ";", "; ", "\t", "|"]

    _VALID_FILEPATH_KEYS = [
        "original_filepath", "originalfilepath", "filepath",
        "file_path", "path", "encoded_filepath",
        "encodedfilepath", "encoded_file_path"
    ]

    _VALID_COLUMN_KEYS = ["column", "colonne", "col", "source_column", "original_field", "field"]

    def __init__(self, phonetic_request: dict):
        self._filepath: Optional[str] = None
        self._column: Optional[str] = None
        self._sep: Optional[str] = None
        self._phonetic: Optional[str] = None
        self._is_valid: bool = self._validate_and_set(phonetic_request)
        self._original_request = phonetic_request

    def _validate_and_set(self, phonetic_request: Optional[dict]) -> bool:
        """
        Valide la requête et initialise les attributs si valide.
        """

        if not phonetic_request:
            logger.error("PhoneticInserter - la requête est vide")
            return False

        filepath = None
        for key in self._VALID_FILEPATH_KEYS:
            if key in phonetic_request:
                filepath = phonetic_request[key]
                break

        column = None
        for key in self._VALID_COLUMN_KEYS:
            if key in phonetic_request:
                column = phonetic_request[key].strip()
                break
        sep = phonetic_request.get("sep")
        phonetic = phonetic_request.get("phonetic")

        if not filepath or not column or not phonetic:
            logger.error(
                f"PhoneticInserter - Valeurs manquantes filepath={filepath}, "
                f"column={column}, phonetic={phonetic}"
            )
            return False

        self._filepath = filepath
        self._column = column
        self._sep = sep if sep in self._VALID_SEPARATORS else None
        self._phonetic = phonetic
        return True

    @property
    def is_valid(self) -> bool:
        """
        Indique si la requête est valide.
        """
        return self._is_valid

    @property
    def filepath(self) -> Optional[str]:
        """Chemin du fichier"""
        return self._filepath

    @property
    def column(self) -> Optional[str]:
        """Nom de la colonne à traiter"""
        return self._column

    @property
    def sep(self) -> Optional[str]:
        """Séparateur utilisé dans le fichier CSV"""
        return self._sep

    @property
    def phonetic(self) -> Optional[str]:
        """Méthode phonétique à utiliser"""
        return self._phonetic

    @property
    def original_request(self) -> Optional[dict]:
        return self._original_request
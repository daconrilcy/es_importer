import logging
from typing import Optional

from config import Config
from models.file_management.filepath_codec import FilePathCodec
from models.file_management.file_modifier.phonex_injecter import PhonexCsvModifier
from models.phonetc_basics.request_validator import PhoneticRequestValidator

logger = logging.getLogger(__name__)


class PhoneticRequestInserter:
    """
    Service d'insertion de colonnes phonétiques dans un fichier à partir d'une requête utilisateur.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        self._config: Config = config or Config()
        self._filepathcodec = FilePathCodec()
        self._request_validator: PhoneticRequestValidator = None

    def insert(self, request_dataset: dict) -> bool:
        """
        Traite une requête d'ajout de phonétique à un dataset.

        :param request_dataset: Dictionnaire contenant les informations nécessaires.
        :return: True si le traitement a réussi, False sinon.
        """
        if not request_dataset:
            logger.error("PhoneticInserter - La requête est vide.")
            return False
        self._request_validator = PhoneticRequestValidator(request_dataset)
        if not self._request_validator.is_valid:
            logger.error("PhoneticInserter - La requête est invalide.")
            return False

        return self._add_phonetic_column()

    def _add_phonetic_column(self) -> bool:
        try:
            decoded_filepath = self._filepathcodec.decode(self._request_validator.filepath)
        except Exception as e:
            logger.error(f"PhoneticInserter - Erreur de décodage du chemin de fichier : {e}")
            return False

        try:
            phonetic_modifier = PhonexCsvModifier(
                filepath=decoded_filepath,
                separator=self._request_validator.sep,
                source_column=self._request_validator.column,
                phonex_dict=self._request_validator.phonetic,
                config=self._config,
            )
            return phonetic_modifier.process()
        except Exception as e:
            logger.error(f"PhoneticInserter - Erreur lors du traitement phonétique : {e}")
            return False


if __name__ == '__main__':
    import json

    filepath = "C:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv"
    encoded_filepath = FilePathCodec().encode(filepath)
    sample_request = {
        'filepath': encoded_filepath,
        'column': 'name_en',
        'phonetic': {
            'soundex': False,
            'metaphone': True,
            'metaphone3': False
        },
        'sep': None
    }

    sample_request_json = json.dumps(sample_request)
    print(PhoneticRequestInserter().insert_phonetic_from_request(sample_request))

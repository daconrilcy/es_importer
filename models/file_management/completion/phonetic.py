import logging
from typing import Optional

from config import Config
from models.file_management.file_utls import FileUtils
from models.file_management.filepath_codec import FilePathCodec
from models.file_management.readers.csv_file_reader import CsvFileReader
from models.phonetc_basics.chunk_encoder import PhoneticChunkEncoder
from models.phonetc_basics.phonetic_dict_validator import PhoneticDictValidator
from models.file_management.completion.creator import CsvManualMultiColumnsBuilder

from models.phonetc_basics.request_validator import PhoneticRequestValidator

logger = logging.getLogger(__name__)


class PhoneticFileCreator:
    """
    Traite une requête de transformation phonétique sur un fichier CSV.
    """

    def __init__(self, request_dataset: dict, config: Optional[Config] = None) -> bool | str:
        self._config = config or Config()
        self._request = PhoneticRequestValidator(request_dataset)

    def create(self) -> bool:
        """
        Lance le processus de création d'un CSV enrichi de colonnes phonétiques.

        Returns:
            bool: Succès ou échec du traitement.
        """
        if not self._request.is_valid:
            logger.error("PhoneticInserter - La requête est invalide.")
            return False

        original_filepath = FilePathCodec().decode(self._request.filepath)
        if not original_filepath:
            logger.error("PhoneticInserter - Le chemin de fichier original est invalide.")
            return False

        phonex_dict = PhoneticDictValidator(self._request.phonetic).validate()
        if not phonex_dict:
            logger.error("PhoneticInserter - Les algorithmes phonétiques sont invalides.")
            return False

        filename = self._request.original_request.get("filename") or FileUtils().generate_filename(".csv")
        csv_reader = CsvFileReader(filepath=original_filepath, sep=self._request.sep, config=self._config)
        encoder = PhoneticChunkEncoder(phonex_dict, self._request.column, self._config, True)

        try:
            self._build_empty_phonetic_csv(csv_reader, encoder, filename, original_filepath)
        except Exception as e:
            logger.error(f"PhoneticInserter - Erreur durant le traitement de création du fichier : {e}")
            return False

        try:
            self._inject_encoded_values(csv_reader, encoder)
        except Exception as e:
            logger.error(f"PhoneticInserter - Erreur durant le traitement d'injection des données : {e}")
            return False

        return filename

    def _build_empty_phonetic_csv(self, csv_reader: CsvFileReader, encoder: PhoneticChunkEncoder,
                                  filename: str, original_filepath: str):
        """Crée un fichier CSV avec des colonnes vides prêtes à recevoir les données encodées."""
        builder = CsvManualMultiColumnsBuilder(
            source_column=self._request.column,
            new_columns=encoder.new_column_names,
            original_filepath=original_filepath,
            separator=self._request.sep,
            chunk_size=csv_reader.chunk_size,
            filename=filename,
            config=self._config
        )
        builder.create_csv()
        self._csv_builder = builder

    def _inject_encoded_values(self, csv_reader: CsvFileReader, encoder: PhoneticChunkEncoder):
        """Injecte les données encodées dans les colonnes du fichier CSV créé."""
        prev_index = 0
        for chunk_index in range(csv_reader.num_chunks):
            chunk = csv_reader.get_column_chunk(self._request.column, chunk_index)
            encoded = encoder.encode(chunk)
            self._csv_builder.inject_values_in_chunks(encoded, prev_index)
            prev_index += len(encoded)


if __name__ == "__main__":
    filepath = "C:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv"
    encoded_filepath = FilePathCodec().encode(filepath)
    sample_request = {
        'encoded_filepath': encoded_filepath,
        'column': 'name_en',
        'phonetic': {
            'soundex': False,
            'metaphone': True,
            'metaphone3': True
        },
        'sep': None,
        'filename': "test.csv"
    }

    processor = PhoneticFileCreator(sample_request)
    processor.create()

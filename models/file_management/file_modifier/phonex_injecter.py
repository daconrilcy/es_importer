import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from config import Config
from models.file_management.file_modifier.csv_file_modifier import CsvChunkAutoModifier
from models.file_management.readers.csv_file_reader import CsvFileReader
from models.phonetc_basics.phonetic_dict_validator import PhoneticDictValidator
from models.phonetc_basics.chunk_encoder import PhoneticChunkEncoder

logger = logging.getLogger(__name__)


class PhonexCsvModifier:
    """
    Applique des algorithmes phonétiques sur une colonne d'un fichier CSV par chunk.
    Centralise la logique via PhoneticChunkEncoder.
    """

    def __init__(
            self,
            filepath: str,
            separator: Optional[str],
            source_column: str,
            phonex_dict: Dict[str, bool],
            config: Optional[Config] = None,
            same_file: bool = True
    ):
        self._config = config or Config()
        self._source_column = source_column
        self._filepath = filepath
        self._separator = separator
        self._phonex_dict = PhoneticDictValidator(phonex_dict).validate()
        self._same_file = same_file
        self._chunk_encoder = PhoneticChunkEncoder(
            phonex_dict=self._phonex_dict,
            source_column=self._source_column,
            config=self._config
        )
        self._csv_reader: Optional[CsvFileReader] = None

    def process(self) -> bool:
        """Exécute les transformations phonétiques configurées."""
        try:
            self._csv_reader = CsvFileReader(filepath=self._filepath, sep=self._separator, config=self._config)
        except Exception as e:
            logger.error(f"PhonexChunkModifier - Erreur d'initialisation du lecteur CSV : {e}")
            return False

        if not self._is_valid_source():
            return False

        # Demande la liste des colonnes générées à l'encodeur (en fonction du dict)
        output_columns = self._chunk_encoder.new_column_names

        if not output_columns:
            logger.warning("Aucun algorithme phonétique sélectionné.")
            return False

        if not self._apply_chunk_modifier(self._encode_chunk, output_columns):
            return False

        return True

    def _is_valid_source(self) -> bool:
        if not self._csv_reader or not self._csv_reader.check_column_exist(self._source_column):
            logger.error(f"PhonexChunkModifier - Colonne source '{self._source_column}' absente")
            return False
        return True

    def _encode_chunk(self, series: pd.Series) -> pd.DataFrame:
        return self._chunk_encoder.encode(series)

    def _apply_chunk_modifier(
            self, modify_func, output_columns
    ) -> bool:
        path_modified = Path(self._csv_reader.filepath).with_name(
            f"{Path(self._csv_reader.filepath).stem}_modified.csv")
        new_file_path = None if self._same_file else path_modified

        try:
            modifier = CsvChunkAutoModifier(
                csv_reader=self._csv_reader,
                source_column=self._source_column,
                modify_func=modify_func,
                output_columns=output_columns
            )
            modifier.process_and_save(new_file_path)
            return True
        except Exception as e:
            logger.error(f"PhonexChunkModifier - Erreur lors du traitement : {e}")
            return False


if __name__ == "__main__":
    filepath = "C:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv"
    separator = ";"
    source_column = "name_fr"
    phonex_dict = {"soundex": True, "metaphone": True, "metaphone3": True}
    chunk_modifier = PhonexCsvModifier(filepath, separator, source_column, phonex_dict, same_file=False)
    chunk_modifier.process()

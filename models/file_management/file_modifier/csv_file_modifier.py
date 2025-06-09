import csv
from pathlib import Path

import pandas as pd
from typing import Callable, Optional, List
import logging

from models.file_management.readers.csv_file_reader import CsvFileReader

logger = logging.getLogger(__name__)


class CsvChunkAutoModifier:
    """
    Applique une fonction de transformation à une colonne d'un CSV chunk par chunk,
    puis insère les colonnes résultantes juste après la colonne source.
    """

    def __init__(
            self,
            csv_reader: CsvFileReader,
            source_column: str,
            modify_func: Callable[[pd.Series], pd.DataFrame],
            output_columns: Optional[List[str]] = None,
    ) -> None:
        self.csv_reader = csv_reader
        self.source_column = source_column
        self.modify_func = modify_func
        self.output_columns = output_columns

    def _generate_modified_chunk(self, chunk: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Transforme un chunk en insérant les colonnes modifiées après la colonne source.
        """
        if self.source_column not in chunk.columns:
            logger.warning(f"Colonne '{self.source_column}' absente du chunk, chunk ignoré.")
            return None

        try:
            modified_df = pd.DataFrame(self.modify_func(chunk[self.source_column]))
        except Exception as e:
            logger.error(f"Erreur de transformation sur chunk: {e}")
            return None

        if self.output_columns and len(modified_df.columns) != len(self.output_columns):
            logger.error("Le nombre de colonnes retournées ne correspond pas à output_columns.")
            return None

        insert_index = chunk.columns.get_loc(self.source_column) + 1
        left = chunk.iloc[:, :insert_index].reset_index(drop=True)
        right = chunk.iloc[:, insert_index:].reset_index(drop=True)
        modified_df.columns = self.output_columns if self.output_columns else modified_df.columns

        return pd.concat([left, modified_df.reset_index(drop=True), right], axis=1)

    def process_and_save(self, output_path: Optional[str] = None) -> None:
        """
        Lance le traitement chunk par chunk et écrit le fichier modifié.
        """
        if output_path is None:
            output_path = Path(self.csv_reader.filepath)
        else:
            output_path = Path(output_path)
        first_chunk = True

        for chunk_index in range(self.csv_reader.num_chunks):
            chunk = self.csv_reader.get_chunk(chunk_index=chunk_index)
            modified_chunk = self._generate_modified_chunk(chunk)
            if modified_chunk is None:
                continue

            if first_chunk:
                modified_chunk.to_csv(
                    output_path, mode="w", index=False, encoding=self.csv_reader.encoding, sep=self.csv_reader.sep,
                    quoting=csv.QUOTE_ALL
                )
                first_chunk = False
            else:
                modified_chunk.to_csv(
                    output_path, mode="a", index=False, header=False,
                    encoding=self.csv_reader.encoding, sep=self.csv_reader.sep,
                    quoting=csv.QUOTE_ALL
                )


if __name__ == "__main__":
    file_path_test = "C:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv"
    output_path_test = "C:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82_modified.csv"
    source_column_test = "name_en"
    output_columns_test = ["name_en_upper"]


    def modify_func_test(series: pd.Series) -> pd.DataFrame:
        return pd.DataFrame({"name_en_upper": series.str.upper()})


    reader = CsvFileReader(file_path_test, sep=";")
    modifier = CsvChunkAutoModifier(reader, source_column_test, modify_func_test, output_columns_test)
    modifier.process_and_save(output_path_test)

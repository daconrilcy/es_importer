import logging
import shutil
from pathlib import Path
from typing import Optional, List, Union
from io import StringIO

import pandas as pd

from config import Config
from elastic_manager import ElasticManager
from models.file_management.file_utls import FileUtils
from models.file_management.readers.csv_file_reader import CsvFileReader

logger = logging.getLogger(__name__)


class CsvManualMultiColumnsBuilder:
    """
    Génère un nouveau CSV en ajoutant dynamiquement des colonnes vides à partir d'un fichier existant.
    Supporte les fichiers issus d'ElasticSearch (via file_id) ou d'un chemin local.
    Permet d'injecter ultérieurement des valeurs dans les colonnes nouvellement créées.
    """

    def __init__(
            self,
            source_column: str,
            new_columns: Union[List[str], str],
            file_id: Optional[str] = None,
            original_filepath: Optional[str] = None,
            separator: Optional[str] = None,
            chunk_size: Optional[int] = None,
            filename: Optional[str] = None,
            config: Optional[Config] = None
    ):
        config = config or Config()
        self.file_types = config.file_types
        self.source_column = source_column
        self.separator = separator
        self.new_columns = [new_columns] if isinstance(new_columns, str) else list(new_columns)
        self.chunk_size = chunk_size or 1000
        self.elastic_manager = ElasticManager(config)
        self.file_utils = FileUtils()
        self._output_csv: Optional[Path] = None

        if file_id:
            file_infos = self.elastic_manager.files_obj.get_one(file_id)
            if not file_infos:
                logger.error(f"Fichier non trouvé dans ElasticSearch pour l'id {file_id}")
                raise ValueError("Fichier non trouvé")
            self.source_filepath = Path(file_infos.filepath)
            self.separator = getattr(file_infos, "separator", None)
            encoding = getattr(file_infos, "encoding", "utf-8")
        elif original_filepath:
            self.source_filepath = Path(original_filepath)
            encoding = "utf-8"
        else:
            raise ValueError("Il faut fournir soit un file_id, soit un filepath.")

        self.reader = CsvFileReader(
            filepath=self.source_filepath,
            sep=self.separator,
            encoding=encoding,
            chunk_size=self.chunk_size,
        )

        if not self.reader.check_column_exist(self.source_column):
            raise ValueError(f"Colonne '{self.source_column}' non trouvée dans {self.source_filepath}")

        if filename:
            self.output_path = filename

    @property
    def auto_file_path(self) -> str:
        return "multicols_" + self.file_utils.generate_filename(ext=".csv")

    @property
    def output_path(self) -> Path:
        if not self._output_csv:
            self._output_csv = self.file_types.completions.folder_path / self.auto_file_path
        return self._output_csv

    @output_path.setter
    def output_path(self, filename: str):
        self._output_csv = self.file_types.completions.folder_path / filename

    def create_csv(self) -> None:
        """
        Crée un nouveau CSV contenant la colonne source et les colonnes vides.
        """
        if self.separator is None:
            self.separator = self.reader.sep
        for chunk_index in range(self.reader.num_chunks):
            chunk_values = self.reader.get_column_chunk(self.source_column, chunk_index, self.chunk_size)
            data = {self.source_column: chunk_values}

            for col in self.new_columns:
                data[col] = ["" for _ in chunk_values]

            df = pd.DataFrame(data)

            df.to_csv(
                self.output_path,
                index=False,
                sep=self.reader.sep,
                encoding=self.reader.encoding,
                mode='w' if chunk_index == 0 else 'a',
                header=chunk_index == 0,
                lineterminator="\n"
            )

    def inject_values_in_chunks(self, df_values: pd.DataFrame, start_row: int = 0) -> None:
        """
        Injecte les valeurs chunk par chunk à partir de `start_row`, sans recharger tout le fichier.

        Args:
            df_values: DataFrame contenant les nouvelles valeurs à injecter.
            start_row: Index de ligne du fichier à partir duquel injecter les données.
        """
        for col in self.new_columns:
            if col not in df_values.columns:
                raise ValueError(f"Colonne {col} manquante dans le DataFrame fourni")

        total_rows = sum(1 for _ in open(self.output_path, encoding=self.reader.encoding)) - 1
        max_required = start_row + len(df_values)
        if max_required > total_rows:
            raise ValueError("Le DataFrame à injecter dépasse la taille du fichier existant.")

        tmp_path = str(self.output_path) + ".tmp"
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()

        header = pd.read_csv(self.output_path, sep=self.reader.sep, nrows=0).columns.tolist()

        with open(self.output_path, encoding=self.reader.encoding) as infile:
            next(infile)  # skip header
            all_lines = infile.readlines()

        n_chunks = (total_rows // self.chunk_size) + (1 if total_rows % self.chunk_size else 0)

        with open(tmp_path, 'w', encoding=self.reader.encoding) as outfile:
            outfile.write(self.reader.sep.join(header) + "\n")

            for chunk_index in range(n_chunks):
                start = chunk_index * self.chunk_size
                end = min((chunk_index + 1) * self.chunk_size, total_rows)
                lines = all_lines[start:end]

                df_chunk = pd.read_csv(
                    StringIO("".join([self.reader.sep.join(header) + "\n"] + lines)),
                    sep=self.reader.sep,
                    dtype=str
                )

                for i in range(len(df_chunk)):
                    global_idx = start + i
                    if start_row <= global_idx < start_row + len(df_values):
                        for col in self.new_columns:
                            val = str(df_values.at[global_idx - start_row, col])
                            if pd.isna(df_chunk.at[i, col]) or df_chunk.at[i, col] == "":
                                df_chunk.at[i, col] = val

                df_chunk.to_csv(
                    outfile,
                    index=False,
                    sep=self.reader.sep,
                    header=False,
                    lineterminator="\n"
                )

        shutil.move(tmp_path, self.output_path)




if __name__ == "__main__":
    creator_test = CsvManualMultiColumnsBuilder(
        source_column="name_fr",
        new_columns=["name_en", "name_es", "name_it"],
        original_filepath="C:/dev/py/csv_importer/files/datas/curiexplore-pays.csv",
        chunk_size=10
    )

    creator_test.create_csv()

    data_to_inject_test = pd.DataFrame({
        "name_en": ["France", "Spain", "Italy"],
        "name_es": ["Francia", "España", "Italia"],
        "name_it": ["Francia", "Spagna", "Italia"],
    })

    creator_test.inject_values_in_chunks(data_to_inject_test)

    data_to_inject_test_n = pd.DataFrame({
        "name_en": ["Germany", "Poland", "Ukraine"],
        "name_es": ["Germania", "Polonia", "Ucrania"],
        "name_it": ["Germania", "Polandia", "Ucrania"],
    })

    creator_test.inject_values_in_chunks(data_to_inject_test_n, 3)

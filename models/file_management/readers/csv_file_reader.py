import math
from typing import List, Optional, Tuple

import pandas as pd

from config import Config
from models.file_management.readers.base_file_reader import BaseFileReader
from models.file_management.file_utls import FileUtils


class CsvFileReader(BaseFileReader):
    """
    Gère la lecture, la validation et l'extraction des données d'un fichier CSV.
    """

    def __init__(
            self,
            filepath: str,
            sep: Optional[str] = None,
            headers: Optional[List[str]] = None,
            encoding: str = "utf-8",
            chunk_size: Optional[int] = None,
            num_chunks: Optional[int] = None,
            config: Optional[Config] = None
    ):
        config = config or Config()
        self._headers: Optional[List[str]] = headers
        self._sep = sep
        self.is_sep_different = False
        self._nrows: Optional[int] = None
        self._chunk_size = chunk_size or config.chunksize
        self._num_chunks = num_chunks
        super().__init__(filepath, encoding)

    @property
    def nrows(self) -> int:
        """Nombre de lignes du fichier."""
        if self._nrows is None:
            self._nrows = self._count_lines()
        return self._nrows

    @property
    def chunk_size(self) -> int:
        """Taille utilisée pour le chunk."""
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: int):
        self._chunk_size = value

    @property
    def num_chunks(self) -> int:
        """Nombre total de chunks dans le fichier."""
        if not self._num_chunks:
            self._num_chunks = math.ceil(self.nrows / self.chunk_size)
        return self._num_chunks

    @num_chunks.setter
    def num_chunks(self, value: int):
        self._num_chunks = value

    @property
    def sep(self) -> str:
        """Retourne le séparateur utilisé dans le fichier."""
        if not self._sep or self._sep is None:
            self._sep = FileUtils.detect_separator(str(self.filepath), encoding=self.encoding)
            self.is_sep_different = True
        return self._sep

    @property
    def headers(self) -> List[str]:
        """Liste des entêtes du fichier CSV."""
        if self._headers is None:
            self._headers = self._load_headers()
        return self._headers

    @headers.setter
    def headers(self, value: List[str]):
        if isinstance(value, list):
            self._headers = value

    def _load_headers(self) -> List[str]:
        df = pd.read_csv(self.filepath, sep=self.sep, encoding=self.encoding, nrows=0, dtype=str)

        return list(df.columns)

    def _count_lines(self) -> int:
        with self.filepath.open(encoding=self.encoding) as f:
            return sum(1 for _ in f)

    def _read_csv(self, skiprows=None, nrows: Optional[int] = None) -> pd.DataFrame:
        return pd.read_csv(
            self.filepath,
            sep=self.sep,
            encoding=self.encoding,
            dtype=str,
            skiprows=skiprows,
            nrows=nrows
        )

    def get_chunk(self, chunk_size: Optional[int] = None, chunk_index: int = 0,
                  max_cols: Optional[int] = None) -> pd.DataFrame:
        """
        Récupère un chunk de données du fichier CSV, basé sur un index de bloc.
        Cette méthode repose sur read_partial() pour effectuer la lecture effective.

        :param chunk_size: Taille d’un chunk (nombre de lignes). Utilise self.chunk_size si non fourni.
        :param chunk_index: Index du chunk (0 = premier bloc).
        :param max_cols: Nombre maximum de colonnes à retourner (optionnel).
        :return: DataFrame du chunk demandé.
        """
        size = chunk_size or self.chunk_size
        start = chunk_index * size
        df = self.read_partial(start, size)
        return df.iloc[:, :max_cols] if max_cols else df

    def get_all(self, max_cols: Optional[int] = None) -> pd.DataFrame:
        """
        Charge l'intégralité du fichier.
        """
        if self.sep is None:
            self._sep = FileUtils.detect_separator(str(self.filepath), encoding=self.encoding)
        df = self._read_csv()
        return df.iloc[:, :max_cols] if max_cols else df

    def read_partial(self, start: int, size: int, **kwargs) -> pd.DataFrame:
        """
        Lit une portion du fichier CSV à partir d'une ligne donnée (index absolu).
        Cette méthode constitue la primitive de lecture partielle, utilisée pour toute lecture partielle personnalisée.

        :param start: Index absolu de la première ligne à lire (hors header).
        :param size: Nombre de lignes à lire.
        :return: DataFrame contenant les lignes demandées.
        """
        if start >= self.nrows:
            return pd.DataFrame(columns=self.headers)

        skiprows = range(1, start + 1) if start > 0 else None
        nrows = min(size, self.nrows - start)

        df = self._read_csv(skiprows=skiprows, nrows=nrows)
        return df

    def validate_structure(self) -> bool:
        """
        Vérifie si le fichier est lisible et contient au moins une ligne.
        """
        try:
            with self.filepath.open(encoding=self.encoding) as f:
                return bool(f.readline().strip())
        except (FileNotFoundError, OSError, UnicodeDecodeError):
            return False
        except ValueError:
            try:
                self._sep = FileUtils.detect_separator(str(self.filepath), encoding=self.encoding)
                self.is_sep_different = True
                with self.filepath.open(encoding=self.encoding) as f:
                    return bool(f.readline().strip())
            except (FileNotFoundError, OSError, UnicodeDecodeError, ValueError):
                return False

    def get_headers_and_chunk(self, chunk_size: Optional[int], chunk_index: int,
                              max_cols: Optional[int] = None) -> Tuple[List[str], pd.DataFrame]:
        """
        Retourne un tuple (headers, chunk).
        """
        return self.headers, self.get_chunk(chunk_size, chunk_index, max_cols)

    def get_column_values(self, column_name: str) -> List[str]:
        """
        Retourne toutes les valeurs d'une colonne.
        """
        if not self.check_column_exist(column_name):
            return []
        df = self.get_all()
        return df[column_name].tolist()

    def get_column_chunk(self, column_name: str, chunk_index: int = 0,
                         chunk_size: Optional[int] = None) -> List[str]:
        """
        Retourne un chunk des valeurs d'une colonne.
        """
        size = chunk_size or self.chunk_size
        start = chunk_index * size
        df = self.read_partial(start, size)
        return df[column_name].tolist()

    def check_column_exist(self, column_name: str) -> bool:
        """
        Vérifie si une colonne est presente dans le fichier
        :param column_name:
        :return:
        """
        if column_name not in self.headers:
            return False
        return True

if __name__ == "__main__":
    csv_file_reader_test = CsvFileReader(filepath="C:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv")
    print(csv_file_reader_test.headers)
    print(csv_file_reader_test.get_column_values("name_fr"))
    print(csv_file_reader_test.get_column_chunk("name_fr", 0, 10))
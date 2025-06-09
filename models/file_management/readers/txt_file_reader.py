from typing import List, Optional
from config import Config
from .csv_file_reader import CsvFileReader


class TxtFileReader(CsvFileReader):
    """
    Gère la lecture et l'extraction des données depuis un fichier
    TXT structuré (type CSV, mais séparateur \t par défaut).
    Hérite de CsvFileReader pour mutualiser toute la logique commune.
    """

    def __init__(
            self,
            filepath: str,
            sep: str = "\t",
            headers: Optional[List[str]] = None,
            encoding: str = "utf-8",
            chunk_size: Optional[int] = None,
            num_chunks: Optional[int] = None,
            config: Optional[Config] = None
    ):
        super().__init__(
            filepath=filepath,
            sep=sep,
            headers=headers,
            encoding=encoding,
            chunk_size=chunk_size,
            num_chunks=num_chunks,
            config=config
        )

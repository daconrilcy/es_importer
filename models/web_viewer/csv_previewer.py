from typing import List, Any, Optional, Dict
from pandas import DataFrame

from models.file_management.file_infos import FileInfos
from models.file_management.readers.csv_file_reader import CsvFileReader
from models.web_viewer.base_file_previewer import BaseFilePreviewer
from config import Config


class FileCsvPreviewer(BaseFilePreviewer):
    """
    Prévisualiseur pour les fichiers CSV, avec gestion de la lecture par chunk.
    """

    def __init__(self, chunk_size: Optional[int] = None,
                 list_files: Optional[List[FileInfos]] = None,
                 config: Optional[Config] = None
                 ):
        super().__init__(list_files, config=config)
        self._chunk_size = chunk_size or Config().preview_row_chunk
        self._chunk_index = 0
        self._cached_chunk_df: Optional[DataFrame] = None

    def _prepare_dict_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prépare les données nécessaires à partir du dictionnaire brut.
        """
        data = super()._prepare_dict_data(data)
        data.setdefault("chunk_index", 0)
        data.setdefault("sep", ",")
        data.setdefault("headers")
        data.setdefault("num_chunks")
        data.setdefault("chunk_size", self._chunk_size)

        self._chunk_index = data["chunk_index"]
        return data

    def build_from_file_infos(self, file_infos: FileInfos, chunk_index: Optional[int] = None) -> None:
        """
        Initialise l'objet à partir d'un objet FileInfos.
        """
        super().build_from_file_infos(file_infos)
        if chunk_index is not None:
            self._chunk_index = chunk_index

    def _create_reader_from_infos(self, file_infos: FileInfos, chunk_index: Optional[int] = None) -> CsvFileReader:
        """
        Crée un lecteur CSV à partir des informations de fichier.
        """
        return CsvFileReader(filepath=file_infos.filepath, sep=file_infos.separator)

    def _create_reader_from_dict(self, data: Dict[str, Any]) -> CsvFileReader:
        """
        Crée un lecteur CSV à partir d’un dictionnaire de données.
        """
        return CsvFileReader(
            filepath=data["filepath"],
            sep=data["sep"],
            chunk_size=data.get("chunk_size"),
            num_chunks=data.get("num_chunks"),
            headers=data.get("headers")
        )

    @property
    def headers(self) -> List[str]:
        """Renvoie les en-têtes du fichier CSV."""
        return self._reader.headers if self._reader else []

    @property
    def num_chunks(self) -> int:
        """Renvoie le nombre de chunks du fichier CSV."""
        return self._reader.num_chunks if self._reader else 0

    @property
    def rows(self) -> List[List[Any]]:
        """Renvoie les lignes du chunk courant."""
        return self._load_chunk().values.tolist()

    @property
    def sep(self) -> Optional[str]:
        """Renvoie le séparateur utilisé dans le fichier CSV."""
        return self._file_infos.separator if self._file_infos else None

    @property
    def chunk_index(self) -> int:
        """Renvoie l’index du chunk courant."""
        return self._chunk_index

    @property
    def chunk_size(self) -> int:
        """Renvoie la taille du chunk."""
        return self._chunk_size

    def _load_chunk(self) -> DataFrame:
        """
        Charge et met en cache le chunk courant s'il ne l'est pas encore.
        """
        if self._cached_chunk_df is None and self._reader:
            self._cached_chunk_df = self._reader.get_chunk(
                chunk_size=self._chunk_size,
                chunk_index=self._chunk_index
            )
        return self._cached_chunk_df if self._cached_chunk_df is not None else DataFrame()

    def reset_cache(self) -> None:
        """
        Réinitialise le cache du chunk courant.
        """
        self._cached_chunk_df = None

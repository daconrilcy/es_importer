from pathlib import Path
from typing import List, Any, Tuple

from models.file_management.filepath_codec import FilePathCodec

from elastic_manager import ElasticManager
from models.file_management.readers.csv_file_reader import CsvFileReader
from models.web_viewer.csv_previewer import FileCsvPreviewer
from config import Config
import logging

from models.web_viewer.mapping_previewer import MappingFilePreviewer

logger = logging.getLogger(__name__)



class FileLoader:
    """
    Classe utilitaire pour charger un fichier à partir de son identifiant Elasticsearch
    ou d'un chemin encodé, et fournir un objet de prévisualisation adapté.
    """

    def __init__(self, config: Config = None, chunk_size: int = None):
        self.config = config or Config()
        self.es_manager = ElasticManager(self.config)
        self.chunk_size = chunk_size or self.config.preview_row_chunk

    def get_full_preview(self, file_id: str, chunk_index: int = 0) -> FileCsvPreviewer:
        """
        Récupère un objet FileCsvPreviewer initialisé avec les données d'un fichier
        référencé dans Elasticsearch.

        Args:
            file_id (str): Identifiant du fichier dans Elasticsearch.
            chunk_index (int): Index du chunk à prévisualiser (par défaut 0).

        Returns:
            FileCsvPreviewer: Objet de prévisualisation des données CSV.

        Raises:
            LookupError: Si aucun fichier n'est trouvé pour l'identifiant donné.
            NotImplementedError: Si le type de fichier n'est pas pris en charge.
        """
        file_infos = self.es_manager.files_obj.get_one(file_id)
        if not file_infos:
            raise LookupError(f"Fichier introuvable dans Elasticsearch : id={file_id}")

        if (file_infos.type.name != self.config.file_types.datas.name
                and file_infos.type.name != self.config.file_types.mappings.name):
            # TODO: Gestion des autres types de fichiers
            logger.error(f"File Loader: Prévisualisation non prise en charge pour le type '{file_infos.type.name}'")
            raise NotImplementedError(
                f"File Loader: Prévisualisation non prise en charge pour le type '{file_infos.type.name}'"
            )

        return self._build_previewer_from_infos(file_infos, chunk_index, file_infos.type.name)

    def get_datas_preview(self, encoded_file_path: str,
                          chunk_index: int = 0,
                          num_chunks: int = None) -> Tuple[List[str], List[List[Any]]]:
        """
        Récupère les lignes d'un chunk de données d'un fichier CSV encodé.

        Args:
            encoded_file_path (str): Chemin encodé vers le fichier.
            chunk_index (int): Index du chunk à récupérer.
            num_chunks (int, optional): Nombre de chunks à charger. Défaut : None.

        Returns:
            List[List[Any]]: Lignes du fichier sous forme de liste.
        """
        previewer = FileCsvPreviewer(chunk_size=self.chunk_size)
        previewer.build_from_dict({
            "encodedFilepath": encoded_file_path,
            "chunk_index": chunk_index,
            "num_chunks": num_chunks,
            "type": self.config.file_types.datas.name
        })
        return previewer

    def get_rows_preview(
            self, encoded_file_path: str, chunk_index: int, num_chunks: int = None) -> List[List[Any]]:
        """
        Récupère les lignes d'un chunk de données d'un fichier CSV encodé.

        Args:
            encoded_file_path (str): Chemin encodé vers le fichier.
            chunk_index (int): Index du chunk à récupérer.
            num_chunks (int, optional): Nombre de chunks à charger. Défaut : None.

        Returns:
            List[List[Any]]: Lignes du fichier sous forme de liste.
        """
        previewer = FileCsvPreviewer(chunk_size=self.chunk_size)
        previewer.build_from_dict({
            "encodedFilepath": encoded_file_path,
            "chunk_index": chunk_index,
            "num_chunks": num_chunks,
            "type": self.config.file_types.datas.name
        })
        return previewer.rows

    def _build_previewer_from_infos(self, file_infos, chunk_index: int, type_file: str) -> FileCsvPreviewer:
        """
        Initialise un FileCsvPreviewer à partir des FileInfos fournis.

        Args:
            file_infos: Métadonnées du fichier.
            chunk_index (int): Index du chunk à prévisualiser.

        Returns:
            FileCsvPreviewer: Prévisualisation initialisée.
        """
        list_files = ElasticManager(Config()).files_obj.get_all_by_type(size=10000)
        previewer = None
        if type_file == self.config.file_types.datas.name:
            previewer = FileCsvPreviewer(chunk_size=self.chunk_size, list_files=list_files[type_file])
            previewer.build_from_file_infos(file_infos, chunk_index)
        elif type_file == self.config.file_types.mappings.name:
            previewer = MappingFilePreviewer(list_files=list_files[type_file],
                                             list_files_related_to=list_files[self.config.file_types.datas.name])
            previewer.build_from_file_infos(file_infos)

        return previewer

    def get_file_data_headers(self, encoded_filepath: str) -> List[str]:
        """
        Récupère les en-tetes des données d'un fichier CSV.

        Args:
            encoded_filepath (str): Chemin du fichier CSV.

        Returns:
            List[str]: Liste des en-tetes des données.
        """
        if encoded_filepath is None or not isinstance(encoded_filepath, str):
            return []
        filepath = FilePathCodec.decode(encoded_filepath)
        filepath = Path(filepath).resolve()
        if not Path(filepath).is_file():
            return []
        file_reader = CsvFileReader(filepath, chunk_size=self.chunk_size)
        return file_reader.headers

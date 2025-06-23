from typing import List

from config import Config
from elastic_manager import ElasticSearchTools
from models.file_management.file_infos import FileInfos
import logging

logger = logging.getLogger(__name__)


class FileInfosDocuments:
    """
    Gère les documents Elasticsearch basés sur la structure FileInfos (métadonnées de fichiers).
    Permet des actions typiques comme l'import, la mise à jour ou la suppression.
    """

    def __init__(self, es_tools: ElasticSearchTools, config: Config):
        self.es_tools = es_tools
        self.config = config or Config()
        self.index_name = self.config.index_files_name

    def import_file_infos(self, file_infos: List[FileInfos], expected_type: str = None) -> bool:
        """
        Transforme une liste de FileInfos en documents Elasticsearch, puis les importe.
        """
        documents = []
        for file_info in file_infos:
            if not file_info or not getattr(file_info, "filename", None):
                continue
            if expected_type and file_info.type.name != expected_type:
                file_info.type = expected_type
            documents.append(file_info.get_doc())

        if not documents:
            return False

        return self.es_tools.bulk_import(self.index_name, documents)

    def get_all(self, size: int = 100) -> List[FileInfos]:
        """
        Récupère tous les documents de l'index de fichiers au format FileInfos
        :param size:
        :return:
        """
        file_docs = self.es_tools.search_all(self.index_name, size=size)
        files_obj = []
        for file_doc in sorted(file_docs, key=lambda x: x.get("date_updated"), reverse=True):
            files_obj.append(FileInfos(doc=file_doc))
        return files_obj

    def get_all_by_type(self, size: int = 10000) -> List[FileInfos]:
        """
        Récupère tous les documents de l'index de fichiers au format FileInfos
        :param size:
        :return:
        """
        file_docs = self.es_tools.search_all(self.index_name, size=size, sorted_result=True)
        files_obj = {}
        for file_type in self.config.file_types.list:
            files_obj[file_type.name] = []

        if not file_docs:
            return files_obj

        for file_doc in file_docs:
            files_obj[file_doc["type"]].append(FileInfos(doc=file_doc))

        for type_key in files_obj:
            files_obj[type_key].sort(key=lambda x: x.date_updated, reverse=True)

        return files_obj

    def get_one(self, file_id: str) -> FileInfos | None:
        """
        Récupère un document de l'index de fichiers au format FileInfos
        :param file_id:
        :return:
        """
        file_doc = self.es_tools.get_doc_by_id(self.index_name, file_id)
        if not file_doc:
            return None
        return FileInfos(doc=file_doc)

    def get_by_type(self, file_type: str) -> List[FileInfos]:
        """
        Récupère tous les documents de l'index de fichiers au format FileInfos
        :param file_type:
        :return:
        """
        file_docs = self.es_tools.search_by_query(self.index_name, {"query": {"match": {"type": file_type}}})
        files_obj = []
        if not file_docs:
            return []

        for file_doc in sorted(file_docs, key=lambda x: x.get("date_updated"), reverse=True):
            files_obj.append(FileInfos(doc=file_doc))

        return files_obj

    def add(self, file_infos: FileInfos) -> bool:
        """
        Ajoute un FileInfos
        :param file_infos:
        :return:
        """
        return self.import_file_infos([file_infos])

    def delete(self, file_infos: FileInfos) -> bool:
        """
        Supprime un FileInfos
        :param file_infos:
        :return:
        """
        if not file_infos:
            logger.error("FileInfosDocuments : Tentative de suppression d'un FileInfos vide")
            return False
        if not file_infos.id:
            logger.info("FileInfosDocuments : Le FileInfos n'a pas d'id, tentative de suppression par filepath")
            if not file_infos.filepath:
                logger.error("FileInfosDocuments : Le FileInfos n'a pas de chemin de fichier, suppression impossible")
                return False
            file_infos = self.get_by_filename(file_infos.filename)
            if not file_infos:
                logger.error("FileInfosDocuments : le document n'a pas pu être trouvé, suppression impossible")
                return False

        return self.es_tools.delete_doc(self.index_name, file_infos.id)

    def get_by_filename(self, filename: str) -> FileInfos | None:
        """
        Récupère un document de l'index de fichiers au format FileInfos
        :param filename:
        :return:
        """
        file_docs = self.es_tools.search_by_query(self.index_name, {"query": {"match": {"filename": filename}}})
        if not file_docs or len(file_docs) == 0:
            logger.error("FileInfosDocuments : le document n'a pas pu'être trouvé, suppression impossible")
            return None
        file_doc = file_docs[0]
        print(file_doc)
        if not file_doc:
            return None
        return FileInfos(doc=file_doc)

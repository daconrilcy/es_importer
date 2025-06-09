from datetime import datetime, timezone
from typing import Dict, Any, Union, List

from elastic_manager import ElasticSearchTools


class ElasticFileDocuments:
    """
    Gère les opérations sur les documents de fichiers dans Elasticsearch.
    Utilise les outils de connexion et d'accès d'ElasticSearchTools.
    """

    def __init__(self, es_tools: ElasticSearchTools, index_name: str):
        self.es_tools = es_tools
        self.index_name = index_name

    def list_all(self, size: int = 100) -> Union[List[Dict[str, Any]], bool]:
        """
        Récupère tous les documents de l'index de fichiers.
        """
        return self.es_tools.search_all(self.index_name, size=size)

    def get_by_id(self, doc_id: str) -> Union[Dict[str, Any], bool]:
        """
        Récupère un document fichier par son ID.
        """
        return self.es_tools.get_doc_by_id(self.index_name, doc_id)

    def search_by_type(self, type_file: str) -> Union[List[Dict[str, Any]], bool]:
        """
        Recherche tous les documents fichiers correspondant à un type donné.
        """
        if not type_file:
            return False
        query = {"query": {"match": {"type": type_file}}}
        return self.es_tools.search_by_query(self.index_name, query)

    def update_doc(self, doc: Dict[str, Any]) -> bool:
        """
        Met à jour un document existant en utilisant son ID.
        """
        if not doc or not doc.get("_id"):
            return False
        doc_id = doc.pop("_id")
        doc.pop("id", None)
        return self.es_tools.update_doc(self.index_name, doc_id, doc)

    def delete_doc(self, doc_id: str) -> bool:
        """
        Supprime un document fichier par son ID.
        """
        return self.es_tools.delete_doc(self.index_name, doc_id)

    def add_doc(self, doc: Dict[str, Any]) -> bool:
        """
        Ajoute un document fichier à l'index.
        """
        if not doc or "type" not in doc or "file_name" not in doc:
            return False

        doc.setdefault("extension", doc["file_name"].split(".")[-1] if "." in doc["file_name"] else "")
        doc.setdefault("separator", ",")
        doc.setdefault("upload_date", datetime.now(timezone.utc).isoformat())
        doc.pop("id", None)
        doc.pop("_id", None)

        return self.es_tools.add_doc(self.index_name, doc)

    def bulk_add(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Importe une liste de documents de fichiers en mode bulk.
        """
        return self.es_tools.bulk_import(self.index_name, documents)

    def update_status_missing(self, doc_ids: List[str]) -> bool:
        """
        Marque les documents fichiers comme manquants via la propriété "status".
        """
        return self.es_tools.update_property(self.index_name, doc_ids, "status", "missing")

    def update_front_end_filename(self, file_id: str, front_end_filename: str) -> bool:
        """
        Met à jour le nom affiché (frontend) d'un document fichier.
        """
        return self.es_tools.update_property(self.index_name, [file_id],
                                             "front_end_filename", front_end_filename)

    def get_one_front_name(self, filename: str, type_file: str) -> str:
        """
        Récupère le nom affiché (frontend) d'un document fichier.
        """
        doc = self.es_tools.multicriteria_search(self.index_name, [{"filename": filename, "type": type_file}])
        if doc and len(doc) > 0:
            return doc[0].get("front_end_filename", filename)
        return filename

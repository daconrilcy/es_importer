"""
Gestionnaire pour la création d'index et l'importation de différents docs Elasticsearch.
"""
from datetime import datetime, timezone

from config import Config
from elastic_manager.estools import ElasticSearchTools
from models.file_infos import FileInfos


class ElasticSearchManager:
    """
    Classe pour la gestion des index et des opérations d'import Elasticsearch.
    """

    def __init__(self, config: Config = None, es_tools: ElasticSearchTools = None):
        self.config = config or Config()
        self._est = es_tools or ElasticSearchTools()

    @property
    def es_tools(self) -> ElasticSearchTools:
        """
        Retourne l'instance ElasticSearchTools.
        :return:
        """
        return self._est

    def recreate_index(self, index_name: str, mapping: dict) -> bool:
        """
        Supprime puis recrée un index avec un mapping donné.
        """
        if not self.es_tools.test_connection():
            print("❌ Échec de la connexion à Elasticsearch.")
            return False

        with self.es_tools.es_connection() as es:
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
                print(f"Index '{index_name}' supprimé avant recréation.")

            es.indices.create(index=index_name, body=mapping)
            print(f"✅ Index '{index_name}' créé avec succès.")

            if es.indices.exists(index=index_name):
                print(f"📌 Index '{index_name}' vérifié après création.")
            else:
                print(f"⚠️ Problème : l'index '{index_name}' n'existe pas après création.")

        return True

    def delete_index(self, index_name: str) -> bool:
        """
        Supprime un index s'il existe.
        """
        with self.es_tools.es_connection() as es:
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
                print(f"🗑️ Index '{index_name}' supprimé.")
                return True
            return False

    def show_list_datas(self, index_name: str, size: int = 10) -> list or bool:
        """
        Retourne la liste des documents dans un index.
        """
        if not self.es_tools.is_index_exist(index_name):
            return False

        with self.es_tools.es_connection() as es:
            response = es.search(index=index_name, size=size, body={"query": {"match_all": {}}})
            documents = [hit["_source"] for hit in response["hits"]["hits"]]
            print(f"📊 {len(documents)} documents trouvés dans l'index '{index_name}'.")
            return documents

    def show_index(self, index_name: str):
        """
        Affiche le mapping d'un index.
        """
        if not self.es_tools.is_index_exist(index_name):
            return False

        with self.es_tools.es_connection() as es:
            index = es.indices.get(index=index_name)
            print(f"📊 Mapping de l'index '{index_name}' : {index}")
            return index

    def import_from_files_obj_list(self, files_obj: list[FileInfos], type_file: str = None) -> bool:
        """
        Importe une liste d'objets FileInfos dans Elasticsearch.
        """
        if not files_obj:
            print("❌ Liste de fichiers vide ou None")
            return False

        docs = []
        for file_obj in files_obj:
            if not file_obj or not file_obj.file_name:
                print("❌ Fichier invalide ou sans nom")
                continue
            if type_file and file_obj.type.name != type_file:
                file_obj.type = type_file
            docs.append(file_obj.get_doc())

        if not docs:
            print("📊 Aucun document à importer.")
            return False

        if not self.es_tools.bulk_import(self.config.index_files_name, docs):
            print("❌ Échec de l'importation en bulk")
            return False

        print(f"✅ {len(docs)} fichiers importés dans l'index '{self.config.index_files_name}'.")
        return True

    def get_files_from_es(self) -> list:
        """
        Get files from elasticsearch
        :return: List of files
        """
        return self.es_tools.search_all(self.config.index_files_name)

    def get_files_by_type(self, type_file: str) -> list:
        """
        Get files from elasticsearch by type
        :param type_file: Type of file
        :return: List of files
        """
        if not type_file:
            print("❌ ElasticSearchManager.get_files_by_type: Invalid type_file")
            return []
        query = {
            "query": {
                "match": {
                    "type": type_file
                }
            }
        }
        return self.es_tools.search_by_query(self.config.index_files_name, query)

    def get_file_by_id(self, file_id: str) -> dict or bool:
        """
        Get a file from Elasticsearch by its id.
        :param file_id: File id
        :return: File document
        """
        return self.es_tools.get_doc_by_id(self.config.index_files_name, file_id)

    def get_files_types_from_es(self) -> list:
        """
        Get files types from elasticsearch
        :return: List of files types
        """
        return self.es_tools.search_all(self.config.index_files_type_name)

    def modify_file_in_index_files(self, doc: dict) -> bool:
        """
        Modify a file in the index files
        :param doc: Document to modify
        :return: True if the document is modified, False otherwise
        """
        if not doc:
            print("❌ ElasticSearchManager.modify_file_in_index_files: Invalid doc")
            return False
        if "_id" not in doc or not doc["_id"]:
            print("❌ ElasticSearchManager.modify_file_in_index_files: No id in doc")
            return False
        if "id" in doc:
            del doc["id"]
        doc_id = doc["_id"]
        del doc["_id"]
        return self.es_tools.update_doc(self.config.index_files_name, doc_id, doc)

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Elasticsearch by its id.
        :param file_id: File id
        :return: True if the file is deleted, False otherwise
        """
        return self.es_tools.delete_doc(self.config.index_files_name, file_id)

    def set_files_statut_to_missing(self, ids: list[str]) -> bool:
        """
        Set the statut of the files to missing
        :param ids: List of files id
        :return: True if the statut is set to missing, False otherwise
        """
        return self.es_tools.update_property(self.config.index_files_name, ids, "status", "missing")

    def add_file_to_index_files(self, doc: dict):
        """
        Add a file to the index files
        :param doc: Document to add
        :return: True if the document is added, False otherwise
        """

        if not doc:
            print("❌ ElasticSearchManager.add_file_to_index_files: Invalid doc")
            return False
        if "type" not in doc:
            print("❌ ElasticSearchManager.add_file_to_index_files: No type in doc")
            return False
        if "file_name" not in doc:
            print("❌ ElasticSearchManager.add_file_to_index_files: No file_name in doc")
            return False
        if "extension" not in doc or not doc["extension"] or doc["extension"] == "":
            extension = doc["file_name"].split(".")[-1] if "." in doc["file_name"] else ""
            doc["extension"] = extension
        if "separator" not in doc or not doc["separator"] or doc["separator"] == "":
            doc["separator"] = ","  # default separator
        if "upload_date" not in doc:
            upload_date = datetime.now(timezone.utc).isoformat()
            doc["upload_date"] = upload_date
        if "id" in doc:
            del doc["id"]
        if "_id" in doc:
            del doc["_id"]
        return self.es_tools.add_doc(self.config.index_files_name, doc)

    def get_es_types(self) -> list:
        """
        Get the elasticsearch types
        :return: List of types
        """
        return self.es_tools.search_all(self.config.index_es_types_name)

    def get_es_analyzers(self) -> list:
        """
        Get the elasticsearch analyzers
        :return: List of analyzers
        """
        return self.es_tools.search_all(self.config.index_es_analysers_name)


if __name__ == "__main__":
    esm_test = ElasticSearchManager()
    doc_tests = esm_test.get_files_from_es()
    for dt in doc_tests:
        print(dt)
    test_id = None
    if doc_tests:
        test_id = doc_tests[0]["_id"]
    if test_id is not None:
        print(test_id)
        doc_id_test = esm_test.get_file_by_id(test_id)
        print(doc_id_test)

"""
Description: Classe utilitaire pour se connecter à Elasticsearch.
"""
import uuid

from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError
from contextlib import contextmanager
from typing import Any, Dict, List, Union

from models.date_formater import MultiDateFormater


class ElasticSearchTools:
    """
    Outils de gestion directe d'une instance Elasticsearch.
    Gère la connexion et les opérations de base : création, suppression, mise à jour,
    recherche et importation en bulk de documents.
    """

    def __init__(self, host: str, username: str, password: str):
        self._host = host
        self._username = username
        self._password = password
        self._es: Elasticsearch | None = None
        self.connected: bool = False
        self._date_formater = MultiDateFormater()

    @contextmanager
    def es_connection(self):
        """
        Context manager pour gérer automatiquement la connexion/déconnexion.
        :return:
        """
        self.connect()
        try:
            yield self._es
        finally:
            self.disconnect()

    def connect(self):
        """
        Ouvre une connexion à Elasticsearch.
        :return:
        """

        if not self.connected or self._es is None:
            self._es = Elasticsearch(
                self._host,
                basic_auth=(self._username, self._password),
                verify_certs=False
            )
            self.connected = True

    def disconnect(self) -> bool:
        """
        Ferme la connexion à Elasticsearch.
        :return:
        """
        if self._es:
            try:
                self._es.close()
            except Exception as e:
                print(f"Erreur de fermeture: {e}")
                return False
            finally:
                self._es = None
                self.connected = False
        return True

    def test_connection(self) -> bool:
        """
        Teste la connexion à Elasticsearch.
        :return:
        """
        self.connect()
        try:
            self._es.info()
            return self._es.ping()
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
        finally:
            self.disconnect()

    def is_index_exist(self, index_name: str) -> bool:
        """
        Indique si un index existe.
        :param index_name:
        :return:
        """
        with self.es_connection() as es:
            return es.indices.exists(index=index_name)

    def search_all(self, index_name: str, size: int = 100,
                   sorted_result: bool = False, sort_by: str = "date_updated") -> Union[List[Dict[str, Any]], bool]:
        """
        Recherche tous les documents d'un index, triés par sort_key (ou date_updated).
        """
        if sorted_result and sort_by is not None:
            body_request = {
                "query": {"match_all": {}},
                "sort": [{sort_by: {"order": "desc"}}]
            }
        else:
            body_request = {"query": {"match_all": {}}}
        if not self.is_index_exist(index_name):
            return False
        with self.es_connection() as es:
            response = es.search(
                index=index_name,
                body=body_request,
                size=size
            )
            return [
                {**hit["_source"], "_id": hit["_id"]}
                for hit in response.get("hits", {}).get("hits", [])
            ]

    def search_by_query(self, index_name: str, query: dict, size: int = 1000) -> Union[List[Dict[str, Any]], bool]:
        """
        Recherche des documents d'un index en fonction d'une requête.
        :param index_name:
        :param size:
        :param query:
        :return:
        """

        if not self.is_index_exist(index_name):
            return False
        with self.es_connection() as es:
            response = es.search(index=index_name, body=query, size=size)
            return [
                {**hit["_source"], "_id": hit["_id"]}
                for hit in response.get("hits", {}).get("hits", [])
            ]

    def get_doc_by_id(self, index_name: str, doc_id: str) -> Union[Dict[str, Any], bool]:
        """
        Recherche un document par son identifiant.
        :param index_name:
        :param doc_id:
        :return:
        """

        if not self.is_index_exist(index_name):
            return False
        try:
            with self.es_connection() as es:
                response = es.get(index=index_name, id=doc_id)
        except Exception as e:
            print(f"❌ ElasticsearchGetter._get_doc_by_id: {e}")
            return False

        if "_source" not in response:
            return False
        if "_id" in response:
            response["_source"]["_id"] = response["_id"]
        return response["_source"]

    def delete_doc(self, index_name: str, doc_id: str) -> bool:
        """
        Supprime un document par son identifiant.
        :param index_name:
        :param doc_id:
        :return:
        """

        if not self.is_index_exist(index_name) or not doc_id:
            return False
        try:
            with self.es_connection() as es:
                es.delete(index=index_name, id=doc_id)
                es.indices.refresh(index=index_name)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du document {doc_id} dans l'index {index_name} : {e}")
            return False

    def update_property(self, index_name: str, list_doc_id: List[str], property_name: str, value: Any) -> bool:
        """
        Met à jour une propriété de plusieurs documents.
        :param index_name:
        :param list_doc_id:
        :param property_name:
        :param value:
        :return:
        """

        if not self.is_index_exist(index_name) or not list_doc_id:
            return False
        try:
            with self.es_connection() as es:
                for doc_id in list_doc_id:
                    if not doc_id:
                        continue
                    date_updated = self._date_formater.to_es()
                    es.update(index=index_name, id=doc_id, body={"doc": {property_name: value,
                                                                         "date_updated": date_updated}})
                es.indices.refresh(index=index_name)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour des documents {list_doc_id} dans l'index {index_name} : {e}")
            return False

    def add_doc(self, index_name: str, doc: Dict[str, Any]) -> bool:
        """
        Ajoute un document.
        :param index_name:
        :param doc:
        :return:
        """

        if not self.is_index_exist(index_name) or not doc:
            return False
        try:
            with self.es_connection() as es:
                es.index(index=index_name, body=doc)
                es.indices.refresh(index=index_name)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du document {doc} dans l'index {index_name} : {e}")
            return False

    def bulk_import(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """
        Importe une liste de documents dans un index Elasticsearch.
        Ajoute automatiquement 'date_updated' et 'sort_key' pour le tri.
        :param index_name: Nom de l'index.
        :param documents: Liste des documents à indexer.
        :return: True si succès, False sinon.
        """
        now = self._date_formater.to_es()
        actions = [
            {
                "_index": index_name,
                "_source": {
                    **{k: v for k, v in doc.items() if k not in ("id", "_id")},
                    "date_updated": now,
                }
            }
            for doc in documents
        ]
        try:
            with self.es_connection() as es:
                helpers.bulk(es, actions)
                es.indices.refresh(index=index_name)
            return True
        except (BulkIndexError, Exception) as e:
            print(f"❌ bulk_import error: {e}")
            return False

    def update_doc(self, index_name: str, doc_id: str, body: Dict[str, Any]) -> bool:
        """
        Met à jour un document dans un index.
        :param index_name:
        :param doc_id:
        :param body:
        :return:
        """

        if not self.is_index_exist(index_name) or not doc_id or not body:
            return False
        try:
            with self.es_connection() as es:
                es.update(index=index_name, id=doc_id, body={"doc": body})
                es.indices.refresh(index=index_name)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du document {doc_id} dans l'index {index_name} : {e}")
            return False

    def update_properties(self, index_name: str, doc_ids: List[str], updates: Dict[str, Any]) -> bool:
        """
        Met à jour plusieurs propriétés pour une liste de documents.
        :param index_name: Nom de l'index.
        :param doc_ids: Liste des IDs des documents à modifier.
        :param updates: Dictionnaire des propriétés à mettre à jour.
        :return: True si l'opération réussit, False sinon.
        """
        if not self.is_index_exist(index_name) or not doc_ids or not updates:
            return False
        try:
            with self.es_connection() as es:
                for doc_id in doc_ids:
                    if not doc_id:
                        continue
                    es.update(index=index_name, id=doc_id, body={"doc": updates})
                es.indices.refresh(index=index_name)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour multiple dans l'index {index_name} : {e}")
            return False

    def multicriteria_search(self, index_name: str, must_criteria: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        if not self.is_index_exist(index_name) or not must_criteria:
            return []

        # Construction des clauses 'term'
        converted_criterias = []
        for criteria in must_criteria:
            for key, value in criteria.items():
                converted_criterias.append({"term": {key: value}})

        # Construction de la requête Elasticsearch
        body_request = {
            "query": {
                "bool": {
                    "must": converted_criterias
                }
            }
        }

        try:
            with self.es_connection() as es:
                response = es.search(index=index_name, body=body_request)
                return [doc["_source"] for doc in response.get("hits", {}).get("hits", [])]
        except Exception as e:
            raise RuntimeError(f"❌ Erreur lors de la recherche Elasticsearch : {e}")
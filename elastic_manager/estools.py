"""
Description: Classe utilitaire pour se connecter à Elasticsearch.
"""
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError

from config import Config
from contextlib import contextmanager


class ElasticSearchTools:
    """
    Classe utilitaire pour se connecter à Elasticsearch.
    Gère la connexion et les opérations de base.
    """

    def __init__(self):
        config = Config()
        self._host = config.get_host_str()
        self._username = config.es_username
        self._password = config.es_password
        self._es: Elasticsearch | None = None
        self.connected: bool = False

    @property
    def es(self) -> Elasticsearch:
        """
        Retourne la connexion Elasticsearch.
        :return:
        """
        return self._es

    def connect(self):
        """
        Ouvre une connexion à Elasticsearch.
        :return:
        """
        if not self.connected or self._es is None:
            self._es = Elasticsearch([self._host], basic_auth=(self._username, self._password))
        self.connected = True

    def disconnect(self):
        """
        Ferme la connexion à Elasticsearch.
        :return:
        """
        if self._es is not None:
            self._es.close()
            self._es = None
            self.connected = False

    def test_connection(self) -> bool:
        """
        Teste la connexion à Elasticsearch.
        """
        self.connect()
        try:
            self._es.info()
            self._es.ping()
            print("Connexion à Elasticsearch réussie.")
            return True
        except Exception as e:
            print(f"Erreur de connexion à Elasticsearch : {e}")
            return False
        finally:
            self.disconnect()
            return True

    def is_index_exist(self, index_name: str) -> bool:
        """
        Vérifie si un index existe dans Elasticsearch.
        """
        if not index_name:
            print("❌ Nom d'index invalide")
            return False

        with self.es_connection() as es:
            return es.indices.exists(index=index_name)

    def search_all(self, index_name: str, size=100) -> dict or bool:
        """
        Récupère tous les documents d'un index.
        """
        if not self.is_index_exist(index_name):
            print(f"❌ Index {index_name} n'existe pas")
            return False

        with self.es_connection() as es:
            response = es.search(index=index_name, body={"query": {"match_all": {}}}, size=size)

        if not response or "hits" not in response or "hits" not in response["hits"]:
            print("❌ ElasticsearchGetter._get_docs_from_es: Invalid response format")
            return False

        documents = [
            {**hit["_source"], "_id": hit["_id"]}
            for hit in response["hits"]["hits"]
        ]

        return documents

    def search_by_query(self, index_name: str, query: dict) -> dict or bool:
        """
        Récupère des documents d'un index en fonction d'une requête.
        :param index_name: Nom de l'index
        :param query: Requête Elasticsearch
        :return: Liste de documents ou False en cas d'erreur
        """
        if not self.is_index_exist(index_name):
            print(f"❌ Index {index_name} n'existe pas")
            return False

        with self.es_connection() as es:
            response = es.search(index=index_name, body=query)

        if not response or "hits" not in response or "hits" not in response["hits"]:
            print("❌ ElasticsearchGetter._get_docs_from_es: Invalid response format")
            return False

        documents = [
            {**hit["_source"], "_id": hit["_id"]}
            for hit in response["hits"]["hits"]
        ]

        return documents

    def get_doc_by_id(self, index_name: str, doc_id: str) -> dict or bool:
        """
        Get a document from Elasticsearch by its id.
        :param index_name: Index name
        :param doc_id: Document id
        :return: Document
        """
        if not self.is_index_exist(index_name):
            print(f"ElasticsearchGetter._get_doc_by_id: Index {index_name} does not exist")
            return False
        try:
            with self.es_connection() as es:
                response = es.get(index=index_name, id=doc_id)
        except Exception as e:
            print(f"❌ ElasticsearchGetter._get_doc_by_id: {e}")
            return False

        if not response:
            print(f"ElasticsearchGetter._get_doc_by_id: Document {doc_id} not found")
            return False

        if "_source" not in response:
            print("ElasticsearchGetter._get_doc_by_id: Invalid response format")
            return False
        if '_id' in response:
            response["_source"]["_id"] = response["_id"]
        return response["_source"]

    def delete_doc(self, index_name, doc_id):
        """
        Supprime un document dans un index.
        :param index_name:
        :param doc_id:
        :return:
        """
        if not self.is_index_exist(index_name):
            print(f"❌ ElasticSearchTools.delete_doc : Index {index_name} n'existe pas")
            return False
        if not doc_id:
            print("❌ ElasticSearchTools.delete_doc : ID de document invalide")
            return False
        with self.es_connection() as es:
            try:
                es.delete(index=index_name, id=doc_id)
                print(f"🗑️ Document {doc_id} supprimé dans l'index {index_name}")
                self.es.indices.refresh(index=index_name)
                return True
            except Exception as e:
                print(f"❌ Erreur lors de la suppression du document {doc_id} dans l'index {index_name} : {e}")
                return False

    def update_property(self, index_name: str, list_doc_id: list[str], property_name: str, value) -> bool:
        """
        Met à jour une propriété d'une liste de doc dans un index.
        :param index_name:
        :param list_doc_id:
        :param property_name:
        :param value:

        :return: bool True si la mise à jour est réussie, False sinon
        """
        if not self.is_index_exist(index_name):
            print(f"❌ ElasticSearchTools.update_property : Index {index_name} n'existe pas")
            return False
        if not list_doc_id:
            print("❌ ElasticSearchTools.update_property : ID de document invalide")
            return False
        with self.es_connection() as ec:
            try:
                for doc_id in list_doc_id:
                    if not doc_id:
                        continue
                    try:
                        ec.update(index=index_name, id=doc_id, body={"doc": {property_name: value}})
                    except Exception as ex:
                        print(
                            f"❌ ElasticSearchTools.update_property : Erreur lors de la mise à jour "
                            f"de la propriété {property_name} pour le document {doc_id} : {ex}"
                        )
                        continue
                print(
                    f"📊 Propriété {property_name} mise à jour pour {len(list_doc_id)} "
                    f"documents dans l'index {index_name}")
                return True
            except Exception as e:
                print(
                    f"❌ Erreur lors de la mise à jour de la propriété {property_name} pour {len(list_doc_id)} "
                    f"documents dans l'index {index_name} : {e}")
                return False

    def add_doc(self, index_name: str, doc: dict) -> bool:
        """
        Ajoute un document dans un index.
        :param index_name:
        :param doc:
        :return:
        """
        if not self.is_index_exist(index_name):
            print(f"❌ ElasticSearchTools.add_doc : Index {index_name} n'existe pas")
            return False
        if not doc:
            print("❌ ElasticSearchTools.add_doc : Document invalide")
            return False
        with self.es_connection() as es:
            try:
                result = es.index(index=index_name, body=doc)
                print(f"✅ Document ajouté dans l'index {index_name} : {result}")
                self.es.indices.refresh(index=index_name)
                return True
            except Exception as e:
                print(f"❌ Erreur lors de l'ajout du document dans l'index {index_name} : {e}")
                return False

    def bulk_import(self, index_name: str, documents: list[dict]) -> bool:
        """
        Importe une liste de documents dans un index Elasticsearch.
        """
        actions = [{"_index": index_name, "_source": doc} for doc in documents]
        print(f"📊 Importation de {len(actions)} documents dans l'index '{index_name}'...")
        for doc in documents:
            if "id" in doc:
                del doc["id"]
            if "_id" in doc:
                if doc["_id"] is None:
                    del doc["_id"]
        try:
            with self.es_connection() as es:
                helpers.bulk(es, actions)
                print(f"✅ Importation terminée pour l'index '{index_name}'.")
                es.indices.refresh(index=index_name)
                count = es.count(index=index_name)
                print(f"📊 Total documents dans '{index_name}': {count['count']}")
                return True

        except BulkIndexError as e:
            print(f"❌ Erreur d'importation bulk : {len(e.errors)} erreurs.")
            for err in e.errors:
                print(err)
            return False

        except Exception as e:
            print(f"❌ Erreur inattendue : {e}")
            return False

    def update_doc(self, index_name: str, doc_id: str, body: dict):
        """
        Met à jour un document dans un index.
        :param index_name:
        :param doc_id:
        :param body:
        :return:
        """
        if not self.is_index_exist(index_name):
            print(f"❌ ElasticSearchTools.update_doc : Index {index_name} n'existe pas")
            return False
        if not doc_id:
            print("❌ ElasticSearchTools.update_doc : ID de document invalide")
            return False
        if not body:
            print("❌ ElasticSearchTools.update_doc : Body invalide")
            return False
        with self.es_connection() as es:
            try:
                result = es.update(index=index_name, id=doc_id, body={"doc": body})
                print(f"📊 Document {doc_id} mis à jour dans l'index {index_name} : {result}")
                self.es.indices.refresh(index=index_name)
                return True
            except Exception as e:
                print(f"❌ Erreur lors de la mise à jour du document {doc_id} dans l'index {index_name} : {e}")
                return False

    @contextmanager
    def es_connection(self):
        """
        Context manager pour gérer automatiquement la connexion/déconnexion.
        """
        self.connect()
        try:
            yield self._es
        finally:
            self.disconnect()

from elastic_manager import ElasticSearchTools
from typing import Dict, Any, Union


class ElasticIndexManager:
    """
    Gère la création, suppression et consultation des index Elasticsearch.
    Utilise ElasticSearchTools pour les interactions bas niveau.
    """

    def __init__(self, es_tools: ElasticSearchTools):
        self.es_tools = es_tools

    def recreate(self, index_name: str, mapping: dict) -> bool:
        """
        Supprime puis recrée un index avec un nouveau mapping.
        """
        if not self.es_tools.test_connection():
            return False

        with self.es_tools.es_connection() as es:
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
            es.indices.create(index=index_name, body=mapping)

        return self.es_tools.is_index_exist(index_name)

    def delete(self, index_name: str) -> bool:
        """
        Supprime un index s'il existe.
        """
        with self.es_tools.es_connection() as es:
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
                return True
        return False

    def get_mapping(self, index_name: str) -> Union[Dict[str, Any], bool]:
        """
        Retourne le mapping d'un index.
        """
        if not self.es_tools.is_index_exist(index_name):
            return False
        with self.es_tools.es_connection() as es:
            return es.indices.get(index=index_name)
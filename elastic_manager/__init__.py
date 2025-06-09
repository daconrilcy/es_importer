from typing import Optional

from config import Config
from elastic_manager.estools import ElasticSearchTools
from elastic_manager.files.doc import ElasticFileDocuments
from elastic_manager.files.obj_cls import FileInfosDocuments
from elastic_manager.index_manager import ElasticIndexManager


class ElasticManager:
    """
    Orchestrateur principal de gestion Elasticsearch.
    Aggrège les composants de gestion : fichiers, métadonnées, index.
    """

    def __init__(self, config: Optional[Config] = None):
        config = config or Config()
        self.config = config
        self.tools = ElasticSearchTools(
            host=config.get_host_str(),
            username=config.es_username,
            password=config.es_password
        )
        self.index = ElasticIndexManager(self.tools)
        self.files = ElasticFileDocuments(self.tools, config.index_files_name)
        self.files_obj = FileInfosDocuments(self.tools, config)


if __name__ == "__main__":
    em_test = ElasticManager(Config())
    front_end_filename_test = em_test.files.get_one_front_name(type_file="datas", filename="curiexplore-pays.csv")
    print(front_end_filename_test)

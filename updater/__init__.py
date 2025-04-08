from config import Config
from converter import MultiConverter
from elastic_manager import ElasticSearchManager
from models.folder_types import FoldersTypes


class MultiUpdater:
    """
    Update the indexes of the application
    """

    def __init__(self, config: Config):
        if config is None:
            config = Config()
        self.config = config
        self.es_importer = ElasticSearchManager(config)
        self.folders_manager = FoldersTypes(config)
        self.converter = MultiConverter(config)

    def update_file_list_index(self):
        """
        Update the file list index
        :return: True if the index is updated, False otherwise
        """
        files_list = self.es_importer.get_files_from_es()
        files_list_obj = self.converter.doc_files_to_file_obj(files_list)
        files_to_add = self.folders_manager.get_files_list_not_in_list(files_list_obj)
        missing_files = self.folders_manager.get_missing_files(files_list_obj)
        print(missing_files)
        docs_to_add = self.converter.files_obj_to_docs(files_to_add)
        if len(missing_files) > 0:
            print(f"📊 MultiUpdater.update_file_list_index: {len(missing_files)} missing files")
            self.es_importer.set_files_statut_to_missing(missing_files)
        result = self.es_importer.bulk_import(self.config.index_files_name, docs_to_add)

        return result


if __name__ == "__main__":
    esg_test = ElasticSearchManager()
    cfg = Config()
    updater = MultiUpdater(cfg)
    updater.update_file_list_index()
    docs_files = esg_test.get_files_from_es()
    for df in docs_files:
        print(df)

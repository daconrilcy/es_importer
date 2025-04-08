"""
This module is used to initialize the configuration of the application.
"""
import csv
import os.path

from config import Config
from converter import MultiConverter
from elastic_manager import ElasticSearchManager
from models.folder_types import FoldersTypes
from initialize.index_details import IndexDetails
from initialize.initconfigfiles import InitConfigFiles


class InitialeConfig:
    """
    Initialize the configuration of the application
    Create the bases indexes in elasticsearch
    """

    def __init__(self):
        self.config = Config()
        self.indexes_infos = InitConfigFiles(self.config)
        self.importer = ElasticSearchManager(self.config)
        self.folders = FoldersTypes(self.config)
        self.converter = MultiConverter(self.config)

    def _verifie_or_create_test_csv(self):
        """
        Check if the test.csv file exists, if not create it
        :return: True if the file exists, False otherwise
        """
        file_name = "test.csv"
        folder_name = self.folders.data_folder.name
        filepath = self.folders.get_filepath_by_es_type_filename(folder_name, file_name)
        if not os.path.isfile(filepath):
            print(f"📊 {file_name} file not found in {folder_name} - Creating it")
            with open(filepath, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "name", "type", "size", "path", "date"])
                writer.writerow(["1", "test", "txt", "100", "C:/test", "2021-01-01"])
                writer.writerow(["2", "test2", "csv", "200", "C:/test2", "2021-01-02"])
            print(f"📊 {file_name} file created in {folder_name}")
        else:
            print(f"📊 {file_name} file found in {folder_name}")

    def _create_es_index(self, index_infos: IndexDetails):
        """
        Create an index in elasticsearch
        :param index_infos: IndexDetails
        :return: True if the index is created, False otherwise
        """
        if index_infos is None:
            print("❌ InitialeConfig._create_es_index: index_infos is None")
            return False
        return self.importer.recreate_index(index_infos.index_name, index_infos.mapping)

    def create_files_index(self):
        """
        Create the file type index in elasticsearch
        :return: True if the index is created, False otherwise
        """
        indexe_infos = self.indexes_infos.index_files
        if indexe_infos is None:
            print("❌ InitialeConfig.create_files_index: indexe_infos is None")
            return False
        return self._create_es_index(indexe_infos)

    def create_types_index(self):
        """
        Create the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        indexe_infos = self.indexes_infos.index_types
        if indexe_infos is None:
            print("❌ InitialeConfig.create_types_index: indexe_infos is None")
            return False
        return self._create_es_index(indexe_infos)

    def create_es_types_index(self):
        """
        Create the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        indexe_infos = self.indexes_infos.index_es_types
        if indexe_infos is None:
            print("❌ InitialeConfig.create_types_index: indexe_infos is None")
            return False
        return self._create_es_index(indexe_infos)

    def create_es_analyser_index(self):
        """
        Create the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        indexe_infos = self.indexes_infos.index_es_analysers
        if indexe_infos is None:
            print("❌ InitialeConfig.create_types_index: indexe_infos is None")
            return False
        return self._create_es_index(indexe_infos)

    def _fill_index(self, index_infos: IndexDetails):
        """
        Fill the index in elasticsearch
        :param index_infos: IndexDetails
        :return: True if the index is created, False otherwise
        """
        if index_infos is None:
            print("❌ InitialeConfig._fill_index: index_infos is None")
            return False
        docs = index_infos.datas
        if docs is None or docs is False:
            print(f"📊 InitialeConfig._fill_index: ❌ No datas to import in {index_infos.index_name} index")
            return False
        return self.importer.es_tools.bulk_import(index_infos.index_name, docs)

    def _fill_files_index(self):
        """
        Fill the file type index in elasticsearch
        :return: True if the index is created, False otherwise
        """
        return self._fill_index(self.indexes_infos.index_files)

    def _fill_types_index(self):
        """
        Fill the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        return self._fill_index(self.indexes_infos.index_types)

    def _fill_es_types_index(self):
        """
        Fill the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        return self._fill_index(self.indexes_infos.index_es_types)

    def _fill_es_analyser_index(self):
        """
        Fill the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        return self._fill_index(self.indexes_infos.index_es_analysers)

    def create_fully_files_index(self):
        """
        Create and fill the file type index in elasticsearch
        :return: True if the index is created, False otherwise
        """
        if self.create_files_index():
            if self._fill_files_index():
                if self._add_additionnal_files_in_folders():
                    return True
        return False

    def create_fully_types_index(self):
        """
        Create and fill the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        if self.create_types_index():
            if self._fill_types_index():
                return True
        return False

    def create_fully_es_types_index(self):
        """
        Create and fill the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        if self.create_es_types_index():
            if self._fill_es_types_index():
                return True
        return False

    def create_fully_es_analyser_index(self):
        """
        Create and fill the types index in elasticsearch wich contains the types of files
        :return: True if the index is created, False otherwise
        """
        if self.create_es_analyser_index():
            if self._fill_es_analyser_index():
                return True
        return False

    def creates_indexes(self) -> None:
        """
        Create and fill the indexes in elasticsearch
        :return: None
        """
        print("***********************start********************************")
        if self.create_fully_types_index():
            print("📊 Types index created")
        else:
            print("❌ Types index not created")
        print("***********************************************************")
        if self.create_fully_files_index():
            print("📊 Files index created")
        else:
            print("❌ Files index not created")
        print("***********************************************************")
        if self.create_fully_es_types_index():
            print("📊 ES Types index created")
        else:
            print("❌ ES Types index not created")
        print("***********************************************************")
        if self.create_fully_es_analyser_index():
            print("📊 ES Analyser index created")
        else:
            print("❌ ES Analyser index not created")
        print("***************************end*****************************")

    def _add_additionnal_files_in_folders(self) -> bool:
        """
        Check if there are additionnal files in the folder
        :return: True if there are additionnal files, False otherwise
        """

        files_in_es = self.importer.get_files_from_es()
        if files_in_es is None:
            return False
        if self.folders.list_folder is None:
            return False

        files_obj_qualified = self.converter.doc_files_to_file_obj(files_in_es)
        files_not_in_folder = self.folders.get_files_list_not_in_list(files_obj_qualified)

        if len(files_not_in_folder) == 0:
            print("📊 InitialeConfig._check_folder_for_additionnal_files: ❌ No files to import")
            return False
        self.importer.import_from_files_obj_list(files_not_in_folder)
        print(f"📊 {len(files_not_in_folder)} new Files imported in {self.config.index_files_name} index")
        return True

    def run(self):
        """
        Initialize the configuration of the application
        :return: None
        """
        self._verifie_or_create_test_csv()
        self.creates_indexes()


if __name__ == "__main__":
    ic_test = InitialeConfig()
    ic_test.run()
    print(ic_test.importer.show_list_datas("file_details"))
    print(ic_test.importer.show_list_datas("file_types"))
    print(ic_test.importer.show_list_datas("es_types", 100))
    print(ic_test.importer.show_list_datas("es_analysers", 100))

    #print(ic_test.importer.delete_index("file_details"))

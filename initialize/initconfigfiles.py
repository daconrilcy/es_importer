import json
import os

from config import Config
from initialize.index_details import IndexDetails


class InitConfigFiles:
    """
    Class used to initialize the configuration files
    """

    def __init__(self, config):
        if config is None:
            config = Config()
        self.folder = config.config_folder
        self.infos_file_path = config.es_init_infos
        self._index_files_name = config.index_files_name
        self._index_types_name = config.index_files_type_name
        self._index_es_types_name = config.index_es_types_name
        self._index_es_analysers_name = config.index_es_analysers_name
        self.infos_config = None
        self._index_files = None
        self._index_types = None
        self._index_es_types = None
        self._index_es_analysers = None
        self._create_config_files()

    @property
    def index_files(self) -> IndexDetails:
        """
        return es index files details
        :return:
        """
        return self._index_files

    @property
    def index_types(self) -> IndexDetails:
        """
        return es index types details
        :return:
        """
        return self._index_types

    @property
    def index_es_types(self) -> IndexDetails:
        """
        return es index types details
        :return:
        """
        return self._index_es_types

    @property
    def index_es_analysers(self) -> IndexDetails:
        """
        return es index types details
        :return:
        """
        return self._index_es_analysers

    def _create_config_files(self):
        """
        Create the configuration files
        :return:
        """
        if self.infos_config is None:
            self._read_infos_file()
        if self.infos_config is not None:
            self._index_files = self._get_index_details(self._index_files_name)
            self._index_types = self._get_index_details(self._index_types_name)
            self._index_es_types = self._get_index_details(self._index_es_types_name)
            self._index_es_analysers = self._get_index_details(self._index_es_analysers_name)

    def _read_infos_file(self):
        with open(self.infos_file_path, encoding="utf-8") as file:
            self.infos_config = json.load(file)

    def _get_index_details(self, attr_name: str):
        """
        Get the index details
        :param attr_name: Index name
        :return: Index details
        """
        if attr_name is None:
            print("InitConfigFiles._get_index_details: attr_name is None")
            return None
        if self.infos_config is None:
            self._read_infos_file()
        if self.infos_config is not None:
            if attr_name not in self.infos_config:
                print(f"InitConfigFiles._get_index_details: {attr_name} not in self.infos_config")
                return None
            mapping_filename = self.infos_config[attr_name]["mapping_file"]
            if mapping_filename is None:
                print("InitConfigFiles._get_index_details: mapping_filename is None")
                return None
            mapping_datas = self._mapping_datas(mapping_filename)
            file_datas_path = self.folder + self.infos_config[attr_name]["datas_file"]
            return IndexDetails(self.infos_config[attr_name]["index_name"],
                                mapping_datas, file_datas_path)
        return None

    def _mapping_datas(self, mapping_datas_filename: str):
        if mapping_datas_filename is None:
            print("❌ InitConfigFiles._mapping_datas: mapping_datas_filename is None")
            return {}
        file_path = self.folder + mapping_datas_filename
        if not os.path.isfile(file_path):
            print(f"❌ InitConfigFiles._mapping_datas: {file_path} does not exist")
            return {}
        try:
            with open(file_path, encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"❌ InitConfigFiles._mapping_datas: {e}")
            return {}


if __name__ == "__main__":
    icf_test = InitConfigFiles(None)
    print(icf_test.index_files.index_name)
    print(icf_test.index_files.mapping)
    print(icf_test.index_files.datas_filepath)
    print(icf_test.index_files.datas)
    print(icf_test.index_types.index_name)
    print(icf_test.index_types.mapping)
    print(icf_test.index_types.datas_filepath)

import os

import bcrypt
from dotenv import load_dotenv

from utils import manage_folder_name, manage_filepath


class Config:
    """
    Configuration class
    Manage all the configuration of the application
    """

    def __init__(self):
        self._host = None
        self._port = None
        self._app_web_secret = None
        self._es_username = None
        self._es_password = None
        self._app_username = None
        self._app_password = None

        self._default_sep = None
        self._default_ext = None

        # folders
        self._root_folder = None
        self._files_folder = None
        self._config_folder = None
        self._data_folder = None
        self._mapping_folder = None
        self._importer_folder = None
        self._process_folder = None
        self._bulk_folder = None
        self._temp_folder = None
        self._other_folder = None
        self._base_template_files_folder = None
        self._base_template_files_preview_folder = None

        # files
        self._es_types_file_path = None
        self._es_init_infos = None

        #variables
        self._chunksize = None

        #indexes
        self._index_files_name = "file_details"
        self._index_files_type_name = "file_types"
        self._index_es_types_name = "es_types"
        self._index_es_analysers_name = "es_analyser"

        self.load()

    @property
    def app_web_secret(self) -> str:
        """
        Get the application web secret
        :return: app_web_secret: str
        """
        return self._app_web_secret

    @property
    def es_username(self) -> str:
        """
        Get the elasticsearch username
        :return: username: str
        """
        return self._es_username

    @property
    def es_password(self) -> str:
        """
        Get the elasticsearch password
        :return: es_password: str
        """
        return self._es_password

    @property
    def default_sep(self) -> str:
        """
        Get the default separator
        :return: : str
        """
        return self._default_sep

    @property
    def default_ext(self) -> str:
        """
        Get the default extension
        :return: extension: str
        """
        return self._default_ext

    @property
    def root_folder(self) -> str:
        """
        Get the root folder path
        root folder contains all the folders
        :return: folder path: str
        """
        return self._root_folder

    @property
    def config_folder(self) -> str:
        """
        Get the config folder path
        config folder contains all the configuration files
        :return: folder path: str
        """
        return self._config_folder

    @property
    def data_folder(self) -> str:
        """
        Get the data folder path
        data folder contains all the raw data files
        :return: folder path: str
        """
        return self._data_folder

    @property
    def mapping_folder(self) -> str:
        """
        Get the mapping folder path
        mapping folder contains all the mapping files
        :return: folder path: str
        """
        return self._mapping_folder

    @property
    def importer_folder(self) -> str:
        """
        Get the importer folder path
        importer folder contains all the importer files
        :return: folder path: str
        """
        return self._importer_folder

    @property
    def process_folder(self) -> str:
        """
        Get the process folder path
        process folder contains all the processor files (list of importers)
        :return: folder path: str
        """
        return self._process_folder

    @property
    def bulk_folder(self) -> str:
        """
        Get the bulks folder path
        bulks folder contains all the bulks files
        :return: folder path: str
        """
        return self._bulk_folder

    @property
    def temp_folder(self) -> str:
        """
        Get the temp folder path
        temp folder contains all the temporary files
        :return: folder path: str
        """
        return self._temp_folder

    @property
    def base_template_files_folder(self) -> str:
        """
        Get the base template files Folder path
        :return: Folder path: str
        """
        return self._base_template_files_folder

    @property
    def base_template_files_preview_folder(self) -> str:
        """
        Get the base template files preview Folder path
        :return: Folder path: str
        """
        return self._base_template_files_preview_folder

    @property
    def es_types_file_path(self) -> str:
        """
        Get the elasticsearch types file path
        :return: : File path: str
        """
        return self._es_types_file_path

    @property
    def es_init_infos(self) -> str:
        """
        Get the elasticsearch init infos file path
        :return: : File path: str
        """
        return self._es_init_infos

    @property
    def chunksize(self) -> int:
        """
        Get the chunksize
        :return: chunksize: int
        """
        return self._chunksize

    @property
    def index_files_name(self) -> str:
        """
        Get the index files name
        :return: index_files_name: str
        """
        return self._index_files_name

    @property
    def index_files_type_name(self) -> str:
        """
        Get the index files type
        :return: index_files_type: str
        """
        return self._index_files_type_name

    @property
    def index_es_types_name(self) -> str:
        """
        Get the index es types name
        :return: index_es_types_name: str
        """
        return self._index_es_types_name

    @property
    def index_es_analysers_name(self) -> str:
        """
        Get the index es analysers name
        :return: index_es_analysers_name: str
        """
        return self._index_es_analysers_name

    def load(self):
        """
        Load all the configuration from environment variables
        :return: None
        """
        load_dotenv()

        # Elasticsearch
        self._host = os.getenv("HOST", "localhost")
        self._port = os.getenv("PORT", 9200)
        self._app_web_secret = os.getenv("APP_WEB_SECRET", "ma_super_cle_secrete")
        self._es_username = os.getenv("ES_USERNAME", "elastic")
        self._es_password = os.getenv("ES_PASSWORD", "changeme")
        self._app_username = os.getenv("APP_USERNAME", "admin")
        self._app_password = os.getenv("APP_PASSWORD", "password").encode('utf-8')

        # Default separator
        self._default_sep = os.getenv("DEFAULT_SEP", ",")
        self._default_ext = os.getenv("DEFAULT_EXT", ".csv")

        # Folder paths
        self._root_folder = os.getenv("BASE_ROOT", os.path.dirname(os.path.abspath(__file__)))
        self._files_folder = self._load_folder(os.getenv("FILES_FOLDER", "files"))

        self._config_folder = self._load_folder(os.getenv("CONFIG_FOLDER", "config"), self._files_folder)
        self._data_folder = self._load_folder(os.getenv("DATA_FOLDER", "datas"), self._files_folder)
        self._mapping_folder = self._load_folder(os.getenv("MAPPING_FOLDER", "mappings"), self._files_folder)
        self._importer_folder = self._load_folder(os.getenv("IMPORTER_FOLDER", "importers"), self._files_folder)
        self._process_folder = self._load_folder(os.getenv("PROCESS_FOLDER", "processors"), self._files_folder)
        self._bulk_folder = self._load_folder(os.getenv("BULK_FOLDER", "bulks"), self._files_folder)
        self._temp_folder = self._load_folder(os.getenv("TEMP_FOLDER", "temp"), self._files_folder)
        self._base_template_files_folder = manage_folder_name(os.getenv("BASE_TEMPLATE_FILES_FOLDER",
                                                                        "types_base_layout"))
        self._base_template_files_preview_folder = manage_folder_name(
            os.getenv("BASE_TEMPLATE_FILES_PREVIEW_FOLDER", "preview_files"))

        # Files
        self._es_types_file_path = manage_filepath(self._config_folder, os.getenv("ES_TYPES_FILE", "es_types.json"),
                                                   "json")
        self._es_init_infos = self.config_folder + os.getenv("ES_INDEX_FILE", "_list_es_config_files.json")

        # Variables
        self._chunksize = int(os.getenv("FILE_CHUNK_SIZE", 100000))

        # Indexes
        self._index_files_name = os.getenv("BASE_INDEX_FILES", "index_files")
        self._index_files_type_name = os.getenv("BASE_INDEX_FILES_TYPE", "file_types")
        self._index_es_types_name = os.getenv("BASE_INDEX_ES_TYPES", "es_types")
        self._index_es_analysers_name = os.getenv("BASE_INDEX_ES_ANALYSERS", "es_analyser")

    def _load_folder(self, folder_name: str, parent_folder: str = None) -> str:
        """
        Load folder path from environment variables
        :param folder_name: str
        :return: str
        """
        if parent_folder is None:
            parent_folder = self._root_folder
        folder_name = manage_folder_name(folder_name)
        folder_path = os.path.join(parent_folder, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def get_host_str(self) -> str:
        """
        Get the connection string for Elasticsearch
        :return: Connection string: str
        """
        return f"{self._host}:{self._port}"

    def check_app_credentials(self, username: str, password: str) -> bool:
        """
        Check the application credentials
        :param username: str
        :param password: str
        :return: bool
        """
        crypt_password = password.encode()
        return (self._app_username == username and
                bcrypt.checkpw(crypt_password, self._app_password))


if __name__ == "__main__":
    config = Config()
    print(config.data_folder)
    print(config.mapping_folder)
    print(config.importer_folder)
    print(config.process_folder)
    print(config.bulk_folder)
    print(config.temp_folder)
    print(config.es_types_file_path)
    print(config.chunksize)
    print(config.default_sep)
    print(config.default_ext)
    print(config.config_folder)

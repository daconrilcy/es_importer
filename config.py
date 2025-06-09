import os
from pathlib import Path
from typing import Optional

import bcrypt
from dotenv import load_dotenv

from models.file_type import FileTypes
from utils import manage_folder_name


class Config:
    """
    Classe de configuration principale pour charger les variables d'environnement,
    configurer les chemins et initialiser les paramètres globaux de l'application.
    """

    def __init__(self) -> None:
        self._load_environment()
        self._init_paths()
        self._load_settings()
        self._set_file_types()

    def _load_environment(self) -> None:
        """Charge les fichiers .env appropriés."""
        root_path = Path(__file__).resolve().parent
        env_base = Path(root_path) / ".env"
        env_dev = Path(root_path) / ".env.test"
        env_prod = Path(root_path) / ".env.prod"
        load_dotenv(env_base)
        env_file = {
            "PROD": env_prod,
            "DEV": env_dev
        }.get(os.getenv("APP_ENV"))

        if env_file:
            load_dotenv(env_file, override=True)
        else:
            print("NO ENV FILE")

        self.environment = env_file

    def _init_paths(self) -> None:
        """Initialise les chemins nécessaires à l'application."""
        self._root_folder = Path(os.getenv("BASE_ROOT", Path(__file__).resolve().parent))
        self._files_folder = self._ensure_folder(os.getenv("FILES_FOLDER", "files"))
        self._config_folder = self._ensure_folder(os.getenv("CONFIG_FOLDER", "config"), self._files_folder)
        self._temp_folder = self._ensure_folder(os.getenv("TEMP_FOLDER", "temp"), self._files_folder)
        self._base_template_files_folder = manage_folder_name(
            os.getenv("BASE_TEMPLATE_FILES_FOLDER", "types_base_layout")
        )
        self._base_template_files_preview_folder = manage_folder_name(
            os.getenv("BASE_TEMPLATE_FILES_PREVIEW_FOLDER", "preview_files")
        )
        self._ext_lib_folder_path = self._root_folder / os.getenv("EXTERNAL_LIB_FOLDER", "ext_lib")

    def _load_settings(self) -> None:
        """Charge les paramètres de configuration depuis les variables d'environnement."""
        self._host = os.getenv("HOST", "localhost")
        self._port = os.getenv("PORT", "9200")
        self._app_web_secret = os.getenv("APP_WEB_SECRET", "ma_super_cle_secrete")
        self._es_username = os.getenv("ES_USERNAME", "elastic")
        self._es_password = os.getenv("ES_PASSWORD", "changeme")
        self._app_username = os.getenv("APP_USERNAME", "admin")
        self._app_password = os.getenv("APP_PASSWORD", "password").encode()

        self._default_sep = os.getenv("DEFAULT_SEP", ",")
        self._default_ext = os.getenv("DEFAULT_EXT", ".csv")

        es_file_name = os.getenv("ES_TYPES_LIST_FILENAME", "es_types.json")
        self._es_types_filepath = str(self._config_folder / es_file_name)
        self._es_init_infos = str(self._config_folder / os.getenv("ES_INDEX_FILE", "_list_es_config_files.json"))
        self._es_analyzers_filepath = str(self._config_folder / os.getenv("ANALYSER_LIST_FILENAME", "es_analyser.json"))
        self._filepath_salt = os.getenv("FILEPATH_SALT", "default_salt")
        self._filepath_phonex = self._ext_lib_folder_path / os.getenv("FILE_PHONEX", "libphonex.so")
        self._filepath_metaphone = self._ext_lib_folder_path / os.getenv("FILE_METAPHONE", "libmetaphone.so")
        self._filepath_metaphone3 = self._ext_lib_folder_path / os.getenv("FILE_METAPHONE3",
                                                                          "libmetaphone3.so")

        self._chunksize = int(os.getenv("FILE_CHUNK_SIZE", "100000"))
        self._max_csv_file_size = int(os.getenv("MAX_CSV_FILE_SIZE", str(100 * 1024 * 1024)))
        self._preview_row_chunk = int(os.getenv("PREVIEW_ROW_CHUNK", "100"))

        self._index_files_name = os.getenv("BASE_INDEX_FILES", "file_details")
        self._index_files_type_name = os.getenv("BASE_INDEX_FILES_TYPE", "file_types")
        self._index_es_types_name = os.getenv("BASE_INDEX_ES_TYPES", "es_types")
        self._index_es_analysers_name = os.getenv("BASE_INDEX_ES_ANALYSERS", "es_analyser")
        self._buffer_phonex = int(os.getenv("BUFFER_PHONEX", 4096))

    def _ensure_folder(self, folder_name: str, parent_folder: Optional[Path] = None) -> Path:
        """Crée un dossier si nécessaire et retourne son chemin absolu."""
        parent_folder = parent_folder or self._root_folder
        path = parent_folder / manage_folder_name(folder_name)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _set_file_types(self) -> None:
        """Initialise le gestionnaire de types de fichiers."""
        file_types_config_path = self._root_folder / os.getenv("FILE_TYPES_LIST_FILE_NAME", "file_types.json")
        self._file_types = FileTypes(
            config_file_path=file_types_config_path,
            base_folder_path=self._files_folder
        )

    def get_host_str(self) -> str:
        """Retourne la chaîne de connexion Elasticsearch."""
        return f"{self._host}:{self._port}"

    def check_app_credentials(self, username: str, password: str) -> bool:
        """Vérifie si les identifiants fournis correspondent à ceux de l'application."""
        return self._app_username == username and bcrypt.checkpw(password.encode(), self._app_password)

    def get_lib_path(self, lib_name: str) -> Path:
        """
        Retourne le chemin vers le fichier de librairie phonétique.
        :param lib_name:
        :return:
        """
        if lib_name == "metaphone":
            return self._filepath_metaphone
        elif lib_name == "metaphone3":
            return self._filepath_metaphone3
        else:
            return self._filepath_phonex

    # Propriétés exposées
    @property
    def app_web_secret(self) -> str:
        return self._app_web_secret

    @property
    def es_username(self) -> str:
        return self._es_username

    @property
    def es_password(self) -> str:
        return self._es_password

    @property
    def default_sep(self) -> str:
        return self._default_sep

    @property
    def default_ext(self) -> str:
        return self._default_ext

    @property
    def root_folder(self) -> Path:
        return self._root_folder

    @property
    def config_folder(self) -> Path:
        return self._config_folder

    @property
    def files_folder(self) -> Path:
        return self._files_folder

    @property
    def temp_folder(self) -> Path:
        return self._temp_folder

    @property
    def base_template_files_folder(self) -> str:
        return self._base_template_files_folder

    @property
    def base_template_files_preview_folder(self) -> str:
        return self._base_template_files_preview_folder

    @property
    def es_types_filepath(self) -> str:
        return self._es_types_filepath

    @property
    def es_analyzers_filepath(self) -> str:
        return self._es_analyzers_filepath

    @property
    def es_init_infos(self) -> str:
        return self._es_init_infos

    @property
    def file_types(self) -> FileTypes:
        return self._file_types

    @property
    def chunksize(self) -> int:
        return self._chunksize

    @property
    def max_csv_file_size(self) -> int:
        return self._max_csv_file_size

    @property
    def preview_row_chunk(self) -> int:
        return self._preview_row_chunk

    @property
    def filepath_salt(self) -> str:
        return self._filepath_salt

    @property
    def index_files_name(self) -> str:
        return self._index_files_name

    @property
    def index_files_type_name(self) -> str:
        return self._index_files_type_name

    @property
    def index_es_types_name(self) -> str:
        return self._index_es_types_name

    @property
    def index_es_analysers_name(self) -> str:
        return self._index_es_analysers_name

    @property
    def ext_lib_folder_path(self) -> Path:
        return self._ext_lib_folder_path

    @property
    def filepath_phonex(self) -> Path:
        return self._filepath_phonex

    @property
    def buffer_phonex(self) -> int:
        return self._buffer_phonex

    @property
    def filepath_metaphone(self) -> Path:
        return self._filepath_metaphone

    @property
    def filepath_metaphone3(self) -> Path:
        return self._filepath_metaphone3


if __name__ == "__main__":
    config = Config()
    for attr in config.__dict__:
        print(f"{attr}: {getattr(config, attr)}")

    print(config.filepath_phonex)

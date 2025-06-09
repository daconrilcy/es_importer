import os
import pytest
from dotenv import load_dotenv
from config import Config


@pytest.fixture(scope="module", autouse=True)
def load_test_env():
    """Charge le fichier .env de test avant l'exécution des tests."""
    env_path = os.path.join(os.path.dirname(__file__), "../.env.test")
    load_dotenv(dotenv_path=env_path, override=True)


def test_config_instantiation():
    cfg = Config()
    assert isinstance(cfg, Config)


def test_app_credentials_valid():
    cfg = Config()
    assert cfg.check_app_credentials("admin", "Adm1n@pp2025") is True


def test_app_credentials_invalid():
    cfg = Config()
    assert not cfg.check_app_credentials("wrong", "password")
    assert not cfg.check_app_credentials("admin", "wrong")


def test_get_host_str():
    cfg = Config()
    assert cfg.get_host_str() == f"{cfg._host}:{cfg._port}"


def test_properties_not_none():
    cfg = Config()
    assert all([
        cfg.app_web_secret,
        cfg.es_username,
        cfg.es_password,
        cfg.default_sep,
        cfg.default_ext,
        cfg.root_folder,
        cfg.config_folder,
        cfg.files_folder,
        cfg.temp_folder,
        cfg.base_template_files_folder,
        cfg.base_template_files_preview_folder,
        cfg.es_types_file_path,
        cfg.es_init_infos,
        cfg.file_types,
        cfg.chunksize > 0,
        cfg.max_csv_file_size > 0,
        cfg.preview_row_chunk > 0,
        cfg.filepath_salt,
        cfg.index_files_name,
        cfg.index_files_type_name,
        cfg.index_es_types_name,
        cfg.index_es_analysers_name
    ])

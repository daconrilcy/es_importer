import json
import tempfile
from pathlib import Path
import pytest
from models.file_type import FileTypes
from models.file_type import FileType

# Exemple de données de configuration
FILE_TYPES_CONFIG = [
    {
        "name": "datas",
        "accepted_extensions": ["csv", "json"],
        "description": "Data files"
    },
    {
        "name": "mappings",
        "accepted_extensions": ["yaml"],
        "description": "Mapping definitions"
    }
]


@pytest.fixture
def config_file_and_path():
    """Crée un fichier temporaire de config JSON et un dossier simulé."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "file_types.json"
        base_path = Path(tmpdir) / "my_base_folder"
        base_path.mkdir(parents=True, exist_ok=True)

        for item in FILE_TYPES_CONFIG:
            item["base_path"] = str(base_path)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(FILE_TYPES_CONFIG, f)

        yield str(config_path), str(base_path)


def test_init_with_valid_config(config_file_and_path):
    config_path, base_path = config_file_and_path
    ft = FileTypes(config_path, base_path)

    assert len(ft.list) == 2
    assert isinstance(ft.get("datas"), FileType)
    assert ft.get("mappings").description == "Mapping definitions"


def test_case_insensitive_lookup(config_file_and_path):
    config_path, base_path = config_file_and_path
    ft = FileTypes(config_path, base_path)

    assert ft.get("DATAS") is not None
    assert ft.is_type("Mappings") is True
    assert ft.get("unknown") is None


def test_named_accessors(config_file_and_path):
    config_path, base_path = config_file_and_path
    ft = FileTypes(config_path, base_path)

    assert ft.datas.name == "datas"
    assert ft.mappings.name == "mappings"
    assert ft.importers is None  # Non défini dans le fichier JSON


def test_invalid_config_file_path_raises():
    with pytest.raises(ValueError, match="Fichier de configuration"):
        FileTypes(config_file_path="invalid.json", base_folder_path=".")


def test_invalid_base_folder_path_raises(tmp_path):
    # Crée un fichier JSON valide
    config_path = tmp_path / "types.json"
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(FILE_TYPES_CONFIG, f)

    with pytest.raises(ValueError, match="Le dossier de base"):
        FileTypes(config_file_path=str(config_path), base_folder_path="/non/existant")


def test_str_output(config_file_and_path):
    config_path, base_path = config_file_and_path
    ft = FileTypes(config_path, base_path)

    out = str(ft)
    assert "FileTypes" in out
    assert "datas" in out

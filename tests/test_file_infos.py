import pytest
from models.file_infos import FileInfos


@pytest.fixture
def sample_doc():
    return {
        "_id": "123",
        "filename": "test.csv",
        "initial_filename": "test.csv",
        "original_filename": "frontend_display",
        "type": "datas",
        "extension": "csv",
        "upload_date": "2024-05-05T10:00:00Z",
        "separator": ",",
        "description": "Test file",
        "status": "uploaded"
    }


def test_file_infos_properties(sample_doc):
    infos = FileInfos(sample_doc)

    assert infos.id == "123"
    assert infos.filename == "example.csv"
    assert infos.original_filename == "original.csv"
    assert infos.front_end_filename == "frontend_display"
    assert infos.type.name == "datas"
    assert infos.extension == "csv"
    assert infos.created_at == "2024-05-05T10:00:00Z"
    assert infos.separator == ","
    assert infos.description == "Test file"
    assert infos.status == "uploaded"
    assert infos.filepath is not None


def test_get_doc_contains_correct_keys(sample_doc):
    infos = FileInfos(sample_doc)
    doc = infos.get_doc()

    expected_keys = {"filename", "original_filename", "type", "extension", "separator", "status", "upload_date", "id"}
    assert expected_keys.issubset(doc.keys())

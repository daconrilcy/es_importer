import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.file_infos import FileInfos
from models.file_type import FileType


class TestFileInfos(unittest.TestCase):

    def setUp(self):
        self.valid_doc = {
            "_id": "123",
            "filename": "test.csv",
            "original_filename": "original.csv",
            "front_end_filename": "frontend",
            "type": "datas",
            "extension": "csv",
            "upload_date": "2024-01-01T00:00:00Z",
            "separator": ",",
            "description": "Test file",
            "status": "processed"
        }

    @patch("models.file_infos.FileUtils.manage_filepath", return_value="/mock/folder/test.csv")
    @patch("models.file_infos.Config")
    def test_initialize_from_doc(self, mock_config_cls, mock_manage_filepath):
        mock_file_type = MagicMock(spec=FileType)
        mock_file_type.name = "datas"
        mock_file_type.folder_path = "/mock/folder"
        mock_config = mock_config_cls.return_value
        mock_config.file_types.get.return_value = mock_file_type

        file_infos = FileInfos(self.valid_doc)

        self.assertEqual(file_infos.id, "123")
        self.assertEqual(file_infos.filename, "test.csv")
        self.assertEqual(file_infos.original_filename, "original.csv")
        self.assertEqual(file_infos.front_end_filename, "frontend")
        self.assertEqual(file_infos.type_name, "datas")
        self.assertEqual(file_infos.extension, "csv")
        self.assertEqual(file_infos.created_at, "2024-01-01T00:00:00Z")
        self.assertEqual(file_infos.separator, ",")
        self.assertEqual(file_infos.description, "Test file")
        self.assertEqual(file_infos.status, "processed")
        self.assertEqual(file_infos.filepath, "/mock/folder/test.csv")

    def test_get_doc(self):
        mock_file_type = MagicMock(spec=FileType)
        mock_file_type.name = "datas"

        file_infos = FileInfos()
        file_infos.id = 456
        file_infos.filename = "sample.csv"
        file_infos.original_filename = "original.csv"
        file_infos.front_end_filename = "original"
        file_infos.extension = "csv"
        file_infos.separator = ";"
        file_infos.status = "new"
        file_infos.created_at = "2025-01-01T10:00:00Z"
        file_infos._type = mock_file_type

        doc = file_infos.get_doc()
        self.assertEqual(doc["filename"], "sample.csv")
        self.assertEqual(doc["original_filename"], "original.csv")
        self.assertEqual(doc["type"], "datas")
        self.assertEqual(doc["extension"], "csv")
        self.assertEqual(doc["separator"], ";")
        self.assertEqual(doc["status"], "new")
        self.assertIn("upload_date", doc)
        self.assertEqual(doc["id"], 456)

    def test_str_output(self):
        fi = FileInfos()
        output = str(fi)
        self.assertTrue(output.startswith("FileInfos("))

    @patch("models.file_infos.FileUtils.manage_filepath")
    def test_setters(self, mock_manage_filepath):
        mock_manage_filepath.side_effect = lambda folder, name, ext=None: f"{folder}/{name}"

        fi = FileInfos()
        mock_file_type = MagicMock(spec=FileType)
        mock_file_type.name = "datas"
        mock_file_type.folder_path = "/mock/folder"
        fi._type = mock_file_type

        fi.filename = "file.csv"
        self.assertEqual(fi.filename, "file.csv")
        self.assertEqual(fi.filepath, "/mock/folder/file.csv")

        fi.extension = "csv"
        self.assertEqual(fi.extension, "csv")
        self.assertEqual(fi.filepath, "/mock/folder/file.csv")

        fi.original_filename = "orig.csv"
        self.assertEqual(fi.original_filename, "orig.csv")

        fi.front_end_filename = "front"
        self.assertEqual(fi.front_end_filename, "front")

        fi.created_at = "2023-01-01"
        self.assertEqual(fi.created_at, "2023-01-01")

        fi.separator = ";"
        self.assertEqual(fi.separator, ";")

        fi.description = "desc"
        self.assertEqual(fi.description, "desc")

        fi.status = "done"
        self.assertEqual(fi.status, "done")

    @patch("models.file_infos.Config")
    def test_type_setter(self, mock_config_cls):
        mock_file_type = MagicMock(spec=FileType)
        mock_file_type.name = "datas"
        mock_config = mock_config_cls.return_value
        mock_config.file_types.get.return_value = mock_file_type

        fi = FileInfos()
        fi.type = "datas"
        self.assertEqual(fi.type.name, "datas")

        fi.type = mock_file_type
        self.assertIs(fi.type, mock_file_type)

        fi.type = None
        self.assertIsNone(fi.type)

    def test_invalid_doc_raises(self):
        with self.assertRaises(ValueError):
            FileInfos({"filename": "test.csv"})  # no type


if __name__ == '__main__':
    unittest.main()

# Fichier : tests/initialise_test/test_initial_config.py

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from initialize import InitialConfig


class TestInitialConfig(unittest.TestCase):

    @patch("initialize.ScanFolderTools")
    @patch("initialize.TestFileFactory")
    @patch("initialize.ElasticManager")
    @patch("initialize.InitConfigFiles")
    @patch("initialize.Config")
    def setUp(self, mock_config, mock_initfiles, mock_elastic, mock_testfilefactory, mock_scanner):
        self.mock_config = MagicMock()
        self.mock_config.file_types.datas.folder_path = "/fake/folder"
        self.mock_config.file_types.list = ["/folderA", "/folderB"]
        self.mock_config.index_files_name = "index_files"
        mock_config.return_value = self.mock_config

        self.mock_initfiles = MagicMock()
        mock_initfiles.return_value = self.mock_initfiles

        self.mock_elastic = MagicMock()
        mock_elastic.return_value = self.mock_elastic

        self.mock_testfilefactory = MagicMock()
        mock_testfilefactory.return_value = self.mock_testfilefactory

        self.mock_scanner = MagicMock()
        mock_scanner.return_value = self.mock_scanner

        self.ic = InitialConfig()

    @patch("initialize.Path.exists", return_value=False)
    def test_ensure_test_csv_exists_creates_file(self, mock_exists):
        self.ic._ensure_test_csv_exists()
        self.mock_testfilefactory.create_datas_test_file.assert_called_once()

    @patch("initialize.Path.exists", return_value=True)
    def test_ensure_test_csv_exists_skips_creation_if_exists(self, mock_exists):
        self.ic._ensure_test_csv_exists()
        self.mock_testfilefactory.create_datas_test_file.assert_not_called()

    def test_create_and_fill_index_none(self):
        self.assertFalse(self.ic._create_and_fill_index(None))

    def test_create_and_fill_index_failed_creation(self):
        index = MagicMock()
        index.index_name = "dummy"
        index.mapping = {}
        self.ic.elastic.index.recreate.return_value = False
        self.assertFalse(self.ic._create_and_fill_index(index))

    def test_create_and_fill_index_no_data(self):
        index = MagicMock()
        index.index_name = "dummy"
        index.mapping = {}
        index.datas = None
        self.ic.elastic.index.recreate.return_value = True
        self.assertTrue(self.ic._create_and_fill_index(index))

    def test_create_and_fill_index_with_data(self):
        index = MagicMock()
        index.index_name = "dummy"
        index.mapping = {}
        index.datas = [{"id": 1}]
        self.ic.elastic.index.recreate.return_value = True
        self.ic.elastic.tools.bulk_import.return_value = True
        self.assertTrue(self.ic._create_and_fill_index(index))

    def test_import_additional_files_none(self):
        self.ic.elastic.files_obj.get_all.return_value = []
        self.mock_scanner.get_missing_files_by_folder.return_value = {}
        self.assertFalse(self.ic._import_additional_files())

    def test_import_additional_files_success(self):
        self.ic.elastic.files_obj.get_all.return_value = []
        self.mock_scanner.get_missing_files_by_folder.return_value = {
            "folderA": [Path("/folderA/file.csv")]
        }
        result = self.ic._import_additional_files()
        self.assertTrue(result)
        self.ic.elastic.files_obj.import_file_infos.assert_called_once()

    @patch.object(InitialConfig, "_create_and_fill_index", return_value=True)
    @patch.object(InitialConfig, "_import_additional_files", return_value=True)
    def test_create_all_indexes(self, mock_import, mock_create):
        self.ic.indexes.index_types = MagicMock()
        self.ic.indexes.index_files = MagicMock()
        self.ic.indexes.index_es_types = MagicMock()
        self.ic.indexes.index_es_analysers = MagicMock()

        self.ic.create_all_indexes()
        self.assertEqual(mock_create.call_count, 4)
        mock_import.assert_called_once()

    @patch.object(InitialConfig, "_ensure_test_csv_exists")
    @patch.object(InitialConfig, "create_all_indexes")
    def test_run(self, mock_create, mock_ensure):
        self.ic.run()
        mock_ensure.assert_called_once()
        mock_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from pandas import DataFrame
from models.web_viewer.csv_previewer import FileCsvPreviewer


def mock_path_open(*args, **kwargs):
    json_data = '''[
        {
            "name": "datas",
            "accepted_extensions": [".csv"],
            "base_path": "C:/mock"
        }
    ]'''
    file_mock = MagicMock()
    file_mock.read.return_value = json_data
    file_context = MagicMock()
    file_context.__enter__.return_value = file_mock
    file_context.__exit__.return_value = False
    return file_context




class TestFileCsvPreviewer(unittest.TestCase):

    def setUp(self):
        self.mock_file_infos = MagicMock()
        self.mock_file_infos.filepath = "/fake/path.csv"
        self.mock_file_infos.separator = ","
        self.mock_file_infos.id = "123"
        self.mock_file_infos.front_end_filename = "fichier_test"
        self.mock_file_infos.type.name = "datas"

        self.mock_reader = MagicMock()
        self.mock_reader.headers = ["col1", "col2"]
        self.mock_reader.num_chunks = 2
        self.mock_reader.get_chunk.return_value = DataFrame([[1, 2], [3, 4]])

    @patch("pathlib.Path.open", new_callable=lambda: mock_path_open)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("models.readers.csv_file_reader.CsvFileReader")
    def test_build_from_dict(self, mock_csvreader, mock_is_file, mock_exists, mock_open):
        data = {
            "filepath": "/datas/path.csv",
            "sep": ",",
            "filename": "fichier_test",
            "type": "datas"
        }
        mock_csvreader.return_value = self.mock_reader
        previewer = FileCsvPreviewer()
        previewer.build_from_dict(data)
        self.assertEqual(previewer.headers, ["col1", "col2"])

    @patch("pathlib.Path.open", new_callable=lambda: mock_path_open)
    @patch("pathlib.Path.stat", return_value=MagicMock(st_size=123))
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("models.readers.csv_file_reader.CsvFileReader")
    def test_build_from_dict(self, mock_csvreader, mock_is_file, mock_exists, mock_stat, mock_open):
        mock_csvreader.return_value = self.mock_reader
        previewer = FileCsvPreviewer()
        previewer.build_from_file_infos(self.mock_file_infos)
        self.assertEqual(previewer.file_infos, self.mock_file_infos)

    def test_rows_and_cache(self):
        previewer = FileCsvPreviewer()
        previewer._reader = self.mock_reader
        previewer._chunk_index = 0
        rows = previewer.rows
        self.assertEqual(rows, [[1, 2], [3, 4]])

    def test_properties(self):
        previewer = FileCsvPreviewer()
        previewer._file_infos = self.mock_file_infos
        previewer._encoded_filepath = "abc"
        previewer._chunk_index = 1
        self.assertEqual(previewer.id, "123")
        self.assertEqual(previewer.front_end_filename, "fichier_test")
        self.assertEqual(previewer.sep, ",")
        self.assertEqual(previewer.type_name, "datas")
        self.assertEqual(previewer.chunk_index, 1)

    def test_reset_cache(self):
        previewer = FileCsvPreviewer()
        previewer._cached_chunk_df = DataFrame([[1, 2]])
        previewer.reset_cache()
        self.assertIsNone(previewer._cached_chunk_df)


if __name__ == "__main__":
    unittest.main()

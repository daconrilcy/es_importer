import unittest
from unittest.mock import patch, mock_open
from models.file_management.readers.json_file_reader import JsonFileReader


class TestJsonFileReader(unittest.TestCase):

    @patch("models.file_management.readers.base_file_reader.BaseFileReader.validate_path")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_get_all_returns_data(self, mock_file, mock_validate_path):
        reader = JsonFileReader("fakepath.json")
        result = reader.get_all()
        self.assertEqual(result, {"key": "value"})

    @patch("models.file_management.readers.base_file_reader.BaseFileReader.validate_path")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_validate_structure_valid(self, mock_file, mock_validate_path):
        reader = JsonFileReader("fakepath.json")
        self.assertTrue(reader.validate_structure())

    @patch("models.file_management.readers.base_file_reader.BaseFileReader.validate_path")
    @patch("builtins.open", new_callable=mock_open, read_data='["not a dict"]')
    def test_validate_structure_invalid(self, mock_file, mock_validate_path):
        with self.assertRaises(ValueError) as context:
            JsonFileReader("fakepath.json")
        self.assertIn("n'a pas une structure valide", str(context.exception))


if __name__ == "__main__":
    unittest.main()

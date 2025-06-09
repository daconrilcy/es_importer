import unittest
import tempfile
import json
from pathlib import Path
from initialize.index_details import IndexDetails  # adapte le chemin si nécessaire


class TestIndexDetails(unittest.TestCase):

    def setUp(self):
        self.index_name = "test_index"
        self.mapping = {"properties": {"field": {"type": "text"}}}

    def test_initialization_without_datas_file(self):
        index = IndexDetails(self.index_name, self.mapping)
        self.assertEqual(index.index_name, self.index_name)
        self.assertEqual(index.mapping, self.mapping)
        self.assertIsNone(index.datas_filepath)
        self.assertIsNone(index.datas)

    def test_initialization_with_valid_datas_file(self):
        temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False)
        sample_data = [{"id": 1, "value": "test"}]
        json.dump(sample_data, temp_file)
        temp_file.close()

        index = IndexDetails(self.index_name, self.mapping, temp_file.name)
        self.assertEqual(index.datas_filepath, Path(temp_file.name))
        self.assertEqual(index.datas, sample_data)

        Path(temp_file.name).unlink()  # nettoyage

    def test_invalid_json_file(self):
        temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False)
        temp_file.write("{invalid_json: true}")  # contenu invalide
        temp_file.close()

        index = IndexDetails(self.index_name, self.mapping, temp_file.name)
        self.assertIsNone(index.datas)

        Path(temp_file.name).unlink()

    def test_missing_file(self):
        fake_path = Path(tempfile.gettempdir()) / "non_existent_file.json"
        index = IndexDetails(self.index_name, self.mapping, fake_path)
        self.assertIsNone(index.datas)

# if __name__ == "__main__":
#     unittest.main()

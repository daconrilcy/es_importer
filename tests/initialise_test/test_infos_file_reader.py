import unittest
import tempfile
import os
import json

from initialize.infos_reader import InfosFileReader


class TestInfosFileReader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        self.valid_content = {
            "index_files": {"index_name": "test_index"},
            "another_key": {"some": "data"}
        }

        self.valid_file_path = os.path.join(self.temp_dir, "valid.json")
        with open(self.valid_file_path, "w", encoding="utf-8") as f:
            json.dump(self.valid_content, f)

        self.invalid_json_path = os.path.join(self.temp_dir, "invalid.json")
        with open(self.invalid_json_path, "w", encoding="utf-8") as f:
            f.write("{ bad json")

        self.nonexistent_path = os.path.join(self.temp_dir, "does_not_exist.json")

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_load_valid_json(self):
        reader = InfosFileReader(self.valid_file_path)
        self.assertEqual(reader._data, self.valid_content)

    def test_get_existing_key(self):
        reader = InfosFileReader(self.valid_file_path)
        value = reader.get("index_files")
        self.assertEqual(value, {"index_name": "test_index"})

    def test_get_missing_key(self):
        reader = InfosFileReader(self.valid_file_path)
        self.assertIsNone(reader.get("missing_key"))

    def test_load_invalid_json(self):
        reader = InfosFileReader(self.invalid_json_path)
        self.assertIsNone(reader._data)

    def test_load_nonexistent_file(self):
        reader = InfosFileReader(self.nonexistent_path)
        self.assertIsNone(reader._data)

    def test_get_with_none_data(self):
        reader = InfosFileReader(self.invalid_json_path)
        self.assertIsNone(reader.get("any_key"))


if __name__ == "__main__":
    unittest.main()

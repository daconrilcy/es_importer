import unittest
import tempfile
import shutil
import os
import json

from initialize.index_builder import IndexDetailsBuilder
from initialize.index_details import IndexDetails


class TestIndexDetailsBuilder(unittest.TestCase):

    def setUp(self):
        # Créer un dossier temporaire avec un fichier JSON valide
        self.temp_dir = tempfile.mkdtemp()
        self.valid_mapping_filename = "valid_mapping.json"
        self.valid_mapping_path = os.path.join(self.temp_dir, self.valid_mapping_filename)
        with open(self.valid_mapping_path, "w", encoding="utf-8") as f:
            json.dump({"properties": {"field": {"type": "text"}}}, f)

        self.valid_config = {
            "index_name": "test_index",
            "mapping_file": self.valid_mapping_filename,
            "datas_file": "test_data.json"
        }

        self.builder = IndexDetailsBuilder(base_folder=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_build_valid_config(self):
        index_details = self.builder.build(self.valid_config)
        self.assertIsInstance(index_details, IndexDetails)
        self.assertEqual(index_details.index_name, "test_index")
        self.assertEqual(index_details.mapping["properties"]["field"]["type"], "text")
        self.assertTrue(index_details.datas_filepath.name.endswith("test_data.json"))

    def test_build_none_config(self):
        self.assertIsNone(self.builder.build(None))

    def test_build_invalid_mapping(self):
        config = {
            "index_name": "bad_index",
            "mapping_file": "not_found.json",
            "datas_file": "data.json"
        }
        self.assertIsNone(self.builder.build(config))

    def test_load_mapping_valid(self):
        mapping = self.builder._load_mapping(self.valid_mapping_filename)
        self.assertIsInstance(mapping, dict)
        self.assertIn("properties", mapping)

    def test_load_mapping_missing_filename(self):
        mapping = self.builder._load_mapping(None)
        self.assertIsNone(mapping)

    def test_load_mapping_file_not_exists(self):
        mapping = self.builder._load_mapping("unknown.json")
        self.assertIsNone(mapping)

    def test_load_mapping_invalid_json(self):
        bad_file = os.path.join(self.temp_dir, "bad.json")
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        mapping = self.builder._load_mapping("bad.json")
        self.assertIsNone(mapping)


if __name__ == "__main__":
    unittest.main()

import unittest
from models.file_management.readers.mapping_file_reader import MappingFileReader


class TestMappingFileReader(unittest.TestCase):

    def setUp(self):
        self.reader = MappingFileReader("c:/dev/py/csv_importer/tests/data/mapping_sample.json")

    def test_mapping_name(self):
        self.assertIsInstance(self.reader.mapping_name, str)

    def test_related_to(self):
        self.assertIsInstance(self.reader.related_to, str)

    def test_fields(self):
        self.assertIsInstance(self.reader.fields, dict)
        self.assertTrue(all(isinstance(f, str) for f in self.reader.fields.keys()))

    def test_get_field(self):
        field = next(iter(self.reader.fields.keys()))
        self.assertIsNotNone(self.reader.get_field(field))

    def test_get_mapped_fields(self):
        mapped_fields = self.reader.get_mapped_fields()
        self.assertTrue(all(f.mapped for f in mapped_fields.values()))

    def test_validate_structure(self):
        self.assertTrue(self.reader.validate_structure())


if __name__ == '__main__':
    unittest.main()

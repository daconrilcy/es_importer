import unittest
import pandas as pd
import tempfile
import os

from models.readers.txt_file_reader import TxtFileReader


class TestTxtFileReader(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w+', encoding='utf-8')
        self.temp_file.write("col1\tcol2\tcol3\n1\t2\t3\n4\t5\t6\n7\t8\t9\n10\t11\t12\n")
        self.temp_file.close()
        self.reader = TxtFileReader(filepath=self.temp_file.name, chunk_size=2)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_nrows(self):
        self.assertEqual(self.reader.nrows, 5)

    def test_headers(self):
        self.assertEqual(self.reader.headers, ["col1", "col2", "col3"])

    def test_get_chunk_first(self):
        chunk = self.reader.get_chunk(chunk_index=0)
        self.assertIsInstance(chunk, pd.DataFrame)
        self.assertEqual(len(chunk), 2)

    def test_get_chunk_second(self):
        chunk = self.reader.get_chunk(chunk_index=1)
        self.assertEqual(len(chunk), 2)

    def test_get_chunk_last(self):
        chunk = self.reader.get_chunk(chunk_index=2)
        self.assertEqual(len(chunk), 0)

    def test_get_all(self):
        df = self.reader.get_all()
        self.assertEqual(len(df), 4)

    def test_read_partial(self):
        df = self.reader.read_partial(start=1, size=2)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["col1"], "4")

    def test_validate_structure(self):
        self.assertTrue(self.reader.validate_structure())

    def test_get_headers_and_chunk(self):
        headers, chunk = self.reader.get_headers_and_chunk(chunk_size=2, chunk_index=1)
        self.assertListEqual(headers, ["col1", "col2", "col3"])
        self.assertEqual(len(chunk), 2)


if __name__ == '__main__':
    unittest.main()

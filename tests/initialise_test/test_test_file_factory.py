import os
import unittest
import tempfile
import shutil
from pathlib import Path

from initialize.test_file import TestFileFactory


class DummyConfig:
    class FileTypes:
        class Datas:
            def __init__(self, folder_path):
                self.folder_path = folder_path

        def __init__(self, folder_path):
            self.datas = self.Datas(folder_path)

    def __init__(self, folder_path):
        self.file_types = self.FileTypes(folder_path)


class TestTestFileFactory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        dummy_config = DummyConfig(self.temp_dir)
        self.factory = TestFileFactory(config=dummy_config)
        self.output_file = Path(self.temp_dir) / "test.csv"

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_datas_test_file_success(self):
        result = self.factory.create_datas_test_file()
        self.assertTrue(result)
        self.assertTrue(self.output_file.exists())

        with self.output_file.open("r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        self.assertEqual(len(lines), 6)  # 1 header + 5 rows
        self.assertEqual(lines[0], "id,name,type,size,path,date")
        self.assertIn("5,test5,yaml,500,C:/test5,2021-01-05", lines)

    def test_create_datas_test_file_exception(self):
        # Simule un dossier supprimé pour provoquer une exception
        shutil.rmtree(self.temp_dir)
        result = self.factory.create_datas_test_file()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

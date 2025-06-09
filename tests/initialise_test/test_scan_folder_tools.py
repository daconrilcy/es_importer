import unittest
from pathlib import Path
import tempfile
import shutil

from models.file_infos import FileInfos
from initialize.scan_folder import ScanFolderTools  # adapte l'import selon ton projet


class DummyFileInfos(FileInfos):
    def __init__(self, filename):
        self._filename = filename

    @property
    def filename(self):
        return self._filename


class TestScanFolderTools(unittest.TestCase):

    def setUp(self):
        # Crée un dossier temporaire
        self.test_dir = tempfile.mkdtemp()
        self.folder_path = Path(self.test_dir)
        (self.folder_path / "file1.txt").write_text("data1")
        (self.folder_path / "file2.txt").write_text("data2")

    def tearDown(self):
        # Supprime le dossier temporaire
        shutil.rmtree(self.test_dir)

    def test_list_files_valid_folder(self):
        files = ScanFolderTools.list_files(self.folder_path)
        filenames = sorted([f.name for f in files])
        self.assertEqual(filenames, ["file1.txt", "file2.txt"])

    def test_list_files_invalid_folder(self):
        files = ScanFolderTools.list_files("/invalid/path")
        self.assertEqual(files, [])

    def test_compare_filepath_list(self):
        a = [self.folder_path / "file1.txt"]
        b = [self.folder_path / "file1.txt", self.folder_path / "file2.txt"]
        add_to_a, add_to_b = ScanFolderTools.compare_filepath_list(a, b)
        self.assertEqual(add_to_a, [self.folder_path / "file2.txt"])
        self.assertEqual(add_to_b, [])

    def test_compare_filepath_list_empty(self):
        add_to_a, add_to_b = ScanFolderTools.compare_filepath_list([], [])
        self.assertEqual(add_to_a, [])
        self.assertEqual(add_to_b, [])

    def test_get_missing_files_by_folder(self):
        other_folder = Path(tempfile.mkdtemp())
        (other_folder / "extra.txt").write_text("not indexed")

        file_infos_list = [DummyFileInfos("file1.txt"), DummyFileInfos("file2.txt")]
        folder_paths = [self.folder_path, other_folder]

        result = ScanFolderTools.get_missing_files_by_folder(file_infos_list, folder_paths)
        self.assertIn(other_folder.name, result)
        self.assertEqual(result[other_folder.name], [other_folder / "extra.txt"])

        shutil.rmtree(other_folder)

    def test_get_missing_files_by_folder_with_invalid_path(self):
        file_infos_list = [DummyFileInfos("file1.txt")]
        folder_paths = ["/invalid/path"]
        result = ScanFolderTools.get_missing_files_by_folder(file_infos_list, folder_paths)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()

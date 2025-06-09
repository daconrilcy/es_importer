import unittest
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage

from models.file_management.save_management import FileSaver
from models.file_type import FileType
from models.file_management.save_management.file_save_strategy import AbstractFileSaveStrategy


class TestFileSaver(unittest.TestCase):

    def setUp(self):
        self.mock_file = MagicMock(spec=FileStorage)
        self.mock_filetype = MagicMock(spec=FileType)
        self.mock_filetype.folder_path = "/fake/dir"
        self.mock_filetype.accepted_extensions = [".txt"]

        self.mock_validator = MagicMock()
        self.mock_checker = MagicMock()
        self.mock_utils = MagicMock()
        self.mock_utils.generate_filename.return_value = "file.txt"

        patcher_utils = patch("models.file_management.save_management.FileUtils", return_value=self.mock_utils)
        self.addCleanup(patcher_utils.stop)
        self.mock_fileutils_class = patcher_utils.start()

    def test_save_valid_file_success(self):
        self.mock_validator.is_valid.return_value = True
        self.mock_checker.is_allowed.return_value = True
        mock_strategy = MagicMock(spec=AbstractFileSaveStrategy)
        mock_strategy.save.return_value = "/fake/dir/file.txt"

        saver = FileSaver(
            save_strategy=mock_strategy,
            validator=self.mock_validator,
            checker=self.mock_checker,
        )

        result = saver.save(self.mock_file, self.mock_filetype, "original.txt")

        self.assertEqual(result, (True, "file.txt", "/fake/dir/file.txt"))
        mock_strategy.save.assert_called_once()

    def test_save_invalid_file_fails_validation(self):
        self.mock_validator.is_valid.return_value = False
        saver = FileSaver(validator=self.mock_validator, checker=self.mock_checker)
        result = saver.save(self.mock_file, self.mock_filetype, "original.txt")
        self.assertEqual(result, (False, None, None))

    def test_save_invalid_extension(self):
        self.mock_validator.is_valid.return_value = True
        self.mock_checker.is_allowed.return_value = False
        saver = FileSaver(validator=self.mock_validator, checker=self.mock_checker)
        result = saver.save(self.mock_file, self.mock_filetype, "original.txt")
        self.assertEqual(result, (False, None, None))

    def test_save_raises_oserror(self):
        self.mock_validator.is_valid.return_value = True
        self.mock_checker.is_allowed.return_value = True

        class FailingStrategy(AbstractFileSaveStrategy):
            def save(self, file: FileStorage, filename: str) -> str:
                raise OSError("Disk full")

        saver = FileSaver(
            save_strategy=FailingStrategy(),
            validator=self.mock_validator,
            checker=self.mock_checker,
        )

        result = saver.save(self.mock_file, self.mock_filetype, "original.txt")
        self.assertEqual(result, (False, None, None))


if __name__ == "__main__":
    unittest.main()

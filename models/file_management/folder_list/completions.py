from pathlib import Path
from typing import Optional, List

from config import Config


class CompletionsFolderList:
    def __init__(self, config: Optional[Config] = None):
        config = config or Config()
        self._filenames_list: List[str] = []
        self._filepaths_list: List[Path] = []
        self._folder = Path(config.files_folder) / "completions"
        self._list_files()

    def _list_files(self):
        for file in self._folder.iterdir():
            if file.is_file():
                self._filenames_list.append(file.name)
                self._filepaths_list.append(file)

    @property
    def filenames_list(self) -> List[str]:
        """List of all file names in the folder."""
        return self._filenames_list

    @property
    def filepaths_list(self) -> List[Path]:
        """List of all file paths in the folder."""
        return self._filepaths_list

    @property
    def folder_path(self) -> Path:
        """Path to the folder."""
        return self._folder
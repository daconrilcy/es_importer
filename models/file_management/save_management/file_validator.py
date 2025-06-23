from pathlib import Path
from typing import Any, Union, List, Dict

import pandas as pd

from models.file_type import FileType
from werkzeug.datastructures import FileStorage


class FileValidator:
    def is_valid(self, data: Any, extension: str, filename: str):
        return all([data, extension, filename])


class FileTypeValidator:
    def is_valid(self, file: FileStorage, filetype: FileType, filename: str) -> bool:
        return all([file, filetype, filename])


class CsvFileValidator:
    def is_valid(self, data: Union[pd.DataFrame, List[Any]], filename: str) -> bool:
        if not isinstance(data, (pd.DataFrame, list)):
            return False
        if not filename:
            return False
        extension = Path(filename).suffix.lower()
        if extension != ".csv":
            return False
        return True

class MappingFileValidator:
    def is_valid(self, data: Dict[str, Any], filename: str) -> bool:
        if not isinstance(data, dict):
            return False
        if not filename:
            return False
        extension = Path(filename).suffix.lower()
        if extension != ".json":
            return False
        return True
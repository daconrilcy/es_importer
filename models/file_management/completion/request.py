from typing import Optional, Dict, Any

from models.file_management.filepath_codec import FilePathCodec
from config import Config


class RequestValidator:
    """
    Validate and extract fields from a request dictionary related to file processing.
    """

    _VALID_FILEID_KEYS = ["fileid", "file-id", "file_id", "fileId", "id", "_id"]
    _VALID_FILEPATH_KEYS = [
        "original_filepath", "originalfilepath", "filepath",
        "file_path", "path", "encoded_filepath",
        "encodedfilepath", "encoded_file_path"
    ]
    _VALID_SEPARATORS = [",", ", ", ";", "; ", "\t", "|"]

    _VALID_COLUMN_KEYS = ["column", "colonne", "col", "source_column"]

    _VALID_NEW_COLUMN_KEYS = ["new_column", "new_col", "new_colonne"]

    def __init__(self, request_dict: Optional[Dict[str, Any]] = None, config: Optional[Config] = None):
        self.config = config or Config()
        self.original_request = request_dict or {}

        # Fields extracted from request
        self._fileid: Optional[str] = None
        self._original_encoded_filepath: Optional[str] = None
        self._original_decoded_filepath: Optional[str] = None
        self._chunk: Optional[int] = None
        self._chunksize: Optional[int] = None
        self._filename: Optional[str] = None
        self._separator: Optional[str] = None
        self._source_column: Optional[str] = None
        self._new_column: Optional[str] = None

        self._codec = FilePathCodec()
        self._is_valid = self._parse_request()

    def is_none(self, value: str) -> bool:
        if value is None:
            return True
        value = str(value).strip()
        if value == "":
            return True
        if value.lower() == "none":
            return True
        if value.lower() == "null":
            return True
        if value.lower() == "nil":
            return True
        if value.lower() == "undefined":
            return True
        return False

    def _parse_request(self) -> bool:
        if not isinstance(self.original_request, dict):
            return False

        for key in self._VALID_FILEID_KEYS:
            if key in self.original_request:
                self._fileid = self.original_request[key]
                break
        if self.is_none(self._fileid):
            self._fileid = None

        for key in self._VALID_FILEPATH_KEYS:
            if key in self.original_request:
                self._original_encoded_filepath = self.original_request[key]
                break
        if self.is_none(self._original_encoded_filepath):
            self._original_encoded_filepath = None

        if not self._fileid and not self._original_encoded_filepath:
            return False

        for key in self._VALID_COLUMN_KEYS:
            if key in self.original_request:
                self._source_column = self.original_request[key]
                break

        if not self._source_column or self.is_none(self._source_column):
            return False

        self._column = self._source_column.strip()

        for key in self._VALID_NEW_COLUMN_KEYS:
            if key in self.original_request:
                self._new_column = self.original_request[key]
                break

        if not self._new_column or self.is_none(self._new_column):
            self._new_column = self._column + "_completion"

        self._new_column = self._new_column.strip()

        self._chunk = self.original_request.get("chunk")
        self._chunksize = self.original_request.get("chunksize", self.config.chunksize)
        self._filename = self.original_request.get("filename")

        separator = self.original_request.get("separator")
        self._separator = separator if separator in self._VALID_SEPARATORS else None

        return True

    def _decode_filepath(self):
        if self._original_encoded_filepath and self._original_decoded_filepath is None:
            try:
                self._original_decoded_filepath = self._codec.decode(self._original_encoded_filepath)
            except ValueError:
                self._original_decoded_filepath = None

    @property
    def is_valid(self) -> bool:
        """Return True if the request was valid."""
        return self._is_valid

    @property
    def original_encoded_filepath(self) -> Optional[str]:
        return self._original_encoded_filepath

    @property
    def original_decoded_filepath(self) -> Optional[str]:
        self._decode_filepath()
        return self._original_decoded_filepath

    @property
    def fileid(self) -> Optional[str]:
        return self._fileid

    @property
    def chunk(self) -> Optional[int]:
        return self._chunk

    @property
    def chunksize(self) -> Optional[int]:
        return self._chunksize

    @property
    def filename(self) -> Optional[str]:
        return self._filename

    @property
    def separator(self) -> Optional[str]:
        return self._separator

    @property
    def source_column(self) -> Optional[str]:
        return self._source_column

    @property
    def new_column(self) -> Optional[str]:
        return self._new_column

    def __repr__(self):
        return (
            f"RequestValidator(fileid={self._fileid}, chunk={self._chunk}, "
            f"chunksize={self._chunksize}, filename={self._filename}, separator={self._separator})"
        )


if __name__ == "__main__":
    filepath = "c:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv"
    encoded_filepath = FilePathCodec.encode(filepath)
    request_dict_test = {"fileid": "123", "chunk": 1, "chunksize": 1000, "filename": "test.csv", "separator": ";",
                         "encoded_filepath": encoded_filepath}
    validator_test = RequestValidator(request_dict_test)
    print(validator_test.is_valid)
    print(validator_test.fileid)
    print(validator_test.chunk)
    print(validator_test.chunksize)
    print(validator_test.filename)
    print(validator_test.separator)
    print(validator_test.original_encoded_filepath)
    print(validator_test.original_decoded_filepath)

from typing import Union, Optional, List, Dict

from config import Config
from models.completion.creator import CsvManualMultiColumnsBuilder
from models.completion.request import RequestValidator
import logging

logger = logging.getLogger(__name__)


class EmptyColumnAdder:

    def __init__(
            self,
            request_dict: Dict,
            config: Optional[Config] = None
    ):
        self._config = config or Config()
        self.request = request_dict
        self._csv_object = None

    def _validate_and_get_request_data(self, request_dict: Dict):
        self._request = RequestValidator(request_dict, self._config)

    def create(self):
        if not self._request.is_valid:
            logger.error("EmptyColumnAdder - La requête est invalide.")
            return False
        try:
            self._csv_object = CsvManualMultiColumnsBuilder(
                source_column=self.request.source_column,
                new_columns=self.request.new_column,
                file_id=self.request.fileid,
                original_filepath=self.request.original_decoded_filepath,
                separator=self.request.separator,
                chunk_size=self.request.chunksize,
                filename=self.request.filename,
                config=self._config
            )
            return self._csv_object.create_csv()
        except Exception as e:
            logger.error(f"EmptyColumnAdder - Erreur durant le traitement de création du fichier : {e}")
            return False

    @property
    def request(self) -> RequestValidator:
        return self._request

    @request.setter
    def request(self, request_dict: Dict):
        if not request_dict:
            self._request = None
            return
        self._validate_and_get_request_data(request_dict)


if __name__ == "__main__":
    from models.file_management.filepath_codec import FilePathCodec

    filepath = "c:/dev/py/csv_importer/files/datas/5c1f2fe2-1e64-4c5e-83a7-d0dd43439a82.csv"
    encoded_filepath = FilePathCodec.encode(filepath)
    request_dict_test = {"fileid": None, "chunk": 1, "chunksize": 1000, "filename": "test.csv", "separator": ";",
                         "encoded_filepath": encoded_filepath, "source_column": "name_en"}
    empty_column_adder_test = EmptyColumnAdder(request_dict_test)
    empty_column_adder_test.create()

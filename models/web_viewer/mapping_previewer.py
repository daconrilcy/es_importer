from typing import Dict, Any, List, Optional

from config import Config
from models.elastic_specifiques import EsTypes, BasicAnalyzers
from models.file_management.file_infos import FileInfos
from models.file_management.filepath_codec import FilePathCodec
from models.file_management.readers.mapping_file_reader import MappingFileReader
from models.web_viewer.base_file_previewer import BaseFilePreviewer


class MappingFilePreviewer(BaseFilePreviewer):

    def __init__(self, list_files: Optional[list[FileInfos]] = None,
                 list_files_related_to: Optional[list[FileInfos]] = None,
                 front_name_related_to: Optional[str] = None) -> None:
        super().__init__(list_files=list_files)
        self._file_encoder = FilePathCodec()
        if front_name_related_to:
            self._front_name_related_to = front_name_related_to

        self._type_related_to: Optional[str] = Config().file_types.datas.name
        self._list_files_related_to: Optional[list[FileInfos]] = list_files_related_to
        self._encode_filepath_related_to()

    def _create_reader_from_infos(self, file_infos):
        return MappingFileReader(filepath=file_infos.filepath)

    def _create_reader_from_dict(self, data):
        return MappingFileReader(filepath=data["filepath"])

    @property
    def related_to(self) -> str:
        return self._reader.related_to if self._reader else ""

    @property
    def front_name_related_to(self) -> str:
        return self._get_front_end_filename()

    @property
    def fields(self) -> Dict[str, Any]:
        return self._reader.fields if self._reader else {}

    @property
    def es_field_types(self) -> List[str]:
        return EsTypes()

    @property
    def es_analyzers(self) -> List[str]:
        return BasicAnalyzers()

    @front_name_related_to.setter
    def front_name_related_to(self, value: Optional[str]):
        self._front_name_related_to = value

    @property
    def list_files_related_to(self) -> list[FileInfos]:
        return self._list_files_related_to

    def _get_front_end_filename(self):
        if not self._front_name_related_to:
            if self.list_files_related_to:
                for file_related_to in self.list_files_related_to:
                    if file_related_to.filename == self.related_to:
                        self._front_name_related_to = file_related_to.front_end_filename
        return self._front_name_related_to

    def _encode_filepath_related_to(self) -> None:
        if self.list_files_related_to:
            for frt in self.list_files_related_to:
                frt.encoded_filepath = self._file_encoder.encode(frt.filepath)

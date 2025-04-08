import os.path

from config import Config
from utils import get_dict_from_json


class DataImporter:
    """
    class to manage process and object to import a data file into Es
    """

    def __init__(self, filepath: str = None, file_type: str = "importers", es_id: str = None):
        config = Config()
        self._id = es_id
        self._folder_path = config.importer_folder
        self._front_name = None
        self._filepath = filepath
        self._file_type = file_type
        self._filename = None
        self._datas_filename = None
        self._datas_separator = None
        self._mapping_filename = None
        self._index_name = None
        self.expected_keys = {"front_name", "datas_filename", "datas_separator", "mapping_filename", "index_name"}

    @property
    def id(self) -> str:
        """
        return the id of the importer
        :return: str: id
        """
        return self._id

    @id.setter
    def id(self, es_id: str):
        if es_id is None or es_id == "":
            print(f"❌ DataImporter.id : id is empty")
            return
        self._id = es_id


    @property
    def front_name(self) -> str:
        """
        return the front name of the importer
        :return: str: front name
        """
        return self._front_name

    @front_name.setter
    def front_name(self, front_name: str):
        if front_name is None or front_name == "":
            print(f"❌ DataImporter.front_name.setter : front name is empty")
            return
        self._front_name = front_name

    @property
    def filepath(self) -> str:
        """
        return file path of the file
        :return:
        """
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: str):
        if filepath is None or filepath == "":
            print(f"❌ DataImporter.file_path : filepath is empty")
        if not os.path.isfile(filepath):
            print(f"❌ DataImporter.file_path : {filepath} is not a file")
            return
        self._filepath = filepath
        filename = os.path.basename(filepath)
        if self.filename is None or self.filename == "":
            self.filename = filename

    @property
    def filename(self) -> str:
        """
        return the file name
        :return:
        """
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        if filename is None or filename == "":
            print(f"❌ DataImporter.filename : filename is empty")
            return
        filepath = self._folder_path + filename
        self._filename = filename
        if self.filepath is None or self.filepath == "":
            self.filepath = filepath

    @property
    def datas_filename(self) -> str:
        """
        return the data filename
        :return:
        """
        return self._datas_filename

    @datas_filename.setter
    def datas_filename(self, filename: str):
        if filename is None or filename == "":
            print(f"❌ DataImporter.datas_filename : filename is empty")
            return
        self._datas_filename = filename

    @property
    def datas_separator(self) -> str:
        """
        return the separator of file data
        :return:
        """
        return self._datas_separator

    @datas_separator.setter
    def datas_separator(self, datas_separator: str = ","):
        self._datas_separator = datas_separator

    @property
    def mapping_filename(self) -> str:
        """
        return the mapping filename
        :return:
        """
        return self._mapping_filename

    @mapping_filename.setter
    def mapping_filename(self, mapping_filename: str):
        if mapping_filename is None or mapping_filename == "":
            print(f"❌ DataImporter.mapping_filename : mapping_filename is empty")
            return
        self._mapping_filename = mapping_filename

    @property
    def index_name(self) -> str:
        """
        return the attached index to import data
        :return:
        """
        return self._index_name

    @index_name.setter
    def index_name(self, index_name: str):
        if index_name is None or index_name == "":
            print(f"❌ DataImporter.index_name.setter : index_name is empty")
            return
        self._index_name = index_name

    @property
    def file_type(self) -> str:
        """
        return the file type
        :return:
        """
        return self._file_type

    @file_type.setter
    def file_type(self, file_type: str):
        if file_type is None or file_type == "":
            print(f"❌ DataImporter.file_type : file_type is empty")
            return
        self._file_type = file_type

    def set_from_filepath(self, filepath: str = None):
        """
        set the importer from a json file
        :param filepath:
        :return:
        """
        if filepath is not None:
            self.filepath = filepath
        data = get_dict_from_json(self.filepath)
        if data is None:
            print(f"❌ DataImporter.set_from_filepath : data is None")
            return False
        if not isinstance(data, dict):
            print(f"❌ DataImporter.set_from_filepath : data is not a dict")
            return False
        return self.set_from_dict(data)

    def set_from_dict(self, datas_importer: dict[str]) -> bool:
        """
        set the importer from a dict
        :param datas_importer:
        :return:
        """
        if datas_importer is None:
            print("❌ DataImporter.set_from_dict : datas_importer is None")
            return False
        if not isinstance(datas_importer, dict):
            print("❌ DataImporter.set_from_dict : datas_importer is not a dict")
            return False
        if not self.expected_keys.issubset(datas_importer.keys()):
            print(f"❌ DataImporter.set_from_dict : datas_importer keys {datas_importer.keys()} are not valid")
            return False
        if "front_name" in datas_importer:
            self.front_name = datas_importer["front_name"]
        if "datas_filename" in datas_importer:
            self.datas_filename = datas_importer["datas_filename"]
        if "datas_separator" in datas_importer:
            self.datas_separator = datas_importer["datas_separator"]
        if "mapping_filename" in datas_importer:
            self.mapping_filename = datas_importer["mapping_filename"]
        if "index_name" in datas_importer:
            self.index_name = datas_importer["index_name"]
        return True

    def load_from_filename(self, filename: str = None):
        """
        load the importer from a json file
        :param filename:
        :return:
        """
        self.filename = filename
        self.set_from_filepath()

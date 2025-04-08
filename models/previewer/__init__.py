from models.Importer import DataImporter
from models.mapping_obj import MappingSchema
from models.previewer.csv_pre import CsvDataPreview
from models.previewer.importer_pre import ImporterPreviewerDataSet
from models.previewer.mapping_pre import MappingPreviewerDataset
from utils import preview_csv


class Previewer:
    """
    Preview the file content
    """

    def __init__(self, layout: str = None,
                 method: str = None,
                 front_name: str = None,
                 filename: str = None,
                 filepath: str = None,
                 sep: str = ",",
                 file_id: str = None,
                 file_type: str = "datas",
                 ):
        """
        Initialize the Previewer
        :param filepath: File path
        :param sep: Separator
        """
        self.layout = layout
        self._method = method
        self.front_name = front_name
        self.filename = filename
        self._filepath = filepath
        self.sep = sep
        self.file_id = file_id
        self.datas = None
        self.file_type = file_type

        self._set()

    def _set(self):
        """
        Preview the file content
        :return:
        """

        if self._filepath is None:
            print("❌ FilePreviewer.set: file_path is None")
            return False
        if self.layout is None:
            print("❌ FilePreviewer.set: layout is None")
            return False
        if self._method is None:
            print("❌ FilePreviewer.set: method is None")
            return False
        if self._method == "data_csv":
            datas_brutes = preview_csv(filepath=self._filepath, sep=self.sep)
            if datas_brutes is None:
                print("❌ FilePreviewer.set: datas_brutes is None")
                return False
            if len(datas_brutes) == 0:
                print("❌ FilePreviewer.set: datas_brutes is empty")
                return False
            self.datas = CsvDataPreview(datas_brutes, self.front_name, self.filename,
                                        self.file_id, file_type=self.file_type)
        if self._method == "mappings_json":
            datas = MappingSchema(file_type=self.file_type, front_name=self.front_name, es_id=self.file_id)
            datas.load_from_filename(self.filename)
            if datas is None:
                print("❌ FilePreviewer.set: datas is None")
                return False
            self.datas = MappingPreviewerDataset(datas)

        if self._method == "importers_json":
            datas = DataImporter()
            datas.load_from_filename(self.filename)
            datas.id = self.file_id
            datas.file_type = self.file_type
            datas.front_name = self.front_name
            if datas is None:
                print("❌ FilePreviewer.set: datas is None")
                return False
            self.datas = ImporterPreviewerDataSet(datas)

    def __str__(self):
        return (f"Previewer({self.layout}, {self._method}, {self.front_name}, {self.filename}, {self._filepath}), "
                f"{self.sep}, {self.datas})")

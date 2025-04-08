from models.Importer import DataImporter


class ImporterPreviewerDataSet:
    """
    DataSet for ImporterPreviewer
    """

    def __init__(self, data: DataImporter):
        self.importer = data
        self._file_type = data.file_type
        self._data_list_files = []
        self._mapping_list_files = []
        self._set_list_files()

    @property
    def importer(self) -> DataImporter:
        """
        Get the data of the dataset.
        :return:
        """
        return self._importer

    @importer.setter
    def importer(self, data: DataImporter):
        self._importer = data

    @property
    def data_list_files(self) -> list:
        """
        Get the list of data files.
        :return:
        """
        return self._data_list_files

    @property
    def mapping_list_files(self) -> list:
        """
        Get the list of mapping files.
        :return:
        """
        return self._mapping_list_files

    @property
    def file_type(self) -> str:
        """
        Get the file type.
        :return:
        """
        return self._file_type

    def _set_list_files(self):
        """
        Set the list of data files and mapping files.
        :return:
        """
        from full_file_manager import FullFileManager
        ffm = FullFileManager()
        self._data_list_files = ffm.get_datas_files_list()
        self._mapping_list_files = ffm.get_mappings_files_list()

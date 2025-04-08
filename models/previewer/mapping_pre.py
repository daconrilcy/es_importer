from models.elastic_type.collection import EsTypes
from models.es_analyser import EsAnalysers
from models.mapping_obj import MappingSchema


class MappingPreviewerDataset:
    """
    Class used to preview the mapping of the dataset
    used to view on the Web UI
    """

    def __init__(self, data: MappingSchema):
        self.mapping = data
        self.file_type = data.file_type
        self.es_types_list = EsTypes()
        self.es_analysers = EsAnalysers()
        self.list_datas_files = []
        self._set_list_datas_files()
        self.list_bool = [True, False]

    def _set_list_datas_files(self):
        """
        Set the list of data files
        :return: None
        """
        from full_file_manager import FullFileManager
        ffm = FullFileManager()
        self.list_datas_files = ffm.get_datas_files_list()

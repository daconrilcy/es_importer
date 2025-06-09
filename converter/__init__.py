from config import Config
from models.file_infos import FileInfos


class MultiConverter:
    """
    Convert the documents to objects and the objects to documents
    """

    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
        self.config = config

    @staticmethod
    def doc_files_to_file_obj(doc_files: list[dict], folder_filter: str = None) -> list[FileInfos]:
        """
        Convert the files documents to FileInfos objects
        :param doc_files:
        :param folder_filter:
        :return: list of FileInfos
        """
        files_obj = []
        for fdoc in doc_files:
            temp_file = FileInfos(doc=fdoc)

            if folder_filter is not None and temp_file.type is not None:
                if folder_filter == temp_file.type.name:
                    files_obj.append(temp_file)
            else:
                files_obj.append(temp_file)
        return files_obj

    @staticmethod
    def files_obj_to_docs(files_obj: list[FileInfos]) -> list[dict]:
        """
        Convert the files objects to documents
        :param files_obj:
        :return: list of documents
        """
        docs = []
        for file_obj in files_obj:
            docs.append(file_obj.get_doc())
        return docs


if __name__ == "__main__":
    cfg_test = Config()
    from elastic_manager import ElasticSearchManager

    esg_test = ElasticSearchManager(cfg_test)
    c_test = MultiConverter(cfg_test)
    docs_files = esg_test.get_files_from_es()
    for df in docs_files:
        print(df)
    files_obj_test = c_test.doc_files_to_file_obj(docs_files)
    for fo in files_obj_test:
        print(fo.status)

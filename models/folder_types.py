"""
This file contains the class FolderType, which is used to store the name, path and type of a folder.
"""
from jinja2.utils import missing

from config import Config
from utils import list_of_file_in_folder
from models.file_infos import FileInfos
import os


class FolderType:
    """
    Class used to store the name, path and type of a folder
    """

    def __init__(self, name: str, path: str, type_es: str, global_index_name: str = "file_details",
                 desc_index_name: str = None):
        self.name = name
        self.path = path
        self.type_es = type_es
        self.global_index_name = None
        self.desc_index_name = None

    def get_list_files(self) -> list[FileInfos] | None:
        """
        List all files in a folder
        :return: List of files
        """
        if self.path is None:
            print(f"❌ FolderType.get_list_files: path is None - {self.name}")
            return None
        list_files = list_of_file_in_folder(self.path)
        if list_files is None:
            print(f"❌ FolderType.get_list_files: list_files is None - {self.name}")
            return None
        if len(list_files) == 0:
            print(f"📊 FolderType.get_list_files: ❌ No files in the folder {self.name}")
            return None
        list_files_obj = []
        for fi in list_files:
            file_info = FileInfos(filepath=fi)
            file_info.type = self.type_es
            list_files_obj.append(file_info)

        if len(list_files_obj) == 0:
            print(f"📊 FolderType.get_list_files: ❌ No files in the folder - {self.name}")
            return None
        return list_files_obj

    def get_folder_files_not_list_file_obj(self, files_obj_list: list[FileInfos]) -> list[FileInfos] | None:
        """
        Compare the files in the folder with the files in the list
        and return the files in folder that are not in the list
        :param files_obj_list: List of fileInfos
        :return: List of files that are not in the list
        """
        if files_obj_list is None:
            print(f"❌ FolderType.compare_files: files is None - {self.name}")
            return []
        folder_files = self.get_list_files()

        if folder_files is None:
            return []
        if files_obj_list is None or len(files_obj_list) == 0:
            print(f"📊 FolderType.compare_files: ❌ No file in list submited is in {self.name} folder")
            return folder_files
        files_to_add = []

        for ff in folder_files:
            finded = False
            for fo in files_obj_list:
                if ff.file_name == fo.file_name and ff.extension == fo.extension:
                    finded = True
                    break
            if not finded:
                files_to_add.append(ff)
        print(f"📊 FolderType.compare_files: {len(folder_files)} files not in list - {self.name}")
        return files_to_add

    def get_missing_files(self, files_obj_list: list[FileInfos]) -> list[FileInfos] | None:
        """
        check if the files in Es are in the folder
        :param files_obj_list:
        :return: List of files that are not in the folder
        """
        if files_obj_list is None:
            print(f"❌ FolderType.get_missing_files: files_obj_list is None - {self.name}")
            return []
        folder_files = self.get_list_files()
        if folder_files is None:
            return files_obj_list
        if files_obj_list is None or len(files_obj_list) == 0:
            print(f"📊 FolderType.get_missing_files: ❌ No file in list submited is in {self.name} folder")
            return folder_files
        missing_files = []

        for fo in files_obj_list:
            finded = False
            for ff in folder_files:
                if ff.file_name == fo.file_name and ff.extension == fo.extension:
                    finded = True
                    break
            if not finded:
                missing_files.append(fo)

        return missing_files

    def filter_files_with_same_type(self, files_obj_list: list[FileInfos]) -> list[FileInfos]:
        """
        Filter the files by type
        :param files_obj_list: List of files
        :return: List of files filtered by type
        """
        if files_obj_list is None:
            print("❌ FolderType._filter_files_by_type: files_obj_list is None")
            return []
        return [f for f in files_obj_list if f.type is not None and f.type.name == self.type_es]


class FoldersTypes:
    """
    Class used to store all the folders of the application
    """

    def __init__(self, config: Config = None):
        if config is None:
            config = Config()

        global_index_name = config.index_files_name
        self.data_folder = FolderType("datas", config.data_folder, "datas", global_index_name,
                                      "datas_files")
        self.mapping_folder = FolderType("mappings", config.mapping_folder, "mappings", global_index_name,
                                         "mappings_files")
        self.importer_folder = FolderType("importers", config.importer_folder, "importers",
                                          global_index_name, "importers_files")
        self.process_folder = FolderType("processors", config.process_folder, "processors",
                                         global_index_name, "processors_files")
        self.bulk_folder = FolderType("bulks", config.bulk_folder, "bulks", global_index_name,
                                      "bulks_files")

        self._folder_not_to_check = []
        self._list_folder = []
        self._set_initial_folders_list()

    @property
    def list_folder(self) -> list[FolderType]:
        """
        Get the list of folders
        :return:
        """
        return self._list_folder

    @list_folder.setter
    def list_folder(self, value: list[FolderType]):
        self._list_folder = value

    def _set_initial_folders_list(self):
        """
        Set the initial list of folders
        :return:
        """
        self._list_folder = []
        for attr in dir(self):
            if attr == "list":
                continue
            if attr.startswith("_"):
                continue
            if attr in self._folder_not_to_check:
                continue
            folder = getattr(self, attr)
            if folder is not None and isinstance(folder, FolderType):
                self._list_folder.append(folder)

    def get_files_list_not_in_list(self, files_obj: list[FileInfos]) -> list[FileInfos]:
        """
        Compare the files in the folder with the files in the list
        and return the files in folder that are not in the list of files
        :param files_obj: List of files
        :return: List of files in folder that are not in the list
        """
        if files_obj is None:
            print("❌ FoldersTypes.get_files_list_not_in_list: files is None")
            return []
        list_files = []
        for folder in self.list_folder:
            if folder is None:
                continue

            filtered_files_obj = folder.filter_files_with_same_type(files_obj)
            files_in_folder_to_add = folder.get_folder_files_not_list_file_obj(filtered_files_obj)

            if files_in_folder_to_add is None:
                continue
            if len(files_in_folder_to_add) > 0:
                list_files.extend(files_in_folder_to_add)
        return list_files

    def get_missing_files(self, files_obj: list[FileInfos]) -> list[str]:
        """
        Get the missing files in the folders
        :param files_obj:
        :return:
        """
        ids = []
        if files_obj is None:
            print("❌ FoldersTypes.get_missing_files: files is None")
            return []
        list_files = []
        for folder in self.list_folder:
            if folder is None:
                continue
            filtered_files_obj = folder.filter_files_with_same_type(files_obj)
            missing_files = folder.get_missing_files(filtered_files_obj)
            if missing_files is None:
                continue
            if len(missing_files) > 0:
                list_files.extend(missing_files)
        if len(list_files) > 0:
            ids = [f.id for f in list_files]
        return ids

    def get_folder_path_by_es_type(self, es_type: str) -> str | None:
        """
        Get the folder path by the es type
        :param es_type: Elasticsearch type
        :return: Folder path
        """
        for folder in self.list_folder:
            if folder.type_es == es_type:
                return folder.path
        return None

    def get_filepath_by_es_type_filename(self, es_type: str, file_name: str) -> str | None:
        """
        Get the file path by the es type
        :param es_type: Elasticsearch type
        :param file_name: Name of the file
        :return: File path
        """
        if file_name is None or file_name == "":
            print("❌ FoldersTypes.get_filepath_by_es_type_filename: file_name is None")
            return None
        folder_path = self.get_folder_path_by_es_type(es_type)
        if folder_path is None or folder_path == "":
            return None
        return os.path.join(folder_path, file_name)


if __name__ == "__main__":
    fo_test = FileInfos()
    fo_test.set_from_doc({
        "type": "datas",
        "extension": "csv",
        "file_name": "curiexplore-pays.csv",
        "separator": ";",
        "upload_date": "2020-06-01",
        "description": "fichier de données sur la liste des pays"
    })
    print(fo_test)
    fo_test.reset()
    fo_test.file_path = "C:/dev/py/csv_importer/files/datas/curiexplore-pays.csv"
    print(fo_test)

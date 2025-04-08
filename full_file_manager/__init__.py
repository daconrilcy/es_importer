import os
import uuid

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import Config
from elastic_manager import ElasticSearchManager
from models.file_infos import FileInfos
from models.file_type import FileType, FileTypes
from models.previewer import Previewer


class FullFileManager:
    """
    Manage all files of the application
    """

    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
        self.config = config
        self.files_types = FileTypes()
        self.es_manager = ElasticSearchManager(config)

    def upload_file(self, upload_file: FileStorage, type_file: str | FileType) -> bool:
        """
        Upload files to the application
        """
        if type_file is None or type_file == "":
            print("❌ FullFileManager.upload_file: type_file is None or empty")
            return False
        if upload_file is None:
            print("❌ FullFileManager.upload_file: upload_file is None")
            return False
        if isinstance(type_file, str):
            type_file = self.files_types.get_file_type_by_name(type_file)
        if type_file is None:
            print("❌ FullFileManager.upload_file: type_file is None")
            return False

        result_save = self._save_secure_file(upload_file, type_file.folder_path)
        if result_save is False:
            print("❌ FullFileManager.upload_file: result_save is False")
            return False
        file_obj = self._set_file_infos(result_save["filepath"], result_save["initial_filename"])
        if file_obj is False:
            print("❌ FullFileManager.upload_file: file_obj is False")
            return False
        es_doc = file_obj.get_doc()
        if es_doc is None:
            print("❌ FullFileManager.upload_file: es_doc is None")
            return False
        result_es = False
        if file_obj.type.name == "datas":
            result_es = self.es_manager.add_file_to_index_files(es_doc)
        return result_es

    def modify_file(self, file_id: str, new_front_filename: str, new_separator: str) -> bool:
        """
        Modify a file in the application
        :param file_id:
        :param new_front_filename:
        :param new_separator:
        :return:
        """
        if file_id is None or file_id == "":
            print("❌ FullFileManager.modify_file: file_id is None or empty")
            return False
        if new_front_filename is None or new_front_filename == "":
            print("❌ FullFileManager.modify_file: new_front_filename is None or empty")
            return False
        if new_separator is None or new_separator == "":
            print("❌ FullFileManager.modify_file: new_separator is None or empty")
            return False
        file_doc = self.es_manager.get_file_by_id(file_id)
        if file_doc is None:
            print("❌ FullFileManager.modify_file: file not found in ES")
            return False
        file_obj = FileInfos()
        file_obj.set_from_doc(file_doc)
        file_obj.front_end_file_name = new_front_filename
        file_obj.separator = new_separator
        new_doc = file_obj.get_doc()
        return self.es_manager.modify_file_in_index_files(new_doc)

    def get_file_by_id(self, file_id: str) -> FileInfos | bool:
        """
        Get a file from the application by its id
        :param file_id:
        :return:
        """
        if file_id is None or file_id == "":
            print("❌ FullFileManager.get_file_by_id: file_id is None or empty")
            return False
        try:
            file_doc = self.es_manager.get_file_by_id(file_id)
        except Exception as e:
            print(f"❌ FullFileManager.get_file_by_id: {e}")
            return False
        if file_doc is None:
            print("❌ FullFileManager.get_file_by_id: file not found in ES")
            return False
        file_obj = FileInfos()
        file_obj.set_from_doc(file_doc)
        return file_obj

    def get_file_preview_by_id(self, file_id: str) -> Previewer | bool:
        """
        Get a file from the application by its id
        :param file_id:
        :return:
        """
        if file_id is None or file_id == "":
            print("❌ FullFileManager.get_file_preview_by_id: file_id is None or empty")
            return False
        file_doc = self.es_manager.get_file_by_id(file_id)
        if file_doc is False:
            print("❌ FullFileManager.get_file_preview_by_id: file not found in ES")
            return False
        file_obj = FileInfos()
        file_obj.set_from_doc(file_doc)

        if file_obj.status == "missing":
            print("❌ FullFileManager.get_file_preview_by_id: file is missing")
            return False
        return file_obj.preview()

    def get_files_list_by_type(self, type_name: str) -> list[FileInfos] | bool:
        """
        Get a list of files from the application by its type
        :param type_name:
        :return:
        """
        if type_name is None or type_name == "":
            print("❌ FullFileManager.get_files_list_by_type: type_name is None or empty")
            return False
        if not self.files_types.is_type(type_name):
            print(f"❌ FullFileManager.get_files_list_by_type: {type_name} is not a valid type")
            return False
        file_list = self.es_manager.get_files_by_type(type_name)
        if file_list is False or file_list is None:
            print("❌ FullFileManager.get_files_list_by_type: file_list is False")
            return False
        files_obj = []
        for file_doc in file_list:
            file_obj = FileInfos()
            file_obj.set_from_doc(file_doc)
            if file_obj is not None:
                files_obj.append(file_obj)
        return files_obj

    def get_datas_files_list(self) -> list[FileInfos] | bool:
        """
        Get a list of files from the application by its type
        :return:
        """
        file_list = self.es_manager.get_files_by_type(self.files_types.datas.name)
        if file_list is False or file_list is None:
            print("❌ FullFileManager.get_datas_files_list: file_list is False")
            return False
        files_obj = []
        for file_doc in file_list:
            file_obj = FileInfos()
            file_obj.set_from_doc(file_doc)
            if file_obj is not None:
                files_obj.append(file_obj)
        return files_obj

    def get_mappings_files_list(self) -> list[FileInfos] | bool:
        """
        Get a list of files from the application by its type
        :return:
        """
        file_list = self.es_manager.get_files_by_type(self.files_types.mappings.name)
        if file_list is False or file_list is None:
            print("❌ FullFileManager.get_mappings_files_list: file_list is False")
            return False
        files_obj = []
        for file_doc in file_list:
            file_obj = FileInfos()
            file_obj.set_from_doc(file_doc)
            if file_obj is not None:
                files_obj.append(file_obj)
        return files_obj

    def update_es_file_index(self):
        """
        Update the ElasticSearch index with the files in the folders
        """
        files_list_es = self.es_manager.get_files_from_es()
        files_list_es_obj = self._set_file_es_to_files_infos(files_list_es)
        files_list_folder_obj = self._get_all_files_from_folders()
        ids_missing = self._verify_file_es_missing(files_list_es_obj)
        docs_to_add = self._compare_list_files(files_list_es_obj, files_list_folder_obj)
        if len(ids_missing) > 0:
            print(f"📊 FullFileManager.update_es_file_index: {len(ids_missing)} files missing in ES")
            self.es_manager.set_files_statut_to_missing(ids_missing)
        if len(docs_to_add) > 0:
            return self.es_manager.es_tools.bulk_import(self.config.index_files_name, docs_to_add)

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the application
        """
        print(f"FullFileManager.delete_file: file_id {file_id}")
        if file_id is None or file_id == "":
            print("❌ FullFileManager.delete_file: file_id is None or empty")
            return False
        doc = self.es_manager.get_file_by_id(file_id)
        print(f"********************{doc}")
        if doc is None:
            print("❌ FullFileManager.delete_file: file not found in ES")
            return False
        file_obj = FileInfos()
        file_obj.set_from_doc(doc)
        filepath = file_obj.file_path
        if filepath is None or filepath == "":
            filepath = os.path.join(file_obj.type.folder_path, file_obj.file_name)
        if not os.path.isfile(filepath):
            print("❌ FullFileManager.delete_file: file not found on disk")
            return False
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"❌ FullFileManager.delete_file: {e}")
            return False
        return self.es_manager.delete_file(file_id)

    @staticmethod
    def _save_secure_file(file_to_save: FileStorage, folder_path: str) -> bool | dict[str, str]:
        """
        Enregistre un fichier FileStorage avec un nom de fichier unique basé sur un timestamp.

        :param file_to_save (FileStorage): Le fichier reçu via un formulaire (Flask).
        :param folder_path (str): Le chemin du dossier où enregistrer le fichier.
        :return: Un dictionnaire contenant le nom de fichier initial et le nom de fichier enregistré.
        :raise: Retourne False si une erreur survient.
        """

        if file_to_save is None:
            print("❌ FullFileManager._save_secure_file: file_to_save is None")
            return False
        if folder_path is None or folder_path == "":
            print("❌ FullFileManager._save_secure_file: folder_path is None or empty")
            return False
        try:
            # Sécurise le nom de fichier pour éviter les caractères spéciaux
            base_name = secure_filename(file_to_save.filename)
            name, ext = os.path.splitext(base_name)

            # Crée un nom de fichier unique avec le timestamp
            unique_name = f"{uuid.uuid4().hex}{ext}"

            # Construit le chemin complet du fichier
            file_path = str(os.path.join(folder_path, unique_name))

            # S'assure que le dossier existe
            os.makedirs(folder_path, exist_ok=True)

            # Sauvegarde le fichier
            file_to_save.save(file_path)

            return {"initial_filename": base_name, "saved_file_name": unique_name, "filepath": file_path}

        except Exception as e:
            print(f"❌ FullFileManager._save_secure_file: {e}")
            return False

    @staticmethod
    def _set_file_infos(filepath, initial_filename: str) -> FileInfos | bool:
        """
        Crée un objet FileInfos à partir d'un fichier uploadé et des informations de sauvegarde.
        :param filepath:
        :param initial_filename:
        :return: Un objet FileInfos ou False en cas d'erreur.
        """
        try:
            file_obj = FileInfos(filepath=filepath)
            file_obj.initial_file_name = initial_filename
            file_obj.front_end_file_name = initial_filename
            return file_obj
        except Exception as e:
            print(f"❌ FullFileManager.upload_file fileInfos creation failed : {e}")
            return False

    @staticmethod
    def _set_file_es_to_files_infos(files_list_es: list) -> list[FileInfos]:
        """
        Set the files from ElasticSearch to FileInfos
        :param files_list_es:
        :return:
        """
        files_list_es_obj = []
        for fles in files_list_es:
            if fles is not None:
                ftemp = FileInfos()
                ftemp.set_from_doc(fles)
                if ftemp is not None:
                    files_list_es_obj.append(ftemp)
        return files_list_es_obj

    @staticmethod
    def _verify_file_es_missing(files_es_obj: list[FileInfos]) -> list[str]:
        """
        Verify if the files in the folders are in the ElasticSearch index
        :param files_es_obj:
        :return:
        """
        ids = []
        if files_es_obj is None:
            return []
        list_files = []
        for file_es_obj in files_es_obj:
            filepath = file_es_obj.file_path
            if filepath is None or filepath == "":
                filepath = os.path.join(file_es_obj.type.folder_path, file_es_obj.file_name)
            if not os.path.isfile(filepath):
                list_files.append(file_es_obj)
        if len(list_files) > 0:
            ids = [f.id for f in list_files]
        return ids

    def _get_all_files_from_folders(self) -> list[FileInfos]:
        """
        Liste tous les fichiers dans les folders définis par chaque FileType.
        Retourne une liste d'objets FileInfos.
        """
        all_file_infos = []
        for file_type in self.files_types.list:
            folder = file_type.folder_path
            if not os.path.isdir(folder):
                continue
            for file_name in os.listdir(folder):
                full_path = os.path.join(folder, file_name)
                if os.path.isfile(full_path):
                    fi = FileInfos(filepath=full_path)
                    fi.front_end_file_name = file_name
                    fi.initial_file_name = file_name
                    all_file_infos.append(fi)
        return all_file_infos

    @staticmethod
    def _compare_list_files(files_list_es: list[FileInfos], files_list_folder: list[FileInfos]) -> list[dict]:
        """
        Compare la liste des fichiers dans les dossiers avec la liste des fichiers indexés dans ElasticSearch.
        Retourne une liste de documents à ajouter dans ES.

        :param files_list_es: fichiers présents dans ES (objets FileInfos)
        :param files_list_folder: fichiers présents sur disque (objets FileInfos)
        :return: liste de dicts représentant les docs à indexer
        """
        files_to_add = []

        # 🔄 Normalisation des chemins indexés
        normalized_es_paths = set()
        for fle_es in files_list_es:
            if fle_es is None:
                continue
            esfilepath = fle_es.file_path or os.path.join(fle_es.type.folder_path, fle_es.file_name)
            normalized_es_paths.add(os.path.normpath(esfilepath))

        # 🔍 Comparaison avec les chemins du système de fichiers
        for fle in files_list_folder:
            ffilepath = os.path.normpath(fle.file_path)
            if ffilepath not in normalized_es_paths:
                files_to_add.append(fle)

        docs_to_add = [f.get_doc() for f in files_to_add]
        return docs_to_add

    def save_file(self, file_type: str, datas: str) -> bool:
        """
        recoit un json avec les données du fichier depuis un adresse url
        Enregistre un fichier dans le dossier correspondant à son type
        A partir du nom du type, on détermine le dossier de destination

        :param file_type:
        :param datas:
        :return:
        """
        print(f"FullFileManager.save_file: file_type {file_type} datas {datas}")
        return True

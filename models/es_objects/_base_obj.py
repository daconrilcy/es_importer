import json
import pathlib
from datetime import datetime
from idlelib.editor import keynames
from typing import Optional, Dict

from werkzeug.datastructures import FileStorage

from models.file_type import FileType, FileTypes
from utils import get_folder_path_from_filepath, generate_filename, set_datetime_in_str, get_dict_from_json, \
    get_creation_date


class BaseObject:
    """
    Classe de base pour représenter un objet avec ses attributs liés à un fichier.
    :param file_type: Type de fichier (FileType ou nom de type en str)
    :return: None
    """

    def __init__(self,
                 es_id: Optional[str] = None,
                 filepath: Optional[str] = None,
                 filename: Optional[str] = None,
                 original_filename: Optional[str] = None,
                 front_name: Optional[str] = None,
                 separator: Optional[str] = None,
                 description: Optional[str] = None,
                 index_name: Optional[str] = None,
                 created_at: Optional[str | datetime] = None,
                 status: Optional[str] = None,
                 fields: Optional[dict | list] = None,
                 file_type: Optional[FileType | str] = None,
                 initial_file: Optional[str] = False,
                 ):
        # Initialisation des attributs internes
        self._id = None
        self._filepath = None
        self._filename = None
        self._original_filename = None
        self._headers = None
        self._separator = None
        self._extension = None
        self._front_name = None
        self._description = ""
        self._file_type = None
        self._index_name = None
        self._created_at = None
        self._status = None
        self._initial_file = initial_file
        self._fields = {}

        # Utilisation des setters après l'init des attributs internes
        self.fileTypes = FileTypes()
        self.id = es_id
        self.filepath = filepath
        self.filename = filename
        self.original_filename = original_filename
        self.separator = separator
        self.front_name = front_name
        self.description = description
        self.file_type = file_type
        self.index_name = index_name
        self.created_at = created_at
        self.status = status
        self.fields = fields

    @property
    def id(self) -> str:
        """Retourne l'identifiant de l'objet."""
        return self._id

    @id.setter
    def id(self, es_id: Dict | str | None):
        if es_id is None:
            return
        if isinstance(es_id, dict):
            keynames_id = ["id", "es_id", "file_id", "_id", "id_file", "_id_file"]
            for key in keynames_id:
                if key in es_id:
                    es_id = es_id[key]
                    break
        self._id = es_id

    @property
    def filepath(self) -> str:
        """Retourne le chemin du fichier."""
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: Dict | str):
        if filepath is None:
            return
        if isinstance(filepath, dict):
            keynames_filepath = ["filepath", "file_path"]
            for key in keynames_filepath:
                if key in filepath:
                    filepath = filepath[key]
                    break
        self._filepath = pathlib.Path(filepath)
        if self.file_type is None:
            folder = get_folder_path_from_filepath(filepath)
            self.file_type = self.fileTypes.get_file_type_by_folder_path(folder)

        if self._filename is None or self._filename == "":
            self.filename = self._filepath.name

    @property
    def filename(self) -> str:
        """Retourne le nom du fichier."""
        if self._filename is None:
            return pathlib.Path(self.filepath).name
        return self._filename

    @filename.setter
    def filename(self, filename: Dict | str | None):
        if filename is None:
            return
        if isinstance(filename, dict):
            keynames_filename = ["filename", "file_name"]
            for key in keynames_filename:
                if key in filename:
                    filename = filename[key]
                    break
        self._filename = filename
        if self._front_name is None or self._front_name == "":
            self._front_name = pathlib.Path(filename).stem
        if self._original_filename is None or self._original_filename == "":
            self._original_filename = filename
        if self._extension is None or self._extension == "":
            self._extension = pathlib.Path(filename).suffix

    @property
    def original_filename(self) -> str | None:
        """
        return the original File name of the file if exists
        :return:
        """
        if self._original_filename is None:
            return self._filename
        return self._original_filename

    @original_filename.setter
    def original_filename(self, original_filename: Dict | str | None):
        if isinstance(original_filename, dict):
            keynames_orig = ["original_filename", "original_name", "original_file_name",
                             "initial_file_name", "initial_name"]
            for key in keynames_orig:
                if key in original_filename:
                    original_filename = original_filename[key]
                    break
        self._original_filename = original_filename

    @property
    def headers(self) -> list[str]:
        """Retourne les en-têtes du fichier."""
        return self._headers

    @headers.setter
    def headers(self, headers: list | None):
        if not headers or not isinstance(headers, list):
            self._headers = []
            return
        self._headers = headers

    @property
    def separator(self) -> str:
        """Retourne le séparateur."""
        return self._separator

    @separator.setter
    def separator(self, separator: Dict | str | None):
        if isinstance(separator, dict):
            keynames_sep = ["separator", "sep", "separator_name", "datas_separator"]
            for key in keynames_sep:
                if key in separator:
                    separator = separator[key]
                    break
        self._separator = separator

    @property
    def extension(self) -> str:
        """Retourne l'extension du fichier."""
        return self._extension

    @extension.setter
    def extension(self, extension: Dict | str | None):
        if isinstance(extension, dict):
            extension = extension.get("extension", None)
        self._extension = extension

    @property
    def front_name(self) -> str:
        """Retourne le nom d'affichage de l'objet."""
        if self._front_name is None:
            if self.filename is None:
                return ""
            self._front_name = pathlib.Path(self.filename).stem
        return self._front_name

    @front_name.setter
    def front_name(self, front_name: Dict | str | None):
        if not front_name:
            self._front_name = ""
            return
        if isinstance(front_name, dict):
            keynames_front = ["front_name", "frontname", "display_name", "front_end_name", "frontend_name", "front_end"]
            for key in keynames_front:
                if key in front_name:
                    front_name = front_name[key]
                    break
        self._front_name = front_name

    @property
    def file_type(self) -> FileType:
        """Retourne le type de fichier."""
        return self._file_type

    @file_type.setter
    def file_type(self, file_type_to_set: FileType | Dict | str | None):
        self._file_type = None
        if isinstance(file_type_to_set, FileType):
            self._file_type = file_type_to_set
            return
        if isinstance(file_type_to_set, dict):
            keynames_types = ["file_type", "type", "type_file", "filetype", "file_type_name", "typefile"]
            for key in keynames_types:
                if key in file_type_to_set:
                    file_type_to_set = file_type_to_set[key]
                    break
        if isinstance(file_type_to_set, str):
            self._file_type = self.fileTypes.get_file_type_by_name(file_type_to_set)

    @property
    def description(self) -> str:
        """Retourne la description de l'objet."""
        return self._description

    @description.setter
    def description(self, description: str | Dict):
        if not description:
            self._description = ""
            return
        if isinstance(description, dict):
            description = description.get("description", "")
        self._description = description

    @property
    def index_name(self) -> str:
        """Retourne le nom de l'index."""
        return self._index_name

    @index_name.setter
    def index_name(self, index_name: str | Dict | None):
        if isinstance(index_name, dict):
            index_name = index_name.get("index_name", None)
        self._index_name = index_name

    @property
    def created_at(self) -> str:
        """Retourne la date de création."""
        return self._created_at

    @created_at.setter
    def created_at(self, created_at: Dict | str | None | datetime = None):
        if isinstance(created_at, dict):
            keys_crea = ["created_at", "uploaded_at", "upload_date"]
            self.created_at = None
            for key in keys_crea:
                result = created_at.get(key, None)
                if result is not None:
                    self.created_at = result
                    break

        self._created_at = set_datetime_in_str(created_at)

    @property
    def status(self):
        """
        retourne le status du fichier
        :return:
        """
        return self._status

    @status.setter
    def status(self, status: Dict | str | None):
        if isinstance(status, dict):
            status = status.get("status", None)
        self._status = status

    @property
    def initial_file(self) -> bool:
        """Retourne si le fichier est un fichier initial."""
        return self._initial_file

    @initial_file.setter
    def initial_file(self, initial_file: bool):
        if not isinstance(initial_file, bool):
            self._initial_file = False
            return
        self._initial_file = initial_file

    @property
    def fields(self) -> dict:
        """Dictionnaire de champs de mapping."""
        return self._fields

    @fields.setter
    def fields(self, value: dict | list):
        if not isinstance(value, dict) and not isinstance(value, list):
            print("❌ fields : doit être un dictionnaire ou une liste")
            return
        self._fields = value

    @property
    def base_dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire de base.
        :return: Dict
        """
        return {
            "id": self.id,
            "filepath": str(self.filepath) if self.filepath else None,
            "filename": self.filename if self.filename else None,
            "front_name": self.front_name,
            "separator": self.separator,
            "description": self.description,
            "file_type": self.file_type.name if self.file_type else None,
            "index_name": self.index_name,
            "created_at": self._created_at,
            "status": self.status,
        }

    @base_dict.setter
    def base_dict(self, data: dict):
        """
        Initialise l'objet à partir d'un dictionnaire de base.
        :param data: Dict
        :return: bool
        """
        if not data:
            print("❌ BaseObject.set_base_dict: data is None")
            return

        self.id = data
        self.filepath = data
        self.filename = data
        self.front_name = data
        self.separator = data
        self.description = data
        self.file_type = data
        self.index_name = data
        self.created_at = data
        self.status = data

    @property
    def dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire.
        :return: Dict
        """
        return self.base_dict

    @dict.setter
    def dict(self, data: dict) -> bool:
        """
        Initialise l'objet à partir d'un dictionnaire.
        :param data: Dict
        :return: bool
        """
        if not data:
            print("❌ BaseObject.set_from_dict: data is None")
            return

        self.base_dict = data

    @property
    def base_dict_file(self):
        """
        Convertit l'objet en dictionnaire pour le fichier.
        :return:
        """
        base_dict = self.base_dict
        base_dict.pop("file_type", None)
        base_dict.pop("filename", None)
        base_dict.pop("filepath", None)
        base_dict.pop("created_at", None)
        if base_dict["id"] is None:
            base_dict.pop("id", None)

        return base_dict

    @property
    def dict_file(self) -> dict:
        """
        Convertit l'objet en dictionnaire pour le fichier.
        :return: Dict
        """
        base_dict = self.base_dict_file
        return base_dict

    @property
    def to_file(self) -> bool:
        """
        Sauvegarde l'objet sous forme de fichier JSON.
        :return: bool
        """
        if not self.filepath:
            if not self.filename:
                if not self.file_type or not self._rebuild_filepath():
                    print("❌ BaseObject.save: rebuild or file_type failed")
                    return False
            else:
                if not self.file_type:
                    print("❌ BaseObject.save: file_type is None")
                    return False
                self.filepath = pathlib.Path(self.file_type.folder_path) / self.filename

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.dict_file, f, indent=4, ensure_ascii=False)
        return True

    def load_from_filepath(self, filepath: str = None) -> bool:
        """
        Initialise l'objet à partir d'un fichier JSON.
        :param filepath: Chemin du fichier JSON
        :return: bool
        """
        filepath = filepath or self.filepath
        if not filepath:
            print("❌ BaseObject.set_from_filepath: filepath is None or empty")
            return False
        if not pathlib.Path.is_file(filepath):
            print(f"❌ BaseObject.set_from_filepath: filepath {filepath} is not a file")
            return False
        self.filepath = filepath
        self.created_at = get_creation_date(filepath)

        data = get_dict_from_json(self.filepath)
        if not data:
            print("❌ BaseObject.set_from_filepath: data is None or empty")
            return False
        if not isinstance(data, dict):
            print("❌ BaseObject.set_from_filepath: data is not a dict")
            return False
        self.dict = data
        return True

    def load_from_filename(self, filename: str = None) -> bool:
        """
        Charge l'objet à partir d'un fichier JSON.
        :param filename: Nom du fichier
        :return: bool
        """
        filename = filename or self.filename

        if not self.filename:
            print("❌ BaseObject.load_from_filename: filename is None")
            return False
        if filename:
            self.filepath = None
            self.filename = filename
        self.load_from_filepath()

    @property
    def json(self) -> str:
        """
        Convertit l'objet en JSON.
        :return: str
        """
        return json.dumps(self.dict, indent=4, ensure_ascii=False)

    def _rebuild_filepath(self) -> bool:
        """
        Reconstruit le chemin du fichier si nécessaire.
        :return: Bool
        """
        if not self.file_type:
            print("❌ BaseObject._rebuild_filepath: file_type is None")
            return False
        new_filename = generate_filename(self.file_type.accepted_extensions[0])
        self.filename = new_filename
        self.filepath = pathlib.Path(self.file_type.folder_path) / new_filename
        return True

    def set_from_upload_default(self, file: FileStorage):
        """ Set the file infos from an upload """
        if file is None:
            print("❌ FileInfos.set_from_upload: Invalid file")
            return
        if self.file_type is None:
            print("❌ FileInfos.set_from_upload: Invalid file type")
            return
        self.filename = file.filename
        self.created_at = None
        self.status = "uploaded"

    def set_from_upload(self, file: FileStorage) -> bool:
        """
        file information from an file uploaded through the website
        :param file:
        :return:
        """
        if file is None:
            print("❌ BaseObject.set_from_upload: Invalid file")
            return False
        original_filename = file.filename
        self.set_from_upload_default(file)

    def to_file_es_doc(self) -> dict:
        """
        Convertit l'objet en document Elasticsearch.
        :return: dict
        """
        extention = "json"
        if self.filename is not None and "." in self.filename:
            extention = self.filename.split(".")[-1]
        doc = {
            "type": self.file_type.name if self.file_type else "",
            "extension": extention if self.filename else "",
            "file_name": self.filename if self.filename else "",
            "initial_file_name": self.original_filename if self.original_filename else "",
            "front_end_file_name": self.front_name if self.front_name else "",
            "separator": self.separator if self.separator else "",
            "upload_date": self.created_at,
            "description": self.description if self.description else "",
            "initial_file": self.initial_file if self.initial_file else False,
            "status": self.status if self.status else "new",
        }
        if self.id is not None:
            doc["_id"] = self.id

        return doc

    def save_file_in_es(self) -> bool:
        """
        Sauvegarde le fichier dans Elasticsearch.
        :return:
        """
        doc = self.to_file_es_doc()
        if not doc:
            print("❌ BaseObject.save_file_in_es: Invalid doc")
            return False

    def __str__(self):
        """
        Convertit l'objet en chaîne de caractères.
        :return: str
        """
        return json.dumps(self.dict, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Test the BaseObject class
    obj = BaseObject()
    obj.filepath = r"C:\dev\py\csv_importer\files\datas\curiexplore-pays.csv"
    print(f"*****{obj.file_type.name}*****")
    obj.filename = "test.txt"
    obj.front_name = "Test File"
    obj.description = "This is a test file."
    obj.file_type = "mappings"
    print(f"*****{obj.file_type.name}*****")
    obj.index_name = "test_index"
    obj.created_at = datetime.now()
    obj.status = "active"
    obj.fields = {"field1": "value1", "field2": "value2"}

    print(obj)
    print("to_es_doc", obj.to_file_es_doc())

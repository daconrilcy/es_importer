import csv
from datetime import datetime, timezone
import os

from werkzeug.datastructures import FileStorage

from models.file_type import FileType, FileTypes
from models.previewer import Previewer


class FileInfos:
    """
    Class used to store information about a file.
    """

    def __init__(self, filepath: str = None):
        self._id = None
        self._file_name = None
        self._initial_file_name = None
        self._front_end_file_name = None
        self._file_path = None
        self._type = None
        self._extension = None
        self._created_at = None
        self._description = ""
        self._types = FileTypes()
        self._separator = None
        self._status = None
        self._previewer = None
        if filepath is not None:  # Calls the setter
            self.file_path = filepath

    @property
    def id(self) -> str | int:
        """
        Get the id of the file
        :return:
        """
        return self._id

    @property
    def file_name(self) -> str:
        """
        Get the file name
        :return:
        """
        return self._file_name

    @file_name.setter
    def file_name(self, value: str):
        self._file_name = value
        self.extension = value.split(".")[-1] if "." in value else ""

    @property
    def initial_file_name(self) -> str:
        """
        Get the initial file name
        :return:
        """
        return self._initial_file_name

    @initial_file_name.setter
    def initial_file_name(self, value: str):
        self._initial_file_name = value

    @property
    def front_end_file_name(self) -> str:
        """
        Get the front end file name
        :return:
        """
        return self._front_end_file_name

    @front_end_file_name.setter
    def front_end_file_name(self, value: str):
        self._front_end_file_name = value

    @property
    def file_path(self) -> str:
        """
        Get the file path
        :return:
        """
        return self._set_default_file_path()

    def _set_default_file_path(self):
        if self._file_path is None:
            if self._file_name is not None and self._file_name != "":
                if self._type is not None and self._type.folder_path is not None:
                    self._file_path = os.path.join(self._type.folder_path, self._file_name)
        return self._file_path

    @file_path.setter
    def file_path(self, value: str):
        if not value or not os.path.isfile(value):
            print(f"❌ FileInfos.file_path: Invalid file path - {value}")
            self._file_path = None
            return
        value = value.replace("\\", os.sep)
        value = value.replace("/", os.sep)
        self._file_path = value
        self.file_name = os.path.basename(value)
        folder_name = os.path.dirname(value)
        if self.type is None:
            self.type = self._types.get_file_type_by_folder(folder_name)
        self.created_at = datetime.fromtimestamp(os.path.getctime(value), tz=timezone.utc)
        self._get_separator_from_file()

    @property
    def type(self) -> FileType | None:
        """
        Get the type of the file
        :return:
        """
        return self._type

    @type.setter
    def type(self, value: str | FileType):
        if isinstance(value, FileType):
            temp_ft = value
        elif isinstance(value, str):
            if not self._types.is_type(value):
                print(f"❌ FileInfos.type: Invalid type - {value}")
                self._type = None
                return
            temp_ft = self._types.get_file_type_by_name(value)
        else:
            print(f"❌ FileInfos.type: Invalid type - {value}")
            return
        if temp_ft is not None:
            if self._type is not None and not self._type.compare(temp_ft):
                print(f"⚠️ FileInfos.type: Type already set : {self._type.name} => changing to `{temp_ft.name}`")
            self._type = temp_ft

    @property
    def created_at(self) -> str:
        """
        Get the creation date of the file
        :return:
        """
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        if isinstance(value, datetime):
            self._created_at = value.astimezone(timezone.utc).isoformat()
        elif isinstance(value, str):
            try:
                self._created_at = datetime.fromisoformat(value.replace("Z", "")).astimezone(timezone.utc).isoformat()
            except ValueError:
                print(f"❌ FileInfos.created_at: Invalid datetime format - {value}")
                self._created_at = datetime.now(timezone.utc).isoformat()
        else:
            self._created_at = None

    @property
    def extension(self) -> str:
        """
        Get the extension of the file
        :return:
        """
        return self._extension

    @extension.setter
    def extension(self, value: str):
        self._extension = value.lower() if value else ""

    @property
    def separator(self) -> str:
        """
        Get the separator of the file
        :return:
        """
        return self._separator

    @separator.setter
    def separator(self, value: str):
        if value is None:
            value = ","
        self._separator = value

    @property
    def description(self) -> str:
        """
        Get the description of the file
        :return:
        """
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value if value else ""

    @property
    def status(self) -> str:
        """
        Get the status of the file
        :return:
        """
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value if value else ""

    def get_doc(self) -> dict:
        """ Get the base document of the file for Elasticsearch """
        if self.type is None:
            type_file = ""
        else:
            type_file = self.type.name
        if self.initial_file_name is None or self.initial_file_name == "":
            self.initial_file_name = self.file_name
        if self.front_end_file_name is None or self.front_end_file_name == "":
            self.front_end_file_name = self.file_name
        return {
            "_id": self._id,
            "type": type_file,
            "extension": self.extension,
            "file_name": self.file_name,
            "initial_file_name": self._initial_file_name,
            "front_end_file_name": self._front_end_file_name,
            "upload_date": self.created_at,
            "separator": self.separator,
            "description": self.description,
            "status": self.status
        }

    def set_from_doc(self, doc: dict) -> None:
        """ Set the file infos from a document """
        if not doc or "file_name" not in doc or "type" not in doc:
            print("❌ FileInfos.set_from_doc: Invalid document")
            return
        self._id = doc.get("_id", None)
        self.file_name = doc["file_name"]
        self.initial_file_name = doc.get("initial_file_name", self.file_name)
        self.front_end_file_name = doc.get("front_end_file_name", self.file_name)
        self.type = doc["type"]
        self.extension = doc.get("extension", self.file_name.split(".")[-1] if "." in self.file_name else "")
        self.created_at = doc.get("upload_date", datetime.now(timezone.utc).isoformat())
        self.separator = doc.get("separator", ",")
        self.description = doc.get("description", "")
        self.status = doc.get("status", "")
        self._set_default_file_path()

    def set_from_upload(self, file: FileStorage, file_type: FileType | str, initial_filename: str = None,
                        front_end_name: str = None, description: str = ""):
        """ Set the file infos from an upload """
        if file is None:
            print("❌ FileInfos.set_from_upload: Invalid file")
            return
        if file_type is None or file_type == "":
            print("❌ FileInfos.set_from_upload: Invalid file type")
            return
        self.file_name = file.filename
        self.initial_file_name = file.filename
        self.front_end_file_name = file.filename
        if initial_filename is not None:
            self.initial_file_name = initial_filename
        if front_end_name is not None:
            self.front_end_file_name = front_end_name
        self.type = file_type
        self.created_at = datetime.now(timezone.utc).isoformat()
        self._get_separator_from_file()
        self.description = description
        self.status = "uploaded"
        self._set_default_file_path()

    def preview(self):
        """
        :return:
        """
        return Previewer(
            layout=self.type.html_preview_layout,
            method=self.type.method_preview,
            front_name=self._front_end_file_name,
            filename=self.file_name,
            filepath=self.file_path,
            sep=self.separator,
            file_id=self._id,
            file_type=self.type.name
        )

    def __str__(self):
        return f"FileInfos({self.get_doc()})"

    def _get_separator_from_file(self):
        """
        Détecte automatiquement le séparateur d'un fichier CSV
        Tres lent pour le json → à éviter pour ce type de fichier
        """
        if self._extension != "csv":
            self._separator = ","
            return None

        if self._file_path is None or not os.path.isfile(self._file_path):
            return None
        with open(self._file_path, newline='') as f:
            # On lit uniquement la première ligne pour éviter les perturbations
            first_line = f.readline()
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(first_line)
                self._separator = dialect.delimiter
            except csv.Error:
                self._separator = ","  # valeur par défaut pour ce genre de fichiers

    def reset(self):
        """ Reset the file infos """
        self._file_name = None
        self._file_path = None
        self._type = None
        self._extension = None
        self._created_at = None
        self._separator = None
        self._description = ""
        self._status = None


if __name__ == "__main__":
    fi_test = FileInfos()
    fi_test.file_path = "C:\\dev\\py\\csv_importer\\files\\datas\\curiexplore-pays.csv"
    print(fi_test)
    print(fi_test.separator)
    #fi_test.type = "mappings"
    print(fi_test.type.folder_path)
    print(fi_test.type.html_preview_layout)
    print(fi_test.preview())

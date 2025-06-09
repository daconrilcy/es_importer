from pathlib import Path
from typing import Union, Optional
from datetime import datetime

from models.date_formater import MultiDateFormater
from models.file_type import FileType
from config import Config


class FileInfos:
    """
    Classe utilitaire pour transformer un document ES (index 'file_details') en objet Python.
    Gère aussi l'objet FileType associé et le chemin physique du fichier.
    """

    def __init__(self, doc: Optional[dict] = None):
        self._id: Optional[Union[str, int]] = None
        self._filename: Optional[str] = None
        self._original_filename: Optional[str] = None
        self._front_end_filename: Optional[str] = None
        self._type: Optional[FileType] = None
        self._extension: Optional[str] = None
        self._created_at: Optional[str] = None
        self._date_updated: Optional[str] = None
        self._description: str = ""
        self._separator: Optional[str] = None
        self._status: Optional[str] = None
        self._filepath: Optional[str] = None
        self._encoded_filepath: Optional[str] = None

        if doc:
            self._initialize_from_doc(doc)

    def _initialize_from_doc(self, doc: dict) -> None:
        if "filename" not in doc or "type" not in doc:
            raise ValueError("Document invalide : 'filename' et 'type' sont requis")

        self._id = doc.get("_id")
        self._filename = doc["filename"]
        self._original_filename = doc.get("original_filename", self.filename)
        self._front_end_filename = doc.get("front_end_filename", Path(self._original_filename).stem)
        self.type = doc.get("type") or doc.get("file_type", "")
        self._extension = doc.get("extension", self._filename.split(".")[-1] if "." in self._filename else "")
        self.created_at = doc.get("upload_date", None)
        self.date_updated = doc.get("date_updated", None)
        self._separator = doc.get("separator") or doc.get("sep", None)
        self._description = doc.get("description", "")
        self._status = doc.get("status", "")
        self._encoded_filepath = doc.get("encoded_filepath")

        self._set_filepath()

    def _set_filepath(self) -> None:
        if self.type and self.filename:
            folder = self._type.folder_path
            self._filepath = Path(folder) / self._filename

    # Properties et setters

    @property
    def id(self) -> Optional[Union[str, int]]:
        """Retourne l'identifiant du fichier."""
        return self._id

    @property
    def filename(self) -> Optional[str]:
        """Retourne le nom du fichier sur le disque."""
        return self._filename

    @property
    def original_filename(self) -> Optional[str]:
        """Retourne le nom de fichier original (avant traitement)."""
        return self._original_filename

    @property
    def front_end_filename(self) -> Optional[str]:
        """Retourne le nom de fichier utilisé pour l'affichage en front-end."""
        return self._front_end_filename

    @property
    def type(self) -> Optional[FileType]:
        """Retourne l'objet FileType associé au fichier."""
        return self._type

    @type.setter
    def type(self, type_file: Union[FileType, str]) -> None:
        if isinstance(type_file, str):
            self._type = Config().file_types.get(name=type_file)
        elif isinstance(type_file, FileType):
            self._type = type_file
        else:
            self._type = None

    @property
    def type_name(self) -> Optional[str]:
        """Retourne le nom du type de fichier (ex: 'datas', 'mapping')."""
        return self._type.name if self._type else None

    @property
    def extension(self) -> Optional[str]:
        """Retourne l'extension du fichier (ex: 'csv')."""
        return self._extension

    @property
    def created_at(self) -> Optional[str]:
        """Retourne la date de création (upload) du fichier."""
        return self._created_at

    @property
    def date_updated(self) -> Optional[str]:
        """Retourne la date de mise à jour du fichier."""
        return self._date_updated

    @property
    def separator(self) -> Optional[str]:
        """Retourne le séparateur utilisé dans le fichier (utile pour CSV)."""
        return self._separator

    @property
    def description(self) -> str:
        """Retourne la description du fichier, si disponible."""
        return self._description

    @property
    def status(self) -> Optional[str]:
        """Retourne le statut du fichier (ex: 'processed', 'error')."""
        return self._status

    @property
    def filepath(self) -> Optional[str]:
        """Retourne le chemin absolu du fichier sur le disque."""
        return self._filepath

    def get_doc(self) -> dict:
        """Retourne un dictionnaire formaté pour l'indexation Elasticsearch (DTO)."""
        doc = {
            "filename": self.filename,
            "original_filename": self.original_filename,
            "type": self.type_name,
            "extension": self.extension,
            "separator": self.separator,
            "status": self.status,
            "upload_date": self.created_at,
            "date_updated": self.date_updated,
        }
        if self.id is not None:
            doc["id"] = self.id
        return doc

    def __str__(self) -> str:
        return f"FileInfos({self.__dict__})"

    @id.setter
    def id(self, value: Union[str, int]) -> None:
        self._id = value

    @filename.setter
    def filename(self, value: str) -> None:
        self._filename = value
        self._set_filepath()

    @original_filename.setter
    def original_filename(self, value: str) -> None:
        self._original_filename = value

    @front_end_filename.setter
    def front_end_filename(self, value: str) -> None:
        self._front_end_filename = value

    @extension.setter
    def extension(self, value: str) -> None:
        self._extension = value
        self._set_filepath()

    @created_at.setter
    def created_at(self, value: Union[str, datetime, None]) -> None:
        self._created_at = MultiDateFormater().to_es(value)

    @date_updated.setter
    def date_updated(self, value: Union[str, datetime, None]) -> None:
        """
        :param value:
        :return:
        """
        self._date_updated = MultiDateFormater().to_es(value)

    @separator.setter
    def separator(self, value: str) -> None:
        self._separator = value

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def encoded_filepath(self) -> Optional[str]:
        """Retourne le chemin absolu du fichier sur le disque."""
        return self._encoded_filepath

    @encoded_filepath.setter
    def encoded_filepath(self, value: str) -> None:
        self._encoded_filepath = value


# Exemple de test unitaire minimal (à mettre dans un fichier de test séparé)
def test_file_infos_creation():
    doc = {"filename": "test.csv", "type": "datas"}
    infos = FileInfos(doc)
    assert infos.filename == "test.csv"
    assert infos.type_name == "datas"

from pathlib import Path
from typing import Optional, Dict, Any

from config import Config
import logging

from elastic_manager import ElasticManager
from models.file_management.file_utls import FileUtils
from models.file_management.filepath_codec import FilePathCodec
from models.mapping_management import FieldsManager

logger = logging.getLogger(__name__)


class MappingRequestTransformer:
    """
    Transforme et valide une requête de mapping.
    Permet d'instancier toutes les propriétés utiles à partir d'une requête utilisateur pour le mapping.
    """

    def __init__(self, request: Optional[Dict[str, Any]] = None, config: Optional[Config] = None) -> None:
        """
        Initialise le transformer à partir d'une requête utilisateur et d'une configuration optionnelle.
        """
        self._request: Dict[str, Any] = request
        self._config: Config = config or Config()
        self._id: Optional[str] = None
        self._encoded_data_filepath: Optional[str] = None
        self._data_filepath: Optional[str] = None
        self._mapping_name: Optional[str] = None
        self._mapping: Optional[Dict[str, Any]] = None
        self._codec: FilePathCodec = FilePathCodec()
        self._fields: Optional[Dict[str, Any]] = None
        self._filepath: Optional[str] = None
        self._filename: Optional[str] = None
        self._related_to: Optional[str] = None
        self._new_file: bool = False

    def _set_from_request(self, request: Dict[str, Any]) -> None:
        """
        Extrait les paramètres utiles de la requête utilisateur.
        """
        self._id = request.get("file_id")
        self._encoded_data_filepath = request.get("encoded_data_filepath")
        self._mapping_name = request.get("mapping_name")
        print(f"MappingRequestTransformer mapping_name: {self._mapping_name}")  # Ajout de cette ligne self._mapping_name)
        self._mapping = request.get("mapping")

    def transform(self, request: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transforme la requête pour initialiser toutes les propriétés nécessaires.
        Retourne True si tout s'est bien passé, False sinon.
        """
        req = request or self._request
        if req is None:
            logger.error("MappingRequestTransformer: request is None")
            return False

        self._set_from_request(req)
        if not self._set_data_filepath():
            return False
        if not self._set_fields():
            return False
        self._set_filepath()
        return True

    def _set_data_filepath(self) -> bool:
        """
        Décode et stocke le chemin du fichier source.
        Retourne True si succès, False sinon.
        """
        if self._encoded_data_filepath is None:
            logger.error("MappingRequestTransformer: encoded_data_filepath is None")
            return False
        try:
            self._data_filepath = self._codec.decode(self._encoded_data_filepath)
            self._related_to = Path(self._data_filepath).name
            return True
        except Exception as e:
            logger.error(
                f"MappingRequestTransformer: error decoding encoded_filepath: {e}"
            )
            return False

    def _set_fields(self) -> bool:
        """
        Instancie les champs à partir du mapping.
        Retourne True si succès, False sinon.
        """
        if self._mapping is None:
            logger.error("MappingRequestTransformer: mapping is None")
            return False
        mapping = {"mapping": self._mapping}
        try:
            fields_manager = FieldsManager(mapping, self._config)
            self._fields = fields_manager.fields
            return True
        except Exception as e:
            logger.error(f"MappingRequestTransformer: error setting fields: {e}")
            return False

    def _set_filepath(self) -> None:
        """
        Détermine le chemin du fichier de mapping associé à l'id, ou en génère un nouveau si absent.
        """
        if self.id is None:
            logger.info(
                "MappingRequestTransformer: id is None, generating filepath"
            )
            self._generate_filepath()
            self._new_file = True
            return
        es_manager = ElasticManager(self._config)
        file_infos = es_manager.files_obj.get_one(self.id)
        if not file_infos or not getattr(file_infos, "filepath", None):
            logger.error(
                f"MappingRequestTransformer: fichier absent pour id {self.id}, generation d'un nouveau filepath"
            )
            self._generate_filepath()
            return
        filepath = file_infos.filepath
        if not Path(filepath).exists():
            logger.error(
                f"MappingRequestTransformer: filepath {filepath} does not exist"
            )
            self._generate_filepath()
            return
        self._filepath = filepath
        self._filename = Path(filepath).name

    def _generate_filepath(self) -> None:
        """
        Génère un chemin de fichier de mapping nouveau et le stocke.
        """
        self._filename = FileUtils().generate_filename()
        # Utilise le folder_path défini dans FileTypes.mappings
        self._filepath = str(self._config.file_types.mappings.folder_path / self._filename)

    @property
    def data_filepath(self) -> Optional[str]:
        """
        Chemin décodé du fichier de données.
        """
        return self._data_filepath

    @property
    def mapping(self) -> Optional[Dict[str, Any]]:
        """
        Mapping brut transmis par l'utilisateur.
        """
        return self._mapping

    @property
    def fields(self) -> Optional[Dict[str, Any]]:
        """
        Dictionnaire des champs de mapping instanciés.
        """
        return self._fields

    @property
    def id(self) -> Optional[str]:
        """
        Identifiant du fichier dans la base.
        """
        return self._id

    @property
    def mapping_name(self) -> Optional[str]:
        """
        Nom du mapping.
        """
        return self._mapping_name

    @property
    def encoded_data_filepath(self) -> Optional[str]:
        """
        Chemin encodé du fichier de données.
        """
        return self._encoded_data_filepath

    @property
    def filepath(self) -> Optional[str]:
        """
        Chemin absolu du fichier de mapping utilisé ou généré.
        """
        return self._filepath

    @property
    def filename(self) -> Optional[str]:
        """
        Nom du fichier de mapping utilisé ou généré.
        """
        return self._filename

    @property
    def request(self) -> Optional[Dict[str, Any]]:
        """
        Requête utilisateur initiale.
        """
        return self._request

    @property
    def related_to(self) -> Optional[str]:
        return self._related_to

    @property
    def new_file(self) -> bool:
        return self._new_file


if __name__ == "__main__":
    # Exemple d'utilisation
    encoded_test = (
        "hdXE55u81wRh77I7BJipV_sKgF_g4_fur913_VR05wxDOlxkZXZccHlcY3N2X2ltcG9ydGVyXGZpbGVzXGRhdGFzXDAzNTg5MmE1LTI4MzAtNGJmNC04MjJkLWNjNGY1YjI0NDM5Zi5jc3Y="
    )
    request_test = {
        "file_id": "d5cKY5cBUmpRjBaYKbAU",
        "encoded_data_filepath": encoded_test,
        "mapping_name": "test_mapping_name",
        "mapping": {
            "flag": {
                "category": "source",
                "source_field": "flag",
                "name": "flag",
                "type": "text",
                "mapped": True,
                "analyzer": "standard",
                "description": "URL de l'image du drapeau du pays",
            }
        },
    }
    transformer_test = MappingRequestTransformer()
    if transformer_test.transform(request_test):
        print(transformer_test.data_filepath)
        print(transformer_test.related_to)
        print(transformer_test.fields)
    else:
        print("Transformation failed")

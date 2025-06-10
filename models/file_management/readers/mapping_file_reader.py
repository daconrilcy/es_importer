from typing import Optional, Dict, Any, Union

from config import Config
from models.file_management.readers.json_file_reader import JsonFileReader
from models.mapping_management.fields_management import FieldsManager
from models.mapping_management.fields_management.base import BaseMappingField


class MappingFileReader(JsonFileReader):
    """
    Lecteur de fichier JSON de mapping qui instancie les champs en objets MappingField.
    """

    def __init__(self, filepath: str, encoding: str = "utf-8", config: Optional[Config] = None) -> None:
        super().__init__(filepath=filepath, encoding=encoding)
        self._related_to: Optional[str] = None
        self._fields: Dict[str, BaseMappingField] = {}
        self._config: Config = config or Config()
        self._load_mapping()

    def _load_mapping(self) -> None:
        """
        Charge et valide les données JSON, puis instancie les champs.
        """
        data = self.get_all()
        self._related_to = data.get("related_to")

        raw_mapping = data.get("mapping")
        if not isinstance(raw_mapping, dict):
            raise TypeError("Le champ 'mapping' doit être un dictionnaire.")

        self._set_fields(data)

    def _set_fields(self, mapping_data: Dict[str, Union[str, Dict[str, Any]]]) -> None:
        """
        Crée les objets champs à partir du mapping brut.
        """
        manager = FieldsManager(mapping=mapping_data, config=self._config)
        self._fields = manager.fields

    @property
    def related_to(self) -> Optional[str]:
        """
        Objet ou entité auquel ce mapping est lié.
        """
        return self._related_to

    @property
    def fields(self) -> Dict[str, BaseMappingField]:
        """
        Tous les champs de mapping instanciés.
        """
        return self._fields

    def get_field(self, field_name: str) -> Optional[BaseMappingField]:
        """
        Retourne un champ spécifique du mapping par son nom.
        """
        return self._fields.get(field_name)

    def get_mapped_fields(self) -> Dict[str, BaseMappingField]:
        """
        Retourne uniquement les champs marqués comme mappés.
        """
        return {k: v for k, v in self._fields.items() if getattr(v, "mapped", False)}

    def validate_structure(self) -> bool:
        """
        Valide la structure minimale attendue du fichier de mapping.
        """
        if not super().validate_structure():
            return False

        required_keys = {"related_to", "mapping"}
        missing = required_keys - self.get_all().keys()
        if missing:
            print(f"[Validation] Clés manquantes dans le mapping : {missing}")
            return False

        return True


if __name__ == "__main__":
    fp_test = 'C:/dev/py/csv_importer/files/mappings/cf55e856-4745-4f15-b682-6fbdb73ed5e6.json'
    reader = MappingFileReader(filepath=fp_test)
    print(reader.get_mapped_fields())

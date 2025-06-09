from typing import Optional, Dict

from models.file_management.readers.json_file_reader import JsonFileReader
from models.mapping_management import MappingField


class MappingFileReader(JsonFileReader):
    """
    Lit un fichier JSON de mapping et instancie les champs sous forme d'objets MappingField.
    """

    def __init__(self, filepath: str, encoding: str = "utf-8"):
        super().__init__(filepath=filepath, encoding=encoding)
        self._related_to: Optional[str] = None
        self._fields: Dict[str, MappingField] = {}

        self._load_mapping()

    def _load_mapping(self) -> None:
        """
        Charge les données du fichier JSON et initialise les champs internes.
        """
        records = self.get_all()
        if not records:
            raise ValueError(f"Fichier de mapping vide : {self.filepath}")

        self._related_to = records.get("related_to")

        raw_mapping = records.get("mapping")
        if not isinstance(raw_mapping, dict):
            raise TypeError("Le champ 'mapping' doit être un dictionnaire.")

        self._fields = {
            name: MappingField(name=name, data=data)
            for name, data in raw_mapping.items()
            if isinstance(data, dict)
        }

    @property
    def related_to(self) -> Optional[str]:
        """Objet ou entité auquel ce mapping est lié."""
        return self._related_to

    @property
    def fields(self) -> Dict[str, MappingField]:
        """Retourne tous les champs de mapping."""
        return self._fields

    def get_field(self, field_name: str) -> Optional[MappingField]:
        """
        Retourne un champ spécifique du mapping par son nom.
        """
        return self._fields.get(field_name)

    def get_mapped_fields(self) -> Dict[str, MappingField]:
        """
        Retourne uniquement les champs mappés (où 'mapped' est True).
        """
        return {k: v for k, v in self._fields.items() if v.mapped}

    def validate_structure(self) -> bool:
        """
        Valide la structure minimale du fichier de mapping.
        """
        try:
            super().validate_structure()
        except ValueError as e:
            print(f"[Validation] Erreur de structure JSON : {e}")
            return False

        required_keys = {"related_to", "mapping"}
        if not required_keys.issubset(self._data):
            missing = required_keys - self._data.keys()
            print(f"[Validation] Clés manquantes dans le mapping : {missing}")
            return False

        return True


if __name__ == "__main__":
    fp_test = 'C:/dev/py/csv_importer/files/mappings/f0be2831-7f19-4c9c-b665-07c4771552d8.json'
    reader = MappingFileReader(filepath=fp_test)
    print(reader.get_mapped_fields())

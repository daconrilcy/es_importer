import json
from typing import Optional, Dict, Any

from models.file_management.readers.base_file_reader import BaseFileReader


class JsonFileReader(BaseFileReader):
    """
    Lecteur de fichiers JSON, prenant en charge les objets dict et NDJSON.
    """

    def __init__(self, filepath: str, encoding: str = "utf-8"):
        self._data: Optional[Dict[str, Any]] = None
        super().__init__(filepath, encoding)

    def _load_data_if_needed(self) -> Dict[str, Any]:
        """
        Charge les données JSON depuis le fichier si elles ne sont pas déjà chargées.
        """
        if self._data is None:
            try:
                with open(self.filepath, encoding=self.effective_encoding) as file:
                    data = json.load(file)
                    if not isinstance(data, dict):
                        raise ValueError("Le fichier JSON ne contient pas un objet dict à la racine.")
                    self._data = data
            except (OSError, json.JSONDecodeError) as e:
                raise ValueError(f"❌ JsonFileReader: erreur de lecture JSON - {e}")
        return self._data

    def get_all(self, **kwargs) -> Dict[str, Any]:
        """
        Retourne l'intégralité des données JSON chargées.
        """
        return self._load_data_if_needed()

    def read_partial(self, start: int, size: int, **kwargs) -> Dict[str, Any]:
        """
        Non applicable ici : retourne toutes les données (JSON non structuré par lignes).
        """
        return self._load_data_if_needed()

    def validate_structure(self) -> bool:
        """
        Valide que la structure du fichier JSON est un dictionnaire.
        """
        try:
            data = self._load_data_if_needed()
            return isinstance(data, dict)
        except ValueError as e:
            print(f"❌ JsonFileReader.validate_structure: {e}")
            return False


if __name__ == "__main__":
    fp_test = "C:/dev/py/csv_importer/files/mappings/cf55e856-4745-4f15-b682-6fbdb73ed5e6.json"
    reader_test = JsonFileReader(fp_test)
    print(reader_test.get_all())

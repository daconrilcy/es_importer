from pathlib import Path
from typing import List, Optional

import pandas as pd

from config import Config
from models.mapping_management.fields_management.base import BaseMappingField


class ReplacementField(BaseMappingField):
    """
    Gère les champs de remplacement pour les fichiers CSV contenant des correspondances.
    """

    def __init__(self, name: str, data: dict, config: Optional[Config] = None):
        """
        Initialise un champ de remplacement à partir des données et de la configuration.
        """
        config = config or Config()
        super().__init__(name, data, config)

        self._folder: Path = Path(config.files_folder) / "completions"
        self._chunk_size: int = config.chunksize

        self._type_completion: str
        self._original_field: str
        self._column_names: List[str]
        self._keep_original: bool
        self._filename: str
        self._use_first_column: bool

        self._set(data)

    def _set(self, data: dict) -> None:
        """
        Valide et extrait les champs obligatoires à partir des données.
        """
        if data is None:
            return
        self._type_completion = self._require(data, "_type_completion")
        self._original_field = self._require(data, "original_field")
        self._column_names = self._require(data, "column_names")
        self._filename = self._require(data, "filename")

        self._keep_original = data.get("keep_original", False)
        self._use_first_column = data.get("use_first_column", False)

    @staticmethod
    def _require(data: dict, key: str):
        """
        Récupère une valeur obligatoire et lève une erreur si absente.
        """
        value = data.get(key)
        if value is None:
            raise ValueError(f"ReplacementField : Le champ '{key}' est obligatoire.")
        return value

    @property
    def original_field(self) -> str:
        """Champ original à remplacer."""
        return self._original_field

    @property
    def column_names(self) -> List[str]:
        """Colonnes à ajouter après le remplacement."""
        return self._column_names

    @property
    def keep_original(self) -> bool:
        """Indique si le champ original doit être conservé."""
        return self._keep_original

    @property
    def use_first_column(self) -> bool:
        """Indique si la première colonne du fichier doit être utilisée."""
        return self._use_first_column

    @property
    def filename(self) -> str:
        """Nom du fichier contenant les correspondances."""
        return self._filename

    def load_all_values(self) -> pd.DataFrame:
        """
        Charge l'ensemble des correspondances depuis le fichier CSV.
        """
        return pd.read_csv(self._folder / self._filename)

    def get_chunk_values(self, chunk_index: int = 0, exclude_first_column: bool = False) -> pd.DataFrame:
        """
        Charge un chunk de données depuis le fichier CSV.
        """
        skiprows = chunk_index * self._chunk_size
        df_iter = pd.read_csv(
            self._folder / self._filename,
            skiprows=skiprows,
            chunksize=self._chunk_size,
            header=None
        )

        chunk = next(df_iter)
        if exclude_first_column:
            chunk = chunk.iloc[:, 1:]
        return chunk

    @property
    def type_completion(self) -> str:
        return self._type_completion

    @property
    def dict(self) -> dict:
        data = super().dict
        data["category"] = self.category
        data["type_completion"] = self.type_completion
        data["original_field"] = self.original_field
        data["column_names"] = self.column_names
        data["keep_original"] = self.keep_original
        data["use_first_column"] = self.use_first_column
        data["filename"] = self.filename

        return data

    def __repr__(self):
        return (f"<MappingField name={self._name}, category={self._category}, description={self._description}, "
                f"type_completion={self._type_completion}, original_field={self._original_field}, "
                f"column_names={self._column_names}, keep_original={self._keep_original}, "
                f"use_first_column={self._use_first_column}, filename={self._filename}>")
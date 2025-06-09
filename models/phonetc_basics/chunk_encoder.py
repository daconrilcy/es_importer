from typing import List, Union, Any, Dict, Callable
import pandas as pd

from config import Config
from ext_lib.phonetic import PhoneticWrapper


class PhoneticChunkEncoder:
    """
    Encode des données textuelles en phonétique selon différents algorithmes.
    """

    def __init__(
            self,
            phonex_dict: dict,
            source_column: str,
            config: Config = None,
            include_source_column: bool = False,
    ) -> None:
        """
        Args:
            phonex_dict: Dictionnaire d'activation des algorithmes (soundex, metaphone, metaphone3).
            source_column: Nom de la colonne source à encoder.
            config: Instance optionnelle de Config.
            include_source_column: Si True, inclut la colonne source dans le résultat.
        """
        self._processor = PhoneticWrapper(config or Config())
        self._phonex_dict = phonex_dict
        self._source_column = source_column
        self._include_source_column = include_source_column

    def encode(self, chunk: Union[List[Any], pd.Series]) -> pd.DataFrame:
        """
        Encode un chunk de texte avec les algorithmes phonétiques spécifiés.

        Args:
            chunk: Liste ou Série Pandas de chaînes à encoder.

        Returns:
            DataFrame contenant les colonnes encodées.
        """
        clean_chunk = self._prepare_input(chunk)
        dfs: List[pd.DataFrame] = []

        if self._include_source_column:
            source_df = pd.DataFrame({self._source_column: clean_chunk})
            dfs.append(source_df)

        encoders: Dict[str, Callable[[List[str]], pd.DataFrame]] = {
            "soundex": self._encode_soundex,
            "metaphone": self._encode_metaphone,
            "metaphone3": self._encode_metaphone3,
        }

        for algo, encoder in encoders.items():
            if self._phonex_dict.get(algo):
                dfs.append(encoder(clean_chunk))

        if not dfs:
            raise ValueError("Aucun algorithme activé dans phonex_dict et source non demandée.")

        return pd.concat(dfs, axis=1)

    @property
    def new_column_names(self) -> List[str]:
        """
        Retourne les noms des colonnes générées selon les algorithmes activés.
        """
        names = []
        if self._phonex_dict.get("soundex"):
            names.append(f"{self._source_column}_soundex")
        if self._phonex_dict.get("metaphone"):
            names.append(f"{self._source_column}_metaphone")
        if self._phonex_dict.get("metaphone3"):
            names += [
                f"{self._source_column}_metaphone3_primary",
                f"{self._source_column}_metaphone3_secondary"
            ]
        return names

    @staticmethod
    def _prepare_input(series: Union[pd.Series, List[Any]]) -> List[str]:
        """
        Nettoie et convertit l'entrée en liste de chaînes.
        """
        if series is None:
            return []
        if isinstance(series, list):
            series = pd.Series(series)
        return series.fillna("").astype(str).str.strip().tolist()

    def _encode_soundex(self, clean_chunk: List[str]) -> pd.DataFrame:
        """
        Encode avec Soundex.
        """
        values = self._processor.phonex_encode(clean_chunk)
        return pd.DataFrame({f"{self._source_column}_soundex": values})

    def _encode_metaphone(self, clean_chunk: List[str]) -> pd.DataFrame:
        """
        Encode avec Metaphone.
        """
        values = self._processor.metaphone_encode(clean_chunk)
        return pd.DataFrame({f"{self._source_column}_metaphone": values})

    def _encode_metaphone3(self, clean_chunk: List[str]) -> pd.DataFrame:
        """
        Encode avec Metaphone3 en séparant primary/secondary.
        """
        encoded = self._processor.metaphone3_encode(clean_chunk)
        primaries, secondaries = zip(*encoded) if encoded else ([], [])
        return pd.DataFrame({
            f"{self._source_column}_metaphone3_primary": primaries,
            f"{self._source_column}_metaphone3_secondary": secondaries
        })


if __name__ == "__main__":
    encoder_test = PhoneticChunkEncoder(phonex_dict={"soundex": True, "metaphone": True, "metaphone3": True},
                                        source_column="text")
    print(encoder_test.encode(["Hello", "World"]))

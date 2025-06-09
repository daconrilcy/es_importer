import logging
from pathlib import Path
from typing import Optional, Tuple, Union, List, Any
import pandas as pd

from models.file_type import FileType
from models.file_management.save_management.file_save_strategy import (
    DataFrameLocalSaveStrategy, BaseLocalSaveStrategy,
)
from models.file_management.file_utls import FileUtils
from models.file_management.save_management.file_validator import CsvFileValidator

logger = logging.getLogger(__name__)


class CsvFileSaver:
    """
    Gère la sauvegarde de données tabulaires (DataFrame ou liste de listes) en fichier CSV,
    avec validation du fichier et de son extension.
    Pas d'extension checker pour cette classe car géré dans FileValidator
    """

    def __init__(self, save_strategy: Optional[BaseLocalSaveStrategy] = None,
                 ) -> None:
        """
        Initialise le CSVFileSaver avec une stratégie de sauvegarde facultative.

        Args:
            save_strategy: Stratégie de sauvegarde à utiliser (injectée), ou None pour la stratégie par défaut.
        """
        self.save_strategy = save_strategy
        self.file_utils = FileUtils()
        self.validator = CsvFileValidator()

    def save(
            self,
            data: Union[pd.DataFrame, List[List[Any]]],
            filename: Optional[str] = None,
            filetype: Optional[FileType] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Sauvegarde les données au format CSV après validation du type et de l'extension.

        Args:
            data: Données à sauvegarder.
            filename: Nom du fichier
            filetype: Métadonnées de type de fichier pour déterminer le dossier et extensions valides.

        Returns:
            Tuple (succès, nom de fichier, chemin complet)
        """
        if not isinstance(data, (pd.DataFrame, list)):
            logger.error("Données non valides : doivent être un DataFrame ou list[list]")
            return False, None, None

        try:
            filename = filename or self.file_utils.generate_filename(".csv")
            df = self._normalize_to_dataframe(data)

            if not self.validator.is_valid(df, filename):
                logger.error("Fichier non valide selon les critères du validateur")
                return False, None, None

            strategy = self._get_strategy(filetype)
            saved_path = strategy.save(df, filename)
            return True, filename, saved_path
        except Exception as err:
            logger.error("Erreur lors de la sauvegarde CSV : %s", err)
            return False, None, None

    @staticmethod
    def _normalize_to_dataframe(
            data: Union[pd.DataFrame, List[List[Any]]]
    ) -> pd.DataFrame:
        """
        Transforme les données brutes en DataFrame si nécessaire.

        Args:
            data: Données à convertir.

        Returns:
            Un DataFrame prêt à être sauvegardé.
        """
        return data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)

    def _get_strategy(self, filetype: FileType) -> BaseLocalSaveStrategy:
        """
        Détermine la stratégie de sauvegarde à utiliser.

        Args:
            filetype: Type de fichier contenant les informations de chemin.

        Returns:
            Une stratégie de sauvegarde conforme à AbstractFileSaveStrategy.
        """

        return self.save_strategy or DataFrameLocalSaveStrategy(filetype.folder_path)

    def append(
            self,
            data: Union[pd.DataFrame, List[List[Any]]],
            filename: str,
            filetype: Optional[FileType] = None, first_append: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Ajoute des données à un fichier CSV existant après validation.

        Args:
            data: Données à ajouter (DataFrame ou list[list]).
            filename: Nom du fichier existant.
            filetype: Métadonnées de type de fichier (utile pour le chemin).
            first_append: Indique si c'est la premiere fois qu'on ajoute des données
        Returns:
            Tuple (succès, nom de fichier, chemin complet)
        """
        if not isinstance(data, (pd.DataFrame, list)):
            logger.error("Données non valides : doivent être un DataFrame ou list[list]")
            return False, None, None

        try:
            df = self._normalize_to_dataframe(data)

            if not self.validator.is_valid(df, filename):
                logger.error("Données invalides selon CsvFileValidator")
                return False, None, None

            strategy = self._get_strategy(filetype)
            path = Path(strategy.folder_path) / filename

            if not path.exists():
                logger.error("Le fichier cible n'existe pas : impossible d'ajouter")
                return False, None, None

            df.to_csv(path, mode='a', header=first_append, index=False)
            return True, filename, str(path)
        except Exception as err:
            logger.error("Erreur lors de l'ajout au fichier CSV : %s", err)
            return False, None, None

if __name__=="__main__":
    from config import Config

    df_initial = pd.DataFrame({
        "Nom": ["Alice", "Bob"],
        "Age": [30, 25]
    })

    df_append = pd.DataFrame({
        "Nom": ["Charlie", "Diana"],
        "Age": [40, 35]
    })
    config_test_folder = Config().temp_folder
    csv_fs_test = CsvFileSaver(DataFrameLocalSaveStrategy(config_test_folder))
    result, filename_test, filepath_test = csv_fs_test.save(df_initial)
    csv_fs_test.append(df_append, filename_test)
import logging
from pathlib import Path
from typing import Optional, Tuple

from werkzeug.datastructures import FileStorage

from models.file_type import FileType
from models.file_management.save_management.extention_checker import FileTypeExtensionChecker
from models.file_management.save_management.file_save_strategy import (
    FileSaveStrategy,
    UploadedLocalFileSaveStrategy,
)
from models.file_management.save_management.file_validator import FileValidator, FileTypeValidator
from models.file_management.file_utls import FileUtils

logger = logging.getLogger(__name__)


class UploadedFileSaver:
    """
    Gère la validation et la sauvegarde d'un fichier selon une stratégie fournie.

    Attributs:
        save_strategy (Optional[AbstractFileSaveStrategy]): Stratégie de sauvegarde à utiliser.
        validator (FileValidator): Validateur de fichier.
        checker (FileTypeExtensionChecker): Contrôleur d'extension.
    """

    def __init__(
            self,
            save_strategy: Optional[FileSaveStrategy] = None,
            validator: Optional[FileTypeValidator] = None,
            checker: Optional[FileTypeExtensionChecker] = None,
    ) -> None:
        self.save_strategy: Optional[FileSaveStrategy] = save_strategy
        self.validator: FileTypeValidator = validator or FileValidator()
        self.checker: FileTypeExtensionChecker = checker or FileTypeExtensionChecker()
        self.utils: FileUtils = FileUtils()

    def save(
            self, file: FileStorage, filetype: FileType, original_filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Valide et sauvegarde le fichier.

        Args:
            file (FileStorage): Fichier téléchargé.
            filetype (FileType): Type de fichier attendu.
            original_filename (str): Nom initial du fichier.

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (succès, nom du fichier généré, chemin de sauvegarde).
        """
        if not self.validator.is_valid(file, filetype, original_filename):
            return False, None, None

        extension = Path(original_filename).suffix
        if not self.checker.is_allowed(extension, filetype):
            return False, None, None

        new_filename = self.utils.generate_filename(extension)

        try:
            strategy = self._get_strategy(filetype)
            saved_path = strategy.save(file, new_filename)
            return True, new_filename, saved_path
        except OSError as err:
            logger.error("Erreur lors de la sauvegarde : %s", err)
            return False, None, None

    def _get_strategy(self, filetype: FileType) -> FileSaveStrategy:
        """
        Retourne la stratégie de sauvegarde à utiliser.

        Args:
            filetype (FileType): Type de fichier.

        Returns:
            AbstractFileSaveStrategy: Stratégie de sauvegarde.
        """
        if self.save_strategy:
            return self.save_strategy
        return UploadedLocalFileSaveStrategy(filetype.folder_path)

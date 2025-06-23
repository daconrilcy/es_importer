from typing import Collection
from models.file_type import FileType


class ExtensionChecker:
    """
    Vérifie si une extension donnée est parmi une liste d'extensions autorisées.
    """

    @staticmethod
    def _normalize_extension(extension: str) -> str:
        """
        Nettoie une extension de fichier en supprimant le point initial et en la convertissant en minuscule.

        :param extension: L'extension de fichier à normaliser.
        :return: L'extension normalisée.
        """
        return extension.lower().lstrip('.')

    def is_allowed(self, extension: str, desired_extensions: Collection[str]) -> bool:
        """
        Vérifie si l'extension est présente dans la collection des extensions autorisées.

        :param extension: L'extension à vérifier.
        :param desired_extensions: Une collection d'extensions autorisées.
        :return: True si l'extension est autorisée, False sinon.
        """
        normalized_extension = self._normalize_extension(extension)
        allowed_set = {self._normalize_extension(ext) for ext in desired_extensions}
        return normalized_extension in allowed_set


class FileTypeExtensionChecker(ExtensionChecker):
    """
    Vérifie si une extension est autorisée selon un type de fichier.
    """

    def is_allowed(self, extension: str, file_type: FileType) -> bool:
        """
        Vérifie si l'extension est acceptée pour un type de fichier donné.

        :param extension: L'extension à vérifier.
        :param file_type: L'objet FileType contenant les extensions autorisées.
        :return: True si autorisée, False sinon.
        """
        return super().is_allowed(extension, file_type.accepted_extensions)

class MappingExtensionChecker(ExtensionChecker):
    """
    Vérifie si une extension est autorisée selon un type de fichier.
    """

    def is_allowed(self, extension: str, file_type: FileType) -> bool:
        """
        Vérifie si l'extension est acceptée pour un type de fichier donné.

        :param extension: L'extension à vérifier.
        :param file_type: L'objet FileType contenant les extensions autorisées.
        :return: True si autorisée, False sinon.
        """
        return super().is_allowed(extension, file_type.accepted_extensions)
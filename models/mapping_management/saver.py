from typing import Optional, Tuple, Union
import json
import logging

from config import Config
from models.file_management.file_utls import FileUtils


class MappingSaver:
    """
    Classe responsable de la sauvegarde d'un mapping (dictionnaire) dans un fichier.
    Permet l'injection des dépendances FileUtils et Config pour faciliter les tests et la maintenance.
    """

    def __init__(self, file_utils: Optional[FileUtils] = None, config: Optional[Config] = None) -> None:
        """
        Initialise le MappingSaver avec les dépendances nécessaires.
        Args:
            file_utils (Optional[FileUtils]): Utilitaire pour générer les noms de fichiers.
            config (Optional[Config]): Configuration contenant les chemins de sauvegarde.
        """
        self.file_utils = file_utils or FileUtils()
        self.config = config or Config()

    def save_from_dict(self, mapping_dict: dict, filepath: Optional[str] = None) -> Tuple[Union[str, bool], bool]:
        """
        Sauvegarde un dictionnaire de mapping dans un fichier JSON.
        Args:
            mapping_dict (dict): Le mapping à sauvegarder.
            filepath (Optional[str]): Chemin du fichier cible. S'il n'est pas fourni,
            un nom sera généré automatiquement.
        Returns:
            Optional[str]: Le chemin du fichier sauvegardé, ou None en cas d'échec.
        """
        new_filepath = False
        if filepath is None:
            filename = self.file_utils.generate_filename()
            folder_path = self.config.file_types.mappings.folder_path
            filepath = str(folder_path / filename)
            new_filepath = True

        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(mapping_dict, file, ensure_ascii=False, indent=4)
            return filepath, new_filepath
        except (OSError, TypeError) as e:
            logging.error(f"Erreur lors de la sauvegarde du mapping dans {filepath}: {e}")
            return False, False

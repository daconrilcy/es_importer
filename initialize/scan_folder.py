from pathlib import Path
from typing import List, Tuple, Dict, Union

from models.file_management.file_infos import FileInfos


class ScanFolderTools:
    """
    Outils pour opérer sur des dossiers : lister les fichiers, comparer des listes de fichiers,
    et détecter les fichiers manquants par dossier.
    """

    @staticmethod
    def list_files(folder_path: Union[str, Path]) -> List[Path]:
        """
        Liste les fichiers dans un dossier donné.

        :param folder_path: Chemin du dossier à scanner.
        :return: Liste des fichiers présents dans le dossier.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            return []
        return list(folder.iterdir())

    @staticmethod
    def compare_filepath_list(filepath_a: List[Path], filepath_b: List[Path]) -> Tuple[List[Path], List[Path]]:
        """
        Compare deux listes de fichiers et détecte les différences.

        :param filepath_a: Liste de chemins de fichiers A.
        :param filepath_b: Liste de chemins de fichiers B.
        :return: Tuple (fichiers présents dans B mais pas dans A, et vice versa).
        """
        set_a = set(filepath_a or [])
        set_b = set(filepath_b or [])
        return list(set_b - set_a), list(set_a - set_b)

    @staticmethod
    def get_missing_files_by_folder(file_infos_list: List[FileInfos], folder_paths: List[Union[str, Path]]) -> Dict[
        str, List[Path]]:
        """
        Récupère les fichiers manquants par dossier par rapport à une liste de référence.

        :param file_infos_list: Liste d'objets avec un attribut 'filename'.
        :param folder_paths: Liste des chemins de dossiers à analyser.
        :return: Dictionnaire des fichiers manquants par nom de dossier.
        """
        if not file_infos_list:
            return {}
        if not folder_paths:
            return {}
        if not isinstance(file_infos_list[0], FileInfos):
            raise ValueError("file_infos_list must contain FileInfos objects")
        if not isinstance(folder_paths[0], str) and not isinstance(folder_paths[0], Path):
            raise ValueError("folder_paths must contain strings or Path objects")

        known_filenames = []
        for fi in file_infos_list:
            if not fi.filename:
                raise ValueError("file_infos_list must contain FileInfos with a filename attribute")
            known_filenames.append(fi.filename)

        missing_by_folder: Dict[str, List[Path]] = {}

        for folder_path in folder_paths:
            folder = Path(folder_path)
            if not folder.is_dir():
                continue

            missing = [f for f in folder.iterdir() if f.is_file() and f.name not in known_filenames]
            if missing:
                missing_by_folder[folder.name] = sorted(missing)

        return missing_by_folder

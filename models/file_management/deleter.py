from typing import Optional
import logging
from pathlib import Path

from config import Config
from elastic_manager import ElasticManager
from models.file_management.file_infos import FileInfos

logger = logging.getLogger(__name__)


class FileDeleter:
    """
    Gère la suppression de fichiers dans Elasticsearch,
    et toujours la suppression physique sur le disque associé.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialise le FileDeleter avec une configuration optionnelle.
        :param config: Configuration Elasticsearch (optionnelle)
        """
        self._config: Config = config or Config()
        self._es_manager = ElasticManager(self._config)

    def delete(
            self,
            filename: Optional[str] = None,
            file_id: Optional[str] = None
    ) -> bool:
        """
        Supprime un fichier dans Elasticsearch (par id ou nom),
        puis tente toujours la suppression physique sur le disque :
        - D’abord via FileInfos si dispo,
        - Sinon, essaie de reconstituer le chemin si type connu,
        - Sinon, scanne tous les sous-dossiers du dossier racine.

        :param filename: Nom du fichier à supprimer
        :param file_id: Identifiant du fichier à supprimer
        :return: True si suppression physique (et ES si dispo), False sinon
        """
        if not filename and not file_id:
            logger.error("Aucun filename ou id de fichier fourni pour la suppression.")
            return False

        file_infos = self._get_file_infos(filename, file_id)

        # 1. Suppression ES si trouvé
        if file_infos:
            logger.info(f"Suppression du fichier ES : {getattr(file_infos, 'filename', file_id)} (ID: {file_infos.id})")
            try:
                self._es_manager.files_obj.delete(file_infos)
            except Exception as e:
                logger.error(f"Erreur suppression ES : {e}")

            # 2. Tentative suppression physique par FileInfos
            return self._delete_by_fileinfos(file_infos, filename)

        # 3. Si non trouvé dans ES, on tente le scan de tout le dossier de fichiers
        if filename:
            logger.warning("Fichier non trouvé en base ES, tentative de suppression physique par scan global.")
            return self._scan_and_delete_in_folders(filename)

        logger.error("Impossible de trouver le fichier à supprimer (ni ES ni physique).")
        return False

    def _get_file_infos(self, filename: Optional[str], file_id: Optional[str]) -> Optional[FileInfos]:
        """
        Récupère l'objet FileInfos correspondant à l'ID ou au nom de fichier.
        :param filename: Nom du fichier
        :param file_id: ID du fichier
        :return: Instance FileInfos ou None si non trouvé
        """
        if file_id:
            file_infos = self._es_manager.files_obj.get_one(file_id)
            if not file_infos:
                logger.error(f"Aucun fichier trouvé avec l'ID : {file_id}")
            return file_infos
        elif filename:
            file_infos = self._es_manager.files_obj.get_by_filename(filename)
            if not file_infos:
                logger.error(f"Aucun fichier trouvé avec le nom : {filename}")
            return file_infos
        return None

    def _delete_by_fileinfos(self, file_infos: FileInfos, filename: Optional[str]) -> bool:
        """
        Supprime physiquement un fichier à partir d'un FileInfos.
        Essaie d'abord filepath, sinon reconstruit avec le type, sinon échoue.

        :param file_infos: Instance FileInfos
        :param filename: Nom du fichier (fallback)
        :return: True si supprimé, False sinon
        """
        filepath = file_infos.filepath
        if not filepath and file_infos.type and filename:
            # On reconstruit le chemin si possible
            folder_path = file_infos.type.folder_path
            if folder_path:
                filepath = str(Path(folder_path) / filename)
                logger.info(f"Chemin reconstitué : {filepath}")

        return self._delete_physical_file_pathlib(filepath)

    @staticmethod
    def _delete_physical_file_pathlib(filepath: Optional[str]) -> bool:
        """
        Supprime physiquement le fichier sur disque (Pathlib).
        :param filepath: Chemin absolu du fichier
        :return: True si supprimé, False sinon
        """
        if not filepath:
            logger.error("Chemin de fichier introuvable pour suppression physique.")
            return False
        file_path = Path(filepath)
        if not file_path.is_file():
            logger.warning(f"Fichier déjà absent ou introuvable : {file_path}")
            return False
        try:
            file_path.unlink()
            logger.info(f"Fichier supprimé physiquement : {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression physique du fichier {file_path} : {e}")
            return False

    def _scan_and_delete_in_folders(self, filename: str) -> bool:
        """
        Parcourt tous les sous-dossiers de self._config.files_folder pour chercher et supprimer un fichier.
        :param filename: Nom du fichier à supprimer
        :return: True si fichier trouvé et supprimé, False sinon
        """
        base_folder = Path(self._config.files_folder)
        found = False
        logger.info(f"Recherche physique de {filename} dans tous les sous-dossiers de {base_folder}")
        for file_path in base_folder.rglob(filename):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    logger.info(f"Fichier supprimé physiquement : {file_path}")
                    found = True
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {file_path} : {e}")
        if not found:
            logger.warning(f"Fichier {filename} non trouvé dans {base_folder} (ni dans aucun sous-dossier).")
        return found

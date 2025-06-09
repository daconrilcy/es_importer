import csv
import uuid
from pathlib import Path
from typing import Optional, List


class FileUtils:
    """
    Classe utilitaire pour la manipulation de fichiers.
    Actuellement focalisée sur le traitement des fichiers CSV.
    """

    @staticmethod
    def detect_separator(
            filepath: str,
            default_separator: str = ",",
            encoding="utf-8",
            candidates: Optional[list[str]] = None
    ) -> str:
        """
        Détecte automatiquement le séparateur dans un fichier CSV.
        Utilise le module "csv. Sniffer". Si cela échoue, utilise le séparateur le plus fréquent.

        :param filepath: Chemin vers le fichier.
        :param default_separator: Séparateur utilisé en cas d’échec de détection.
        :param encoding: Encoder à utiliser
        :param candidates: Liste de séparateurs à tester.
        :return: Le séparateur détecté.
        :raises RuntimeError: Si le fichier ne peut être lu.
        :raises ValueError: Si le fichier n’a pas une extension supportée.
        """
        if candidates is None:
            candidates = [';', ',', '\t', '|']

        filepath = FileUtils.normalize_filepath(filepath)

        if Path(filepath).suffix.lower() not in {".csv", ".txt", ".dat"}:
            raise ValueError("Extension de fichier non supportée pour détection de séparateur.")

        try:
            with open(filepath, encoding=encoding) as f:
                sample = f.read(4096)
        except (FileNotFoundError, OSError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Impossible de lire le fichier : {e}") from e

        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="".join(candidates))
            return dialect.delimiter
        except csv.Error:
            counts = {sep: sample.count(sep) for sep in candidates}
            return max(counts, key=counts.get, default=default_separator)

    @staticmethod
    def normalize_filepath(filepath: str) -> str:
        """
        Normalise un chemin de fichier pour le rendre compatible tous OS (résout les chemins relatifs, ~, etc.).

        :param filepath: Chemin brut.
        :return: Chemin absolu normalisé.
        """
        return str(Path(filepath).expanduser().resolve())

    @staticmethod
    def manage_filepath(folder: str, filename: str, ext=".csv") -> str | None:
        """
        Gère le chemin d'accès à un fichier.
        :param folder: Dossier contenant le fichier.
        :param filename: Nom du fichier (sans extension ou avec).
        :param ext: Extension par défaut à ajouter si manquante.
        :return: Chemin complet vers le fichier ou None si problème.
        """
        if ext[0] != ".":
            ext = "." + ext
        filename_wo_ext = Path(filename.lower()).stem
        filename = filename_wo_ext + ext

        folder = Path(folder).resolve()  # nettoie le chemin

        if not folder.is_dir():
            print(f"utils - Dossier {folder} introuvable.")
            return None

        filepath = folder / filename

        if not Path(filepath).is_file():
            raise ValueError(f"{filepath} n'est pas un fichier connu")

        return filepath

    @staticmethod
    def generate_filename(ext: Optional[str] = ".json") -> str:
        """
        Génère un nom de fichier unique avec une extension donnée.

        :param ext: Extension du fichier, par défaut ".json".
        :return: Nom de fichier unique avec l'extension donnée.
        """
        if not ext.startswith("."):
            ext = f".{ext}"
        return f"{uuid.uuid4()}{ext}"

    @staticmethod
    def validate_filepath(filepath: str, expected_extentions: Optional[List[str]] = None) -> bool:
        if filepath is None or filepath == "":
            return False
        filepath = Path(filepath)
        if not filepath.is_file():
            return False
        if expected_extentions is None:
            return True

        file_extention = filepath.suffix
        if file_extention not in expected_extentions:
            return False
        return True

    def build_filepath(*parts: str) -> Path:
        """
        Construit un chemin de fichier compatible avec tous les OS à partir d'éléments séparés.

        Exemple :
            build_filepath("dossier", "sous-dossier", "fichier.txt")
            => Path('dossier/sous-dossier/fichier.txt') (ou backslashes sous Windows)
        """
        return Path(*parts).resolve()


if __name__ == "__main__":
    fu_test = FileUtils()
    fp_test = "C:/dev/py/csv_importer/files/datas/curiexplore-pays.csv"
    print(fu_test.validate_filepath(fp_test))
    print(fu_test.validate_filepath(fp_test, [".csv", ".txt"]))
    print(fu_test.validate_filepath(fp_test, [".json"]))


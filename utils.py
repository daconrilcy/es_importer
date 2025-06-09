"""
    Utility functions for the project
"""
import json
import os
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Any
import platform
from pathlib import Path

import pandas as pd


def manage_folder_name(folder_name: str, lowered=True) -> str:
    """
        Rename folder name to remove special characters and spaces and add a trailing slash if not present
        :param folder_name: str
        :param lowered: bool
        :return: new folder name: str
        """
    folder_name = sanitaze_string(folder_name, lowered)
    if folder_name[-1] != "/":
        folder_name += "/"
    return folder_name


def is_file_in_folder(filename, folder_path):
    """
    Check if a file is in a folder.
    :param filename: Name of the file.
    :param folder_path: Path to the folder.
    :return: True if the file is in the folder, False otherwise.
    """
    # Construire le chemin complet
    full_path = os.path.join(folder_path, filename)
    # Vérifier si c'est un fichier valide
    return os.path.exists(full_path)


def safe_load_csv(file_path: str, sep: str = ',', header: bool = True) \
        -> pd.DataFrame or None:
    """
    Load a CSV file safely.
    :param file_path: Path to the CSV file.
    :param sep: Separator of the CSV file.
    :param header: True if the file has a header, False otherwise.
    :return: DataFrame or None.
    """
    if not file_path:
        print("utils - Le chemin du fichier est vide.")
        return None
    if not os.path.exists(file_path):
        print(f"utils - Le fichier {file_path} n'existe pas.")
        return None
    try:
        if header:
            return pd.read_csv(file_path, sep=sep).replace({pd.NA: None, pd.NaT: None, float('nan'): None})
        else:
            return pd.read_csv(file_path, sep=sep, header=None).replace({pd.NA: None, pd.NaT: None, float('nan'): None})
    except Exception as e:
        print(f"utils - Erreur lors de la lecture du fichier : {e}")
        return None


def file_name_extension(file_name: str) -> str:
    """
    Get the extension of a file.
    :param file_name: Name of the file.
    :return: Extension of the file.
    """
    return os.path.splitext(file_name)[1]


def filename_without_extension(file_name: str) -> str:
    """
    Get the filename without the extension.
    :param file_name: Name of the file.
    :return: Filename without the extension.
    """
    if file_name_extension(file_name) is not None:
        return os.path.splitext(file_name)[0]
    return file_name


def filename_manager(file_name: str, ext: str = ".csv") -> str:
    """
    Manage the filename with the extension.
    :param file_name: Name of the file.
    :param ext: Extension of the file.
    :return: Filename with the extension.
    """
    name_wo_ext = filename_without_extension(file_name)
    proper_filename = sanitaze_string(name_wo_ext)
    return f"{proper_filename}{ext}"


def sanitaze_string(string: str, lowered=True) -> str:
    """
    Remove special characters from a string.
    :param string: String to sanitize.
    :param lowered: True if the string should be lowered, False otherwise.
    :return: Sanitized string
    """
    if string is None:
        print("utils - sanitize : String is None.")
        return ""
    result = "".join([c for c in string if c.isalnum() or c in ['.', '_', '-']])
    if lowered:
        return result.lower()
    return result


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

    proper_filename = filename_manager(filename, ext)
    folder = os.path.abspath(folder)  # clean le chemin du dossier

    if not os.path.isdir(folder):
        print(f"utils - Dossier {folder} introuvable.")
        return None

    filepath = os.path.join(folder, proper_filename)
    if not os.path.isfile(filepath):
        print(f"utils - Fichier {proper_filename} introuvable dans {folder} avec le path {filepath}.")
        return None

    return filepath


def get_csv_headers(file_path, sep=";") -> list[str]:
    """
    Get the headers of a CSV file.
    :param file_path:
    :param sep: Separator of the CSV file.
    :return:
    """
    df = pd.read_csv(file_path, nrows=0, sep=sep)
    return df.columns.tolist()


def clean_pd_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a DataFrame to replace NA, NaT and float('nan') by None.
    For json serialization.
    :param df: DataFrame to clean.
    :return: Cleaned DataFrame.
    """
    return df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})


def list_of_file_in_folder(folder_path: str, fullpath: bool = True) -> list:
    """
    List all files in a folder.
    :param folder_path: Folder path.
    :param fullpath: If True, return the full path of the files.
    :return: List of files.
    """
    if folder_path is None:
        print("❌ utils - Folder path is None.")
        return []
    if not os.path.exists(folder_path):
        print(f"❌ utils - Folder {folder_path} does not exist.")
        return []
    files = os.listdir(folder_path)
    if fullpath:
        return [os.path.join(folder_path, f) for f in files]
    return files


def is_json(val) -> bool:
    """
    Check if a string is a valid JSON object.
    :param val:
    :return:
    """
    try:
        if not isinstance(val, str) and not isinstance(val, bytes) and not isinstance(val, bytearray):
            return False
        obj = json.loads(val)
        return isinstance(obj, dict)
    except ValueError:
        return False


def is_boolean_column(series: pd.Series) -> bool:
    """
    Check if a column contains boolean values.
    :param series:
    :return:
    """

    vals = series.dropna().unique()
    bool_like = {"TRUE", "FALSE", "True", "False", "true", "false", True, False}
    return all(val in bool_like for val in vals)


def is_float_list(val) -> bool:
    """
    Check if a string is a list of floats.
    :param val:
    :return:
    """
    try:
        [float(x.strip()) for x in val.split(',')]
        return True
    except ValueError:
        return False


def is_list_column(series) -> bool:
    """
    Vérifie si une colonne contient des listes de floats (séparées par des virgules).
    :param series:
    :return:
    """
    try:
        sample = series.dropna().iloc[0]
        if not isinstance(sample, str) or ',' not in sample:
            return False
        return all(is_float_list(str(x)) for x in series.dropna())
    except (IndexError, TypeError):
        return False


def is_geo_shape(val) -> bool:
    """
    Check if a string is a valid GeoJSON shape (Polygon or MultiPolygon).
    :param val:
    :return:
    """
    try:
        obj = json.loads(val) if isinstance(val, str) else val
        return (isinstance(obj, dict) and "type" in obj and "coordinates" in obj and obj["type"]
                in ["Polygon", "MultiPolygon"])
    except (ValueError, TypeError, json.JSONDecodeError):
        return False


def infer_es_type_from_values(series: pd.DataFrame) -> str:
    """
    Infer the Elasticsearch type from the values of a column.
    :param series:
    :return:
    """

    clean_series = series.dropna()

    if clean_series.empty:
        return "text"  # Type par défaut en cas d'absence de valeur

    sample = series.dropna().iloc[0]

    # Geo shape ?
    if is_geo_shape(sample):
        return "geo_shape"

    if is_json(sample):
        return "object"

    if is_boolean_column(series):
        return "boolean"

    if is_list_column(series):
        return "list"

    try:
        float(sample)
        return "double"
    except ValueError:
        pass

    try:
        pd.to_datetime(sample)
        return "date"
    except (ValueError, TypeError):
        pass

    if series.nunique() < 50 and series.dtype == object:
        return "keyword"

    return "text"


def infer_elasticsearch_mapping_from_csv(file_path, sep='\\t'):
    """
    Infer the Elasticsearch mapping from a CSV file.
    :param file_path:
    :param sep:
    :return:
    """
    df = pd.read_csv(file_path, sep=sep, dtype=str)
    pre_mapping = {}

    for col in df.columns:
        es_type = infer_es_type_from_values(df[col])
        pre_mapping[col] = {"type": es_type}
    return pre_mapping


def preview_csv(filepath: str, sep: str = ',') -> str or bool:
    """
    Preview the csv file and return the first and last three rows.
    """
    if not filepath or not os.path.exists(filepath):
        print(f"❌ utils - Preview_csv : Le fichier {filepath} n'existe pas.")
        return False

    alternate_sep = [',', ';', '|', '\t']
    if sep is None:
        sep = ','
    df = None
    tried_separators = [sep] + [s for s in alternate_sep if s != sep]

    for current_sep in tried_separators:
        try:
            df = pd.read_csv(filepath, sep=current_sep)
            sep = current_sep  # met à jour le séparateur utilisé
            break
        except Exception as e:
            print(f"❌ utils - Preview_csv : Erreur avec séparateur '{current_sep}' : {e}")
            df = None

    if df is None:
        return False

    df_clean = clean_pd_dataframe(df)

    headers = ["index"] + df_clean.columns.tolist()
    first_three_rows = df_clean.head(3).reset_index().to_dict(orient="records")
    if len(df_clean) > 3:
        last_rows_len = len(df_clean) - 3
        if last_rows_len > 3:
            last_rows_len = 3
        last_three_rows = df_clean.tail(last_rows_len).reset_index().to_dict(orient="records")
    else:
        last_three_rows = []

    return {
        "sep": sep,
        "headers": headers,
        "first_three_rows": first_three_rows,
        "last_three_rows": last_three_rows
    }


def get_dict_from_json(filepath: str) -> dict[Any, Any] | Any:
    """
    Load a JSON file and return its content as a dictionary.
    :param filepath: Path to the JSON file.
    :return: Dictionary with the content of the JSON file.
    """
    if not os.path.isfile(filepath):
        print(f"❌ utils - get_dict_from_json - Le fichier {filepath} n'existe pas.")
        return {}

    with open(filepath, encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ utils - get_dict_from_json - Erreur lors du chargement du fichier JSON : {e}")
            return {}


def get_folder_name_from_filepath(filepath: str) -> str:
    """
    Get the folder path from a file path.
    :param filepath: Path to the file.
    :return: Folder path.
    """
    if not os.path.isfile(filepath):
        print(f"❌ utils - get_folder_from_filepath - Le fichier {filepath} n'existe pas.")
        return ""
    file_path = pathlib.Path(filepath)
    folder_path = file_path.parent.name
    return folder_path

def get_folder_name_by_folder_path(folder_path: str) -> str | None:
    """
    Get the folder name from a folder path.
    :param folder_path: Path to the folder.
    :return: Folder name.
    """
    if not os.path.isdir(folder_path):
        print(f"❌ utils - get_folder_name_by_folder_path - Le dossier {folder_path} n'existe pas.")
        return None
    folder_path = pathlib.Path(folder_path)
    folder_name = folder_path.name
    return folder_name

def get_folder_path_from_filepath(filepath: str) -> str:
    """
    Get the folder path from a file path.
    :param filepath: Path to the file.
    :return: Folder path.
    """
    if not os.path.isfile(filepath):
        print(f"❌ utils - get_folder_from_filepath - Le fichier {filepath} n'existe pas.")
        return ""
    file_path = pathlib.Path(filepath)
    folder_path = file_path.parent
    return folder_path


def generate_filename(ext=".json"):
    """
    Generate a filename with the current date and time.
    :param ext: Extension of the file.
    :return: Filename with the current date and time.
    """
    if ext[0] != ".":
        ext = "." + ext
    return f"{uuid.uuid4()}{ext}"


# Dateime functions

def set_datetime_in_str(date_to_set: datetime | str | None = None) -> str:
    """
    Convertit une date en chaîne de caractères au format ISO.
    :param date_to_set: Date à convertir
    :return: Date au format ISO
    """
    if date_to_set is None:
        date_to_set = datetime.now(timezone.utc)
    if isinstance(date_to_set, datetime):
        date_to_set = date_to_set.strftime("%Y-%m-%dT%H:%M:%SZ")

    return _str_date_to_es_datetime(date_to_set)


def _str_date_to_es_datetime(date_str: str) -> str | None:
    """
    Convertit une date string en format Elasticsearch (%Y-%m-%dT%H:%M:%SZ)
    :param date_str: chaîne de date à parser
    :return: chaîne formatée ou None si invalide
    """
    if not isinstance(date_str, str):
        return None

    try:
        # Cas exact attendu
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    # Cas ISO 8601 Python (ex: 2025-02-16T23:27:31+00:00)
    try:
        dt = datetime.fromisoformat(date_str)
        dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    # Cas commun sans timezone
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    # Dernier recours : timestamp numérique ?
    try:
        timestamp = float(date_str)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        pass

    print(f"❌ Date invalide : {date_str}")
    return None


def get_creation_date(path: str | Path) -> float:
    """
    Retourne la date de création (timestamp float) d'un fichier.
    Utilise ctime sous Windows, et birthtime si dispo (Mac), sinon fallback à ctime.
    """
    path = Path(path)
    stat = path.stat()

    if platform.system() == 'Windows':
        return stat.st_ctime
    elif hasattr(stat, 'st_birthtime'):  # macOS
        return stat.st_birthtime
    else:
        # Linux fallback — pas la vraie création
        return stat.st_ctime


def normalize_filepath(filepath: str) -> str:
    """
    Normalise un chemin de fichier pour qu'il soit compatible avec tous les OS (Windows, Linux, Mac).
    Retourne une chaîne de caractères utilisable par open(), pandas, etc.
    """
    return str(Path(filepath).expanduser().resolve())


# Exemple d'utilisation
if __name__ == "__main__":
    mapping = infer_elasticsearch_mapping_from_csv("C:/dev/py/csv_importer/files/datas/curiexplore-pays.csv", sep=';')
    print(json.dumps(mapping, indent=2, ensure_ascii=False))
    print(preview_csv("C:/dev/py/csv_importer/files/datas/curiexplore-pays.csv", ';'))

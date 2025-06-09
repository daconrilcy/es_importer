import base64
import hashlib
import binascii
from pathlib import Path
from typing import ClassVar

from config import Config


class FilePathCodec:
    """
    Utilitaire pour encoder et décoder les chemins de fichiers
    avec un salt (base64 + hash).
    """
    _salt: ClassVar[str] = Config().filepath_salt
    _salt_hash: ClassVar[bytes] = hashlib.sha256(_salt.encode()).digest()

    @classmethod
    def encode(cls, filepath: str) -> str:
        """
        Encode un chemin de fichier en base64 avec un hash du salt.

        :param filepath: Chemin du fichier à encoder.
        :return: Chaîne encodée.
        """
        if isinstance(filepath, Path):
            filepath = str(filepath)
        if not isinstance(filepath, str):
            raise TypeError("Le chemin doit être une chaîne de caractères.")

        to_encode = cls._salt_hash + filepath.encode()
        return base64.urlsafe_b64encode(to_encode).decode('ascii')

    @classmethod
    def decode(cls, encoded_filepath: str) -> str:
        """
        Décode une chaîne encodée contenant un chemin de fichier avec hash salt.

        :param encoded_filepath: Chaîne encodée à décoder.
        :return: Chemin de fichier d'origine.
        """
        if not isinstance(encoded_filepath, str):
            raise TypeError("L'argument doit être une chaîne de caractères.")

        try:
            decoded = base64.urlsafe_b64decode(encoded_filepath.encode('ascii'))
        except (ValueError, binascii.Error):
            raise ValueError("La chaîne encodée est invalide.")

        if not decoded.startswith(cls._salt_hash):
            raise ValueError("Le salt ne correspond pas ou l'encodage est invalide.")

        return decoded[len(cls._salt_hash):].decode()

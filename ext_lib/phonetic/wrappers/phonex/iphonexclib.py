from typing import Protocol


class IPhonexLib(Protocol):
    """
    Interface pour un moteur de phonétisation compatible avec Phonex.
    Permet de fournir différentes implémentations (lib C, mock, etc.).
    """

    def phonex(self, input_str: str, separator: str, length: int) -> str:
        """
        Applique l'algorithme de phonétisation à une chaîne.

        :param input_str: Chaîne d'entrée à traiter.
        :param separator: Séparateur utilisé dans la sortie.
        :param length: Longueur maximale du code phonex.
        :return: Chaîne phonétisée.
        """
        ...

from abc import ABC, abstractmethod
from typing import Any


class CLib(ABC):
    """
    Classe abstraite représentant une interface pour une bibliothèque externe chargée dynamiquement.
    """

    @abstractmethod
    def _load_library(self, lib_path: str) -> Any:
        """
        Méthode abstraite pour charger la bibliothèque à partir du chemin fourni.

        :param lib_path: Chemin vers la bibliothèque dynamique.
        :return: Instance représentant la bibliothèque chargée.
        """
        pass

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Méthode abstraite pour exécuter une opération avec la bibliothèque chargée.

        :param args: Arguments positionnels.
        :param kwargs: Arguments nommés.
        :return: Résultat de l'exécution.
        """
        pass

from abc import ABC, abstractmethod


class AbstractPhoneticStrategy(ABC):
    def __init__(self, lib):
        self._lib = lib

    @abstractmethod
    def process(self, *args) -> str:
        """
        Applique une transformation phonétique.

        :param args:
        :return: Chaîne transformée.
        """
        pass

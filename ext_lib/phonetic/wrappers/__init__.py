from typing import Union, List, Protocol

from config import Config
from ext_lib.phonetic.wrappers.metaphone import MetaphoneWrapper
from ext_lib.phonetic.wrappers.metaphone3 import Metaphone3Wrapper
from ext_lib.phonetic.wrappers.phonex import PhonexWrapper


class PhoneticAlgorithm(Protocol):
    """
    Fournit une interface unifiée pour les algorithmes phonétiques :
    Phonex, Metaphone et Metaphone3.
    """

    def run(self, *args) -> Union[str, List[str]]:
        raise NotImplementedError


class PhoneticWrapper:
    """
    Fournit une interface unifiée pour les algorithmes phonétiques :
    Phonex, Metaphone et Metaphone3.
    """

    def __init__(self, config: Config = None) -> None:
        """
        Initialise les wrappers phonétiques avec la configuration donnée.

        Args:
            config (Config, optional): Configuration de l'application.
        """
        config = config or Config()
        self._phonex: PhoneticAlgorithm = PhonexWrapper(config=config)
        self._metaphone: PhoneticAlgorithm = MetaphoneWrapper(config=config)
        self._metaphone3: PhoneticAlgorithm = Metaphone3Wrapper(config=config)

    def phonex_encode(self, input_str: str, separator: str = "|", length: int = 8) -> Union[str, List[str]]:
        """Encode une chaîne en utilisant Phonex."""
        return self._phonex.run(input_str, separator, length)

    def metaphone_encode(self, input_str: str, separator: str = "|", length: int = 8) -> Union[str, List[str]]:
        """Encode une chaîne en utilisant Metaphone."""
        return self._metaphone.run(input_str, separator, length)

    def metaphone3_encode(
            self,
            input_str: str,
            separator: str = "|",
            length: int = 8,
            encode_vowels: bool = False,
            encode_exact: bool = True,
    ) -> Union[str, List[str]]:
        """Encode une chaîne en utilisant Metaphone3."""
        return self._metaphone3.run(input_str, separator, length, encode_vowels, encode_exact)


if __name__ == "__main__":
    wrapper = PhoneticWrapper(Config())
    print(wrapper.phonex_encode("Dupont|Durand|Dumont"))
    print(wrapper.metaphone_encode(["Dupont", "Durand", "Dumont"]))
    print(wrapper.metaphone3_encode(["Dupont", "Durand", "Dumont"]))

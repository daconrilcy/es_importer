from typing import Any, Union, List
from ctypes import CDLL
from ext_lib.phonetic.builders.strategy.abstract import AbstractPhoneticStrategy
import logging

logger = logging.getLogger(__name__)


class PhoneticStrategy(AbstractPhoneticStrategy):
    """
    Implémente une stratégie de transformation phonétique
    en utilisant une bibliothèque C externe.
    """

    def __init__(self, lib: CDLL):
        """
        Initialise la stratégie avec une bibliothèque C.

        :param lib: Instance de bibliothèque partagée chargée via ctypes.
        """
        super().__init__(lib)

    def _valid_input_value(self, input_value: Union[str, List[str]]) -> Union[str, List[str]]:
        if input_value is None:
            logger.error("La valeur d'entrée ne peut pas être None.")
            return False

        if isinstance(input_value, str):
            if len(input_value) == 0:
                logger.error("La valeur d'entrée ne peut pas avoir une longueur de 0.")
                return False
            return True

        if isinstance(input_value, list):
            if len(input_value) == 0:
                logger.error("La valeur d'entrée ne peut pas avoir une longueur de 0.")
                return False
            return True

        return False

    def _define_input_str(self, input_value: Union[str, List[str]], separator: str) -> str:
        if not self._valid_input_value(input_value):
            logger.error("La valeur d'entrée n'est pas valide.")
            raise
        if isinstance(input_value, str):
            return input_value
        return separator.join(input_value)

    def process(self, *args: Any, **kwargs: Any) -> str:
        """
        Applique une transformation phonétique via la bibliothèque C.

        :param args: Arguments pour la fonction de transformation.
        :return: Chaîne transformée.
        :raises NotImplementedError: Si non implémentée.
        """
        raise NotImplementedError("La méthode 'process' doit être implémentée par une sous-classe concrète.")
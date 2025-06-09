from ctypes import string_at
from typing import List, Union

from ext_lib.phonetic.builders import PhoneticStrategy


class PhonexStrategy(PhoneticStrategy):
    """
    Stratégie phonétique utilisant l'algorithme Phonex via une bibliothèque C.
    """

    def process(self, input_value: Union[str, List[str]], separator: str, length: int) -> Union[str, List[str]]:
        """
        Applique l'algorithme Phonex sur la chaîne d'entrée.

        :param input_value: Chaine d'entrée ou liste de chaines d'entrée.
        :param separator: Séparateur utilisé pour la sortie Phonex.
        :param length: Longueur maximale allouée pour le buffer de sortie.
        :return: Chaîne transformée selon l’algorithme Phonex.
        :raises MemoryError: Si l’allocation du buffer échoue.
        """
        input_str = self._define_input_str(input_value, separator)

        ptr = self._lib.phonex_auto_alloc(input_str.encode(), separator.encode(), length)
        if not ptr:
            raise MemoryError("Échec de l’allocation du buffer Phonex")

        try:
            result = string_at(ptr).decode()
            if separator in result:
                return result.split(separator)
            return result
        finally:
            self._lib.phonex_free(ptr)

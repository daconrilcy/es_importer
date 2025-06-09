from ctypes import string_at, c_char_p, byref
from typing import List, Union

from ext_lib.phonetic.builders import PhoneticStrategy


class MetaphoneStrategy(PhoneticStrategy):
    """
    Stratégie phonétique utilisant l'algorithme Metaphone via une bibliothèque C.
    """

    def process(self, input_value: Union[str, List[str]],
                separator: str, length: int) -> Union[str, List[str]]:
        """
        Applique l'algorithme Metaphone sur la chaîne d'entrée.

        :param input_value: Chaine d'entrée ou liste de chaines d'entrée.
        :param separator: Séparateur utilisé pour la sortie Metaphone.
        :param length: Longueur maximale allouée pour le buffer de sortie.
        :return: Chaîne transformée selon l’algorithme Metaphone.
        :raises MemoryError: Si l’allocation du buffer échoue.
        """
        input_str = self._define_input_str(input_value, separator)
        output_ptr = c_char_p()

        self._lib.metaphone_api(input_str.encode(), byref(output_ptr), separator.encode(), length)
        if not bool(output_ptr):
            raise MemoryError("Aucun buffer retourné (null pointer).")

        try:
            result = string_at(output_ptr).decode()
            return result.split(separator) if separator in result else result
        finally:
            self._lib.free_output(output_ptr)

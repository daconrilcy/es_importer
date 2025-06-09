from ctypes import string_at
from typing import Union, List, Optional

from ext_lib.phonetic.builders import PhoneticStrategy


class Metaphone3Strategy(PhoneticStrategy):

    def process(
            self,
            input_value: Union[str, List[str]],
            separator: Optional[str] = "|",
            length: Optional[int] = 8,
            encode_vowels: Optional[bool] = True,
            encode_exact: Optional[bool] = False
    ) -> List[tuple[str, str]]:
        input_str = self._define_input_str(input_value, separator)
        lib = self._lib

        sep_byte = separator.encode("utf-8")
        if len(sep_byte) != 1:
            raise ValueError("Le séparateur doit être un caractère ASCII unique.")

        # Appel C, retour c_char_p donc string binaire à décoder
        csv_result_ptr = lib.metaphone3_encode_multi_str(
            input_str.encode("utf-8"),
            sep_byte[0],
            int(length),
            int(encode_vowels),
            int(encode_exact)
        )
        if not bool(csv_result_ptr):
            raise MemoryError("Le pointeur C est NULL")

        # Récupère le contenu du buffer C
        csv_result_bytes = string_at(csv_result_ptr)
        csv_result = csv_result_bytes.decode("utf-8")

        # Libère la mémoire côté C
        lib.free_result_str(csv_result_ptr)

        # Suite inchangée
        lines = [line for line in csv_result.strip().split("\n") if line]
        results = []
        for line in lines:
            cols = line.split("|")
            while len(cols) < 3:
                cols.append("")
            results.append(cols[1:])
        return self._normalize_result(results)

    def _normalize_result(self, raw: List[str]) -> List[tuple[str, str]]:
        """
        Normalise la sortie de Metaphone3.
        :param raw: La sortie de Metaphone3.
        :return: La sortie normalisée.
        """
        # Normalisation : chaque item est un tuple (primary, secondary)
        normalized = []
        for item in raw:
            # Cas normal
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                normalized.append((item[0] or "", item[1] or ""))
            # Cas partiel (rare)
            elif isinstance(item, (list, tuple)) and len(item) == 1:
                normalized.append((item[0] or "", ""))
            else:
                normalized.append(("", ""))
        return normalized

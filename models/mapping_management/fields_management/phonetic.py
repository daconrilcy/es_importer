from typing import Optional, Dict, Union, Any

from config import Config
from models.mapping_management.fields_management.remplacement import ReplacementField


class PhoneticField(ReplacementField):

    def __init__(self, name: str, data: dict, config: Optional[Config] = None):
        self._default_phonetic = {"soundex": False, "metaphone": False, "metaphone3": False}
        super().__init__(name, data, config)
        data["type_completion"] = "phonetic"
        self._phonetics = Dict[str, bool]
        self._set(data)

    def _set(self, data: dict):
        super()._set(data)
        self._keep_original = True
        self._use_first_column = True
        self._phonetics_set(data)

    def _phonetics_set(self, data: dict):
        self._phonetics = data.get("phonetic", None)
        if self._phonetics is None:
            self._phonetics = self._default_phonetic
        for key, value in self._phonetics.items():
            self._phonetics[key] = self._bool_set(value)

    def _bool_set(self, bool_string: Union[str, bool, int]) -> bool:
        if isinstance(bool_string, bool):
            return bool_string
        elif isinstance(bool_string, str):
            return bool_string.lower() in {"true", "1", "yes", "on", "oui", "tru"}
        elif isinstance(bool_string, int):
            return bool_string >= 1
        else:
            return False

    @property
    def phonetics(self) -> Dict[str, bool]:
        return self._phonetics

    @property
    def is_soundex(self) -> bool:
        return self.phonetics.get("soundex", False)

    @property
    def is_metaphone(self) -> bool:
        return self.phonetics.get("metaphone", False)

    @property
    def is_metaphone3(self) -> bool:
        return self.phonetics.get("metaphone3", False)

    @property
    def dict(self) -> Dict[str, Any]:
        data = super().dict
        data["phonetic"] = self.phonetics
        data["category"] = "phonetic"

        return data

if __name__ == '__main__':
    data_test = {"name": "test", "category": "test", "original_field": "test", "type_completion": "phonetic",
                 "column_names": ["test"], "filename": "test",
                 "phonetic": {"soundex": True}}
    field = PhoneticField("test", data_test)
    print(field.dict)

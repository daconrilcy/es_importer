from typing import Union, Optional

from config import Config
from models.mapping_management.fields_management.base import BaseMappingField
from models.mapping_management.fields_management.fixed import FixedValueMappingField
from models.mapping_management.fields_management.phonetic import PhoneticField
from models.mapping_management.fields_management.remplacement import ReplacementField
from models.mapping_management.fields_management.source import MappingSourceField
import logging

logger = logging.getLogger(__name__)


class FieldsCreator(BaseMappingField):
    def __init__(self, field_info: dict, config: Optional[Config] = None) -> None:
        self._base_categories = ["fixed_value", "remplacement", "phonetic", "source"]
        super().__init__(field_info["name"], field_info, config)
        self._is_valid = True
        self._field: Union[FixedValueMappingField, ReplacementField, PhoneticField, MappingSourceField] = None
        self._set(field_info)

    def _set(self, field_info: dict) -> None:
        if field_info is None:
            self._is_valid = False
            return
        if not isinstance(field_info, dict):
            self._is_valid = False
            return
        if "category" in field_info:
            if field_info["category"] not in self._base_categories:
                self._is_valid = False
                return
            self._category = field_info["category"]

        self._set_field(field_info)

    def _set_field(self, field_info: dict) -> None:
        if self._category == "fixed_value":
            self._set_fixed_field(field_info)
        elif self._category == "remplacement":
            self._set_remplacement_field(field_info)
        elif self._category == "phonetic":
            self._set_phonetic_field(field_info)
        elif self._category == "source":
            self._set_source_field(field_info)

    def _set_source_field(self, field_info: dict) -> None:
        try:
            field_info["type"] = "text"
            field_info["mapped"] = True
            field_info["analyzer"] = "standard"
            self._field = MappingSourceField(self.name, field_info)
        except Exception as e:
            self._is_valid = False
            logger.error("FieldsCreator - set_source_field - Erreur : %s", e)

    def _set_fixed_field(self, field_info: dict) -> None:
        try:
            self._field = FixedValueMappingField(self.name, field_info)
        except Exception as e:
            self._is_valid = False
            logger.error("FieldsCreator - set_fixed_field - Erreur : %s", e)

    def _set_phonetic_field(self, field_info: dict) -> None:
        try:
            self._field = PhoneticField(self.name, field_info)
        except Exception as e:
            self._is_valid = False
            logger.error("FieldsCreator - set_phonetic_field - Erreur : %s", e)

    def _set_remplacement_field(self, field_info: dict) -> None:
        try:
            self._field = ReplacementField(self.name, field_info)
        except Exception as e:
            self._is_valid = False
            logger.error("FieldsCreator - set_remplacement_field - Erreur : %s", e)

    @property
    def field(self) -> Union[FixedValueMappingField, ReplacementField, PhoneticField, MappingSourceField]:
        return self._field

    @property
    def category(self) -> str:
        return self._category

    @property
    def is_valid(self) -> bool:
        return self._is_valid


if __name__ == "__main__":
    # Test the FieldsCreator class
    field_info_test = {
        "name": "test_field",
        "category": "fixed",
        "value": "test_value",
    }
    creator_test = FieldsCreator(field_info_test)
    print(creator_test.field)
    field_info_test = {
        "name": "test_field",
        "original_field": "test_original_field",
        "type_completion": "synonymes",
        "category": "remplacement",
        "column_names": "test_column",
        "filename": "test_file.txt",
    }
    creator_test = FieldsCreator(field_info_test)
    print(creator_test.field)
    field_info_test = {
        "name": "test_field",
        "category": "phonetic",
        "type_completion": "phonetic",
        "column_names": ["test_column1", "test_column2"],
        "phonetic": {"soundex": True, "metaphone": True, "metaphone3": True},
        "filename": "test_file.txt",
    }
    creator_test = FieldsCreator(field_info_test)
    print(creator_test.field)

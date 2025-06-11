from typing import Dict, Any

from config import Config
from models.mapping_management.fields_management.base import BaseMappingField

import logging

logger = logging.getLogger(__name__)


class FixedValueMappingField(BaseMappingField):

    def __init__(self, name: str, data: Dict[str, Any], config: Config = None) -> None:
        super().__init__(name, data, config)
        self._value: Any = None
        self._set(data)

    def _set(self, data: Dict[str, Any]):
        if data is None:
            return
        if "value" not in data:
            logger.error("FixedValueField : Le champ 'value' est manquant.")
            self._value = None
            return
        self._value = data.get("value", None)
        if not self._value:
            logger.error("FixedValueField : Le champ 'value' est None.")

    def value(self):
        return self._value

    @property
    def dict(self):
        dict_base = super().dict
        dict_base["value"] = self._value
        return dict_base


if __name__ == "__main__":
    test_data = {"name": "test", "category": "test", "value": "test"}
    field = FixedValueMappingField("test", test_data)
    print(field.dict)
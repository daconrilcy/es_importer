from typing import Optional

from config import Config
from models.elastic_specifiques.base_type import BasicEsModule
from models.elastic_specifiques.es_types.field import EsFieldType


class EsTypes(BasicEsModule):
    def __init__(self, config: Optional[Config] = None):
        config = config or Config()
        super().__init__(config.es_types_filepath)

    def _fill_fields(self) -> None:
        fields_raw = super()._pre_fill_fields()
        if fields_raw is None:
            return
        for field_raw in fields_raw:
            if not isinstance(field_raw, dict):
                continue
            if field_raw.get("name") is None:
                continue
            self._fields[field_raw['name']] = EsFieldType(doc=field_raw)


if __name__ == "__main__":
    et = EsTypes()
    print(et.fields_names)

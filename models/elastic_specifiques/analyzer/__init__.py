import logging
from typing import Optional

from config import Config
from models.elastic_specifiques.analyzer.field import AnalyzerBaseField
from models.elastic_specifiques.base_type import BasicEsModule

logger = logging.getLogger(__name__)


class BasicAnalyzers(BasicEsModule):
    """
    Classe chargée de lire et d'encapsuler des définitions d'analyseurs
    depuis un fichier JSON et de les représenter sous forme d'objets AnalyzerBaseField.
    """

    def __init__(self, config: Optional[Config] = None):
        config = config or Config()
        super().__init__(config.es_analyzers_filepath)

    def _fill_fields(self) -> None:
        fields_raw = super()._pre_fill_fields()
        if fields_raw is None:
            return
        for field_raw in fields_raw:
            if not isinstance(field_raw, dict):
                continue
            if field_raw.get("name") is None:
                continue
            self._fields[field_raw['name']] = AnalyzerBaseField(doc=field_raw)


if __name__ == "__main__":
    et = BasicAnalyzers()
    print(et.fields_names)
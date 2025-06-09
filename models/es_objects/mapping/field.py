from typing import Optional, Any

from models.elastic_specifiques import EsFieldType
from models.es_analyser import EsAnalysers, EsAnalyser
from models.es_objects.model_field import ModelField


class MappingField(ModelField):
    """
    Représente un champ de mapping pour un fichier Elasticsearch.
    """

    def __init__(self,
                 field_name: Optional[str] = None,
                 field_type: Optional[EsFieldType | str] = None,
                 value: Optional[Any] = None,
                 description: Optional[str] = None,
                 source_field_name: Optional[str] = None,
                 analyzer: Optional[str] = None,
                 fixed: Optional[bool] = False,
                 mapped: Optional[bool] = True,
                 ):
        super().__init__(field_name=field_name,
                         field_type=field_type,
                         value=value,
                         description=description,
                         )
        self._analysers = EsAnalysers()
        self.source_field_name = source_field_name
        self._analyzer_name = None
        self.analyzer = analyzer
        self.mapped = mapped
        self.fixed = fixed
        self.excluded_keys.extend(["_analyzer", "_analysers"])

    @property
    def source_field_name(self) -> str:
        """Nom du champ source dans le fichier d’origine."""
        return self._source_field_name

    @source_field_name.setter
    def source_field_name(self, value: str):
        self._source_field_name = value

    @property
    def analyzer_name(self) -> str:
        """Nom de l’analyseur utilisé."""
        return self._analyzer_name

    @property
    def analyzer(self) -> EsAnalyser | None:
        """Analyseur utilisé (english, french...)."""
        return self._analyzer

    @analyzer.setter
    def analyzer(self, value: str | EsAnalyser | None = None):
        if isinstance(value, str):
            analyser = self._analysers.get_analyser(value)
        elif isinstance(value, EsAnalyser):
            analyser = value
        else:
            analyser = None

        if analyser is None:
            analyser = self._analysers.get_analyser("standard")

        self._analyzer = analyser
        self._analyzer_name = analyser.name

    @property
    def mapped(self) -> bool:
        """Champ mappé ou non dans Elasticsearch."""
        return self._mapped

    @mapped.setter
    def mapped(self, value: bool):
        self._mapped = value

    @property
    def fixed(self) -> bool:
        """Champ à valeur fixe ou dynamique."""
        return self._fixed

    @fixed.setter
    def fixed(self, value: bool):
        self._fixed = value


if __name__ == "__main__":
    field = MappingField(field_name="example_field", field_type="text", value="example_value")
    print(field.field_name)
    print(field.type)
    print(field.value)
    print(field)

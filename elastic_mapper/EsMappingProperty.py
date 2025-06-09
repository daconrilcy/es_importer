import pandas as pd
from models.elastic_specifiques import EsFieldType
from utils import sanitaze_string


class EsMappingProperty:
    """
    Class which represent fields of a mapping
    """

    def __init__(self, fields_types: list[EsFieldType] = None, row: pd.Series = None):
        self._sourcefield = None
        self._name = None
        self._type = None
        self._has_analyzer = False
        self._analyzer = None
        self._has_normalizer = False
        self._normalizer = None
        self._to_map = True
        self._is_fixed = False
        self._fixed_value = None
        self.fields_types = fields_types
        self.excluded_attributes = ["_excluded_attributes", "_fields_types", "_has_analyzer", "_has_normalizer"]
        if row is not None:
            self.set_from_df_row(row)

    @property
    def source_field(self) -> str | None:
        """
        Get the source field.
        :return: Source field.
        """
        return self._sourcefield

    @source_field.setter
    def source_field(self, value: str | None):
        """
        Set the source field.
        :param value: Source field.
        """
        self._sourcefield = value

    @property
    def name(self) -> str:
        """
        Get the name of the field.
        :return: Name of the field.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Set the name of the field.
        :param value: Name of the field.
        """
        self._name = sanitaze_string(value)

    @property
    def type(self) -> EsFieldType:
        """
        Get the type of the field.
        :return: Type of the field.
        """
        return self._type

    @property
    def fields_types(self) -> list[EsFieldType]:
        """
        Get the list of fields types.
        :return: List of fields types.
        """
        return self._fields_types

    @fields_types.setter
    def fields_types(self, value: list[EsFieldType]):
        """
        Set the list of fields types.
        :param value: List of fields types.
        """
        self._fields_types = value

    @type.setter
    def type(self, value: EsFieldType):
        """
        Set the type of the field.
        :param value: Type of the field.
        """
        self._type = value

    def set_type_by_name(self, name: str):
        """
        Set the type of the field by name.
        :param name: Name of the type.
        """
        if self.fields_types is not None:
            finded = False
            for fts in self.fields_types:
                if fts.is_this(name):
                    self._type = fts
                    finded = True
                    break
            if not finded:
                print(f"EsMappingProperty - Type {name} not found in the list of fields types.")
            return
        else:
            self._type = EsFieldType(name=name)

    @property
    def has_analyzer(self) -> bool:
        """
        Get the has analyzer flag.
        :return: Has analyzer flag.
        """
        return self._has_analyzer

    @has_analyzer.setter
    def has_analyzer(self, value: bool):
        """
        Set the has analyzer flag.
        :param value: Has analyzer flag.
        """
        self._has_analyzer = value

    @property
    def analyzer(self) -> str:
        """
        Get the analyzer.
        :return: Analyzer.
        """
        return self._analyzer

    @analyzer.setter
    def analyzer(self, value: str):
        """
        Set the analyzer.
        :param value: Analyzer.
        """
        self._analyzer = value
        if value is not None and value != "":
            self._has_analyzer = True

    @property
    def has_normalizer(self) -> bool:
        """
        Get the has normalizer flag.
        :return: Has normalizer flag.
        """
        return self._has_normalizer

    @has_normalizer.setter
    def has_normalizer(self, value: bool):
        """
        Set the has normalizer flag.
        :param value: Has normalizer flag.
        """
        self._has_normalizer = self._is_true_mixed(value)

    @property
    def normalizer(self) -> str:
        """
        Get the normalizer.
        :return: Normalizer.
        """
        return self._normalizer

    @normalizer.setter
    def normalizer(self, value: str):
        """
        Set the normalizer.
        :param value: Normalizer.
        """
        self._normalizer = value
        if value is not None and value != "":
            self._has_normalizer = True

    @property
    def to_map(self) -> bool:
        """
        Get the to map flag.
        :return: To map flag.
        """
        return self._to_map

    @to_map.setter
    def to_map(self, value: bool | None):
        """
        Set the to map flag.
        :param value: To map flag.
        """
        if value is None:
            self._to_map = True
        else:
            self._to_map = self._is_true_mixed(value)

    @property
    def is_fixed(self) -> bool:
        """
        Get the is fixed flag.
        :return: Is fixed flag.
        """
        return self._is_fixed

    @is_fixed.setter
    def is_fixed(self, value: bool | None):
        """
        Set the is fixed flag.
        :param value: Is fixed flag.
        """
        if value is None:
            self._is_fixed = False
        else:
            self._is_fixed = value

    @property
    def fixed_value(self) -> str:
        """
        Get the fixed value.
        :return: Fixed value.
        """
        return self._fixed_value

    @fixed_value.setter
    def fixed_value(self, value: str):
        """
        Set the fixed value.
        :param value: Fixed value.
        """
        if value is not None and value != "":
            self._is_fixed = True
        self._fixed_value = value

    @property
    def excluded_attributes(self) -> list[str]:
        """
        Get the excluded attributes.
        :return: Excluded attributes.
        """
        return self._excluded_attributes

    @excluded_attributes.setter
    def excluded_attributes(self, value: list[str]):
        """
        Set the excluded attributes.
        :param value: Excluded attributes.
        """
        self._excluded_attributes = value

    def to_doc(self) -> dict:
        """
        Get the document.
        :return: Document.
        """
        doc = {self.name: {}}
        doc[self.name]["type"] = self.type.name
        if self.has_analyzer:
            doc[self.name]["analyzer"] = self.analyzer
        if self.has_normalizer:
            doc[self.name]["normalizer"] = self.normalizer

        return doc

    @staticmethod
    def _get_attr_clean_name(attr_name: str):
        """
        Get the clean name of the attribute.
        :param attr_name: Name of the attribute.
        :return: Clean name of the attribute.
        """
        return attr_name.replace("_", "")

    def attr_to_list(self):
        """
        Get the attributes of the class as a list.
        :return: List of attributes.
        """
        attrs = []
        for at in self.__dict__.keys():
            if at not in self.excluded_attributes:
                attrs.append(self._get_attr_clean_name(at))

        return attrs

    def check_fields_struct(self, field_names_list: list[str]) -> bool:
        """
        Check if the fields structure is correct.
        :param field_names_list: List of data fields.
        :return: True if the structure is correct, False otherwise.
        """
        attrs = self.attr_to_list()

        not_found = []
        not_found_optional = []
        for at in attrs:
            if at not in field_names_list:
                if at == "normalizer":
                    not_found_optional.append(at)
                elif at == "tomap":
                    not_found_optional.append(at)
                elif at == "isfixed":
                    not_found_optional.append(at)
                elif at == "fixedvalue":
                    not_found_optional.append(at)
                else:
                    if at == "sourcefield":
                        if ("isfixed" in field_names_list) and ("fixedvalue" in field_names_list):
                            continue
                    not_found.append(at)
        if len(not_found) > 0:
            print(f"EsMappingProperty - {len(not_found)} Fields not found: {not_found}")
            return False
        elif len(not_found_optional) > 0:
            print(f"EsMappingProperty  - {len(not_found_optional)} Optionals Fields not found: {not_found_optional}")
        return True

    def set_from_df_row(self, row: pd.Series):
        """
        Add the property from a DataFrame row.
        :param row: DataFrame row.
        """
        attrs = self.attr_to_list()
        for at in attrs:
            at_u = f"_{at}"
            if at in row:
                if at == "type":
                    self.set_type_by_name(row[at])
                else:
                    setattr(self, at_u, row[at])
            else:
                if at == "sourcefield":
                    setattr(self, at_u, None)
                elif at == "type":
                    setattr(self, at_u, None)
                elif at == "analyzer":
                    setattr(self, at_u, None)
                    self.has_analyzer = False
                elif at == "normalizer":
                    setattr(self, at_u, None)
                    self.has_normalizer = False
                elif at == "tomap":
                    setattr(self, at_u, True)
                elif at == "isfixed":
                    setattr(self, at_u, False)
                elif at == "fixedvalue":
                    setattr(self, at_u, None)

    def reset(self):
        """
        Reset the property.
        """
        self._type = None
        self._has_analyzer = False
        self._analyzer = None
        self._has_normalizer = False
        self._normalizer = None
        self._to_map = True
        self._is_fixed = False
        self._fixed_value = None

    def get_doc(self):
        """
        Get the document.
        :return:
        """
        doc = {self.name: {"type": self.type.name}}
        if self.has_analyzer:
            doc[self.name]["analyzer"] = self.analyzer
        if self.has_normalizer:
            doc[self.name]["normalizer"] = self.normalizer
        return doc

    @staticmethod
    def _is_true_mixed(value):
        """
        Check if the value is true.
        :param value:
        :return:
        """
        if value is None:
            return False
        if isinstance(value, str):
            if value.lower() == "true" or value.lower() == "tru" or value.lower() == "1" or value.lower() == "yes":
                return True
            return False
        elif isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return value == 1
        return False

    def __str__(self):
        return (f"{self.name} - {self.source_field} - {self.type.name} - {self.has_analyzer} - {self.analyzer} - "
                f"{self.has_normalizer} - "
                f"{self.normalizer} - {self.to_map} - {self.is_fixed} - {self.fixed_value}")

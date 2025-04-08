import pandas as pd

from utils import sanitaze_string


class EsFieldType:
    """
    ElasticSearch field type class.
    """

    def __init__(self, name: str = None, category: str = None, description: str = None):
        self._name = None
        self._category = None
        self._description = None
        if name is not None:
            self.name = name
        if category is not None:
            self.category = category
        if description is not None:
            self.description = description

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
        self._name = self.sanitize_or_none("name", value)

    @property
    def category(self) -> str:
        """
        Get the category of the field.
        :return: Category of the field.
        """
        return self._category

    @category.setter
    def category(self, value: str):
        """
        Set the category of the field.
        :param value: Category of the field.
        """
        self._category = self.sanitize_or_none("category", value)

    @property
    def description(self) -> str:
        """
        Get the type of the field.
        :return: Type of the field.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Set the type of the field.
        :param value: Type of the field.
        """
        self._description = value

    def is_this(self, name: str):
        """
        Check if the name is the same as the name of the field.
        :param name:
        :return:
        """
        proper_name = sanitaze_string(name)
        return self.name == proper_name

    def set_from_df_row(self, row: pd.DataFrame.values):
        """
        Set the field type from a DataFrame row.
        :param row:
        :return:
        """
        if "name" not in row:
            print("EsFieldType - set_from_df_row - name not in row")
            return
        if "category" not in row:
            print("EsFieldType - set_from_df_row - category not in row")
            return
        if "description" not in row:
            print("EsFieldType - set_from_df_row - description not in row")
            return
        if row["name"] is None:
            print("EsFieldType - set_from_df_row - name is None")
            return
        if row["category"] is None:
            print("EsFieldType - set_from_df_row - category is None")
            return
        if row["description"] is None:
            print("EsFieldType - set_from_df_row - description is None")
        self.name = row["name"]
        self.category = row["category"]
        self.description = row["description"]

    @staticmethod
    def sanitize_or_none(source: str, value: str) -> str:
        """
        Sanitize a string or return None if the string is None.
        :param source: Source of the string.
        :param value: String to sanitize.
        :return: Sanitized string.
        """
        if value is None:
            print(f"EsFieldType - {source} value is None")
            return ""
        return sanitaze_string(value)

    def __str__(self):
        return f"{self.name} - {self.category} - {self.description}"

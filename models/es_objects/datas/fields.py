from copy import copy
from typing import Optional, Dict, List

import pandas as pd
from models.elastic_specifiques.collection import EsTypes
from models.es_objects.model_field import ModelField
from utils import infer_es_type_from_values, clean_pd_dataframe


class DataFields:
    """
    Représente un champ de données pour un fichier Elasticsearch.
    """

    def __init__(self,
                 datas: pd.DataFrame | Dict | None = None,
                 ):
        self._es_types = EsTypes()
        self._list = {}
        self._headers = []
        self.max_list = 6
        self.max_columns = 12
        if datas is not None:
            if isinstance(datas, pd.DataFrame):
                self.list = datas
            elif isinstance(datas, dict):
                self.list_from_dict_lists(datas)

    @property
    def list(self) -> dict:
        """
        Retourne une liste contenant les champs de données.
        :return:
        """
        return self._list

    def list_by_header(self, header_name: str) -> list:
        """
        Retourne une liste contenant les champs de données.
        :return:
        """
        if header_name in self._list:
            return self._list[header_name]
        return []

    def list_by_index(self, index: int) -> list:
        """
        Retourne une liste contenant les champs de données.
        :return:
        """
        result = []
        for header in self._list:
            if index < len(self._list[header]):
                result.append(self._list[header][index])
        return result

    @property
    def is_empty(self) -> bool:
        """
        Retourne True si la liste est vide, sinon False.
        :return:
        """
        return len(self._list) == 0

    def list_first_indexes(self, index: int) -> list:
        """
        Retourne une liste contenant les champs de données.
        :return:
        """
        result = []
        for header in self._list:
            imax = len(self._list[header])
            if index < imax:
                imax = index
            list_temp = []
            for i in range(imax):
                if i < len(self._list[header]):
                    list_temp.append(self._list[header][i])
                break
            result.append(list_temp)
        return result

    @property
    def pd_list(self) -> pd.DataFrame:
        """
        Retourne une liste contenant les champs de données.
        :return:
        """
        if len(self._list) == 0:
            return pd.DataFrame()
        return pd.DataFrame.from_dict(self._list, orient="index")

    @property
    def headers(self) -> list:
        """
        Retourne une liste contenant les noms des champs de données.
        :return:
        """
        return self._headers

    @headers.setter
    def headers(self, headers: list):
        """
        Setter pour la liste des champs de données.
        :param headers:
        :return:
        """
        if headers is None or not isinstance(headers, list):
            return
        self._headers = headers

    @list.setter
    def list(self, datas: pd.DataFrame | None):
        """
        Setter pour la liste des champs de données.
        :param datas:
        :return:
        """
        if datas is None or not isinstance(datas, pd.DataFrame):
            return

        self._list.clear()

        for nc, pd_field in enumerate(datas.columns, start=1):
            temp_list = []
            serie = datas[pd_field]
            if len(serie) == 0 or pd_field is None:
                continue
            field_type_name = infer_es_type_from_values(serie)

            field_type = self._es_types.get_type(field_type_name)
            field_model = ModelField(field_name=pd_field, field_type=field_type)
            for nf, value in enumerate(datas[pd_field], start=1):
                field_model.value = value
                temp_list.append(copy(field_model))
            self._list[pd_field] = temp_list
            self._headers.append(pd_field)

    def list_datas_from_lists(self, headers_list: list, datas_list: list) -> bool:
        """
        Retourne une liste contenant les champs de données.
        :param headers_list:
        :param datas_list:
        :return:
        """
        if headers_list is None or not isinstance(headers_list, list):
            print("❌ headers_list is None or not a list")
            return False
        if datas_list is None or not isinstance(datas_list, list):
            print("❌ datas_list is None or not a list")
            return False
        if len(headers_list) != len(datas_list):
            print("❌ headers_list and datas_list have different lengths")
            return False

        pd_field = pd.DataFrame(datas_list, columns=headers_list)
        self._list.clear()
        self.list = pd_field

    def list_from_dict_lists(self, dict_lists: Dict[str, List[str]]) -> bool:
        """
        Génère la liste de données à partir d'un dictionnaire contenant headers et datas.

        :param dict_lists: Dictionnaire du type {"headers": List[str], "datas": List[str]}
        :return: bool indiquant le succès
        """
        if not isinstance(dict_lists, dict):
            print("❌ dict_lists n'est pas un dictionnaire valide.")
            return False

        if "headers" not in dict_lists or "datas" not in dict_lists:
            print("❌ dict_lists doit contenir les clés 'headers' et 'datas'.")
            return False

        headers = dict_lists["headers"]
        datas = dict_lists["datas"]

        if not (isinstance(headers, list) and all(isinstance(h, str) for h in headers)):
            print("❌ headers doit être une liste de chaînes.")
            return False

        if not (isinstance(datas, list) and all(isinstance(d, list) for d in datas)):
            print("❌ datas doit être une liste de lists.")
            return False

        if len(headers) != len(datas):
            print("❌ headers et datas n'ont pas la même longueur.")
            return False

        if len(headers) == 0:
            print("❌ headers et datas ne peuvent pas être vides.")
            return False

        return self.list_datas_from_lists(headers, datas)

    def __str__(self):
        """
        Retourne la représentation sous forme de chaîne de caractères de l'objet DataFields.
        """
        lines = []
        for header in self._headers:
            if header not in self._list:
                continue
            lines.append(f"{header}:")
            for field in self._list[header]:
                if field is not None:
                    lines.append(f"  {field}")
        return "\n".join(lines)


if __name__ == "__main__":
    data = clean_pd_dataframe(pd.read_csv(
        r"C:\dev\py\csv_importer\files\datas\curiexplore-pays.csv", sep=";"))
    data_fields_test = DataFields(data)
    print(data_fields_test.headers)
    print("list fields index n:3")
    for field_test in data_fields_test.list_by_index(3):
        print(field_test)
    print("----------------")
    headers_test = ['col1', 'col2']
    datas_test = [['val1', 'val2'], ['val3', 'val4']]
    data_fields_test.list_datas_from_lists(headers_test, datas_test)
    print(data_fields_test)
    data_fields_test.list_from_dict_lists({"headers": headers_test, "datas": datas_test})
    print(data_fields_test)

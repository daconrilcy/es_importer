"""
This file contains the class IndexDetails which is used to store the index name and mapping of the index.
"""
import json
import os


class IndexDetails:
    """
    Class used to store the index name and mapping of the index
    """

    def __init__(self, index_name: str, mapping: dict, datas_filepath: str = None):
        self._index_name = index_name
        self._mapping = mapping
        self._datas_filepath = datas_filepath

    @property
    def index_name(self) -> str:
        """
        Get the index name
        :return:
        """
        return self._index_name

    @property
    def mapping(self) -> dict:
        """
        Get the mapping of the index
        :return:
        """
        return self._mapping

    @property
    def datas_filepath(self) -> str:
        """
        Get the datas filepath
        :return:
        """
        return self._datas_filepath

    @property
    def datas(self) -> list | None:
        """
        Get the datas
        :return:
        """
        if self._datas_filepath is None:
            print("❌ IndexDetails.datas: datas_filepath is None")
            return None
        if not os.path.exists(self._datas_filepath):
            print(f"❌ IndexDetails.datas: {self._datas_filepath} does not exist")
            return None
        try:
            with open(self._datas_filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"❌ IndexDetails.datas: {e}")
            return None

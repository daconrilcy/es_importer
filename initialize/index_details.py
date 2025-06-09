"""
This module defines the IndexDetails class used to encapsulate the name, mapping,
and optional data source (JSON file) of an index.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


class IndexDetails:
    """
    Encapsulates the name, mapping, and data file path for an index.
    """

    def __init__(self, index_name: str, mapping: dict, datas_filepath: Optional[Union[str, Path]] = None):
        self._index_name = index_name
        self._mapping = mapping
        self._datas_filepath = Path(datas_filepath) if datas_filepath is not None else None

    @property
    def index_name(self) -> str:
        """
        Returns the name of the index.
        """
        return self._index_name

    @property
    def mapping(self) -> dict:
        """
        Returns the mapping associated with the index.
        """
        return self._mapping

    @property
    def datas_filepath(self) -> Optional[Path]:
        """
        Returns the file path to the associated data (if any).
        """
        return self._datas_filepath

    @property
    def datas(self) -> Optional[list]:
        """
        Loads and returns datas from the JSON file if the file path is set and valid.

        Returns:
            A list of records if successful, otherwise None.
        """
        if self._datas_filepath is None:
            logger.error("IndexDetails.datas: datas_filepath is None")
            return None

        if not self._datas_filepath.exists():
            logger.error("IndexDetails.datas: %s does not exist", self._datas_filepath)
            return None

        try:
            with self._datas_filepath.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.error("IndexDetails.datas: JSON decode error - %s", e)
        except OSError as e:
            logger.error("IndexDetails.datas: File access error - %s", e)

        return None

from ctypes import cdll
from typing import Any, Dict, Type, Union, List, Optional
import logging

from config import Config
from ext_lib.phonetic.builders.strategy import PhoneticStrategy

logger = logging.getLogger(__name__)

from ext_lib.phonetic.builders.c_lib.abstract import CLib


class CTypesLib(CLib):
    def __init__(self, lib_name: str,
                 signature: Dict[str, Dict[str, Any]],
                 strategy: Type[PhoneticStrategy], _: int = 0,
                 config: Optional[Config] = None
                 ):
        config = config or Config()
        lib_path = config.get_lib_path(lib_name)
        self._signatures = signature
        self._lib = None
        self._load_library(lib_path)
        self._strategy = strategy(self._lib)

    def _load_library(self, lib_path: str) -> Any:
        try:
            lib = cdll.LoadLibrary(lib_path)
            for func_name, sig in self._signatures.items():
                if hasattr(lib, func_name):
                    func = getattr(lib, func_name)
                    func.argtypes = sig.get("argtypes", [])
                    func.restype = sig.get("restype", None)
            self._lib = lib
        except OSError as e:
            logger.error(f"Erreur lors du chargement de la bibliothèque Metaphone : {e}")
            raise

    def run(self, *args: Any) -> Union[str, List[str]]:
        return self._strategy.process(*args)

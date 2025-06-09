from typing import Type, Union, List
from ext_lib.phonetic.builders import CTypesLib
from ext_lib.phonetic.wrappers.base.abstract import BaseWrapperAbstract


class BaseWrapper(BaseWrapperAbstract):
    def __init__(self, lib: Type[CTypesLib] = None):
        self._lib = lib

    def run(self, *args):
        return self._lib.run(*args)

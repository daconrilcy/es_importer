from typing import Optional

from config import Config
from ext_lib.phonetic.builders import CTypesLib
from ext_lib.phonetic.wrappers.phonex.signature import phonex_signature
from ext_lib.phonetic.wrappers.phonex.strategy import PhonexStrategy


class ClibPhonex(CTypesLib):

    def __init__(self, config: Optional[Config] = None, _=0):
        super().__init__(lib_name="phonex",
                         config=config,
                         signature=phonex_signature,
                         strategy=PhonexStrategy,
                         _=_)

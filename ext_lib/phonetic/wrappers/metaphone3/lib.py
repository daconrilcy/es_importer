from typing import Optional

from config import Config
from ext_lib.phonetic.builders import CTypesLib
from ext_lib.phonetic.wrappers.metaphone3.signature import metaphone3_signature
from ext_lib.phonetic.wrappers.metaphone3.strategy import Metaphone3Strategy


class ClibMetaphone3(CTypesLib):

    def __init__(self, config: Optional[Config] = None, _=0):
        super().__init__(lib_name="metaphone3",
                         config=config,
                         signature=metaphone3_signature,
                         strategy=Metaphone3Strategy,
                         _=_)

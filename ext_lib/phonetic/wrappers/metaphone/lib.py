from config import Config
from ext_lib.phonetic.builders import CTypesLib
from ext_lib.phonetic.wrappers.metaphone.signature import metaphone_signature
from ext_lib.phonetic.wrappers.metaphone.strategy import MetaphoneStrategy


class ClibMetaphone(CTypesLib):

    def __init__(self, config: Config, _=0):
        super().__init__(lib_name="metaphone",
                         signature=metaphone_signature,
                         strategy=MetaphoneStrategy,
                         config=config,
                         _=_)
from typing import Optional

from config import Config
from ext_lib.phonetic.wrappers.base import BaseWrapper
from ext_lib.phonetic.wrappers.phonex.lib import ClibPhonex


class PhonexWrapper(BaseWrapper):

    def __init__(self, config: Optional[Config]):
        config = config or Config()
        super().__init__(lib=ClibPhonex(config=config, _=8))
    #     """
    #     Initialise la stratégie Phonex avec la configuration spécifiée.
    #
    #     :param config: Configuration de l'application
    #     """

if __name__ == "__main__":
    config_test = Config()
    phonex = PhonexWrapper(config_test)
    print(phonex.run("Dupont", "|", 4))
    print(phonex.run(["Dupont", "jacques", "jean", "pierre"], "|", 4))

from typing import Optional

from config import Config
from ext_lib.phonetic.wrappers.base import BaseWrapper
from ext_lib.phonetic.wrappers.metaphone3.lib import ClibMetaphone3


class Metaphone3Wrapper(BaseWrapper):

    def __init__(self, config: Optional[Config]):
        config = config or Config()
        super().__init__(lib=ClibMetaphone3(config=config, _=8))
    #     """
    #     Initialise la stratégie Phonex avec la configuration spécifiée.
    #
    #     :param config: Configuration de l'application
    #     """


if __name__ == "__main__":
    import pprint

    config_test = Config()
    dm_test = Metaphone3Wrapper(config_test)
    print(dm_test.run("Jose", "|", 4, True, False))
    print(dm_test.run("Smith", "|", 4))
    print(dm_test.run("Schmidt", "|", 8, False, True))
    pprint.pprint(dm_test.run(["London", "jacques", "jean", "pierre"]))

    print(dm_test.run("Tanzania,United Republic of", "|", 4, True, True))
    print(dm_test.run("Tanzania,United Republic of", "|", 4, False, True))
    print(dm_test.run("Tanzania,United Republic of", "|", 4, True, False))
    print(dm_test.run("Tanzania,United Republic of", "|", 4, False, False))

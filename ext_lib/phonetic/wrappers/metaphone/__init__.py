from config import Config
from ext_lib.phonetic.wrappers.metaphone.lib import ClibMetaphone


class MetaphoneWrapper:

    def __init__(self, config: Config) -> None:
        """
        Initialise la stratégie Phonex avec la configuration spécifiée.

        :param config: Configuration de l'application
        """
        config = config or Config()
        self._lib = ClibMetaphone(config=config, _=0)

    def run(self, input_str: str, separator: str = "|", length: int = 8):
        return self._lib.run(input_str, separator, length)


if __name__ == "__main__":
    config_test = Config()
    phonex = MetaphoneWrapper(config_test)
    print(phonex.run("Dupont", "|", 4))
    print(phonex.run(["Dupont", "jacques", "jean", "pierre"], "|", 4))

from config import Config
from initialize.infos_reader import InfosFileReader
from initialize.index_builder import IndexDetailsBuilder
from initialize.index_details import IndexDetails


class InitConfigFiles:
    """
    Coordination de la lecture des fichiers de configuration et
    construction des IndexDetails.
    """

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.reader = InfosFileReader(self.config.es_init_infos)
        self.builder = IndexDetailsBuilder(self.config.config_folder)

        self._index_files = self._load(self.config.index_files_name)
        self._index_types = self._load(self.config.index_files_type_name)
        self._index_es_types = self._load(self.config.index_es_types_name)
        self._index_es_analysers = self._load(self.config.index_es_analysers_name)

    def _load(self, key: str) -> IndexDetails:
        return self.builder.build(self.reader.get(key))

    @property
    def index_files(self) -> IndexDetails:
        return self._index_files

    @property
    def index_types(self) -> IndexDetails:
        return self._index_types

    @property
    def index_es_types(self) -> IndexDetails:
        return self._index_es_types

    @property
    def index_es_analysers(self) -> IndexDetails:
        return self._index_es_analysers

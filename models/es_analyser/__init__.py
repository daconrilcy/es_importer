from models.es_analyser.es_analyser import EsAnalyser


class EsAnalysers:
    """
    Analyzers for Elasticsearch.
    """

    def __init__(self):
        """
        Initialize the EsAnalysers class.
        """
        self._analyzers = {}
        self._set_default_analyzers()

    @property
    def analyzers(self) -> dict[str, EsAnalyser]:
        """
        Get the analyzers.
        :return: The analyzers.
        """
        return self._analyzers

    @property
    def list(self) -> list[EsAnalyser]:
        """
        Get the list of analyzers.
        :return: The list of analyzers.
        """
        list_analysers = []
        for name, analyzer_class in self._analyzers.items():
            if name is None:
                continue
            if not isinstance(analyzer_class, EsAnalyser):
                continue
            list_analysers.append(analyzer_class)

        return list_analysers

    def get_analyser(self, analyser_name: str) -> EsAnalyser or False:
        """
        Get the specified analyzer.

        :param analyser_name: The name of the analyzer to retrieve.
        :return: The specified analyzer.
        """
        if analyser_name is None:
            print("EsAnalysers.get_analyser: analyser_name is None")
            return False
        analyser_name = analyser_name.lower()
        if analyser_name in self._analyzers:
            return self._analyzers[analyser_name]
        else:
            print(f"EsAnalysers.get_analyser: analyser_name {analyser_name} not found")
            return False

    def is_valid_analyser(self, analyser_name: str) -> bool:
        """
        Check if the specified analyzer is valid.

        :param analyser_name: The name of the analyzer to check.
        :return: True if the analyzer is valid, False otherwise.
        """
        if analyser_name is None:
            print("EsAnalysers.is_valid_analyser: analyser_name is None")
            return False
        analyser_name = analyser_name.lower()
        if analyser_name in self._analyzers:
            return True
        else:
            print(f"EsAnalysers.is_valid_analyser: analyser_name {analyser_name} not found")
            return False

    def _set_default_analyzers(self):
        """
        Set the default analyzers.
        """
        from elastic_manager import ElasticSearchManager
        es = ElasticSearchManager()
        docs = es.get_es_analyzers()
        if docs is None:
            print("EsAnalysers._set_default_analyzers: No documents found")
            return
        for doc in docs:
            if doc is None:
                continue
            if not self._valide_doc(doc):
                continue
            new_analyser = EsAnalyser(
                name=doc["name"],
                requeries_additionnal_info=doc["requeries_additionnal_info"],
                description=doc["description"],
            )
            if new_analyser is None:
                continue
            self._analyzers[new_analyser.name] = new_analyser

    @staticmethod
    def _valide_doc(doc: dict) -> bool:
        """
        Validate the document.
        :param doc: Document to validate.
        :return: True if the document is valid, False otherwise.
        """
        if doc is None:
            return False
        if "name" not in doc or not doc["name"]:
            return False
        if "requeries_additionnal_info" not in doc or not doc["requeries_additionnal_info"]:
            doc["requeries_additionnal_info"] = False
        if "description" not in doc or not doc["description"]:
            doc["description"] = ""
        return True
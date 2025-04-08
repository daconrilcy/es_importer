class EsAnalyser:
    """
    Class wich define an ElasticSearch Analyser.
    """

    def __init__(self, name: str = None, requeries_additionnal_info: bool = False,
                 description: str = None):
        """
        Initialize the EsAnalyser class.
        :param name: Name of the analyzer.
        :param requeries_additionnal_info: If True, the analyzer will require additional information.
        """
        self._name = name
        self._requeries_additionnal_info = requeries_additionnal_info
        self._description = description

    @property
    def name(self) -> str:
        """
        Get the name of the analyzer.
        :return: Name of the analyzer.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Set the name of the analyzer.
        :param value: Name of the analyzer.
        """
        self._name = value.lower()

    @property
    def requeries_additionnal_info(self) -> bool:
        """
        Get the requeries_additionnal_info of the analyzer.
        :return: requeries_additionnal_info of the analyzer.
        """
        return self._requeries_additionnal_info

    @requeries_additionnal_info.setter
    def requeries_additionnal_info(self, value: bool | str):
        """
        Set the requeries_additionnal_info of the analyzer.
        :param value: requeries_additionnal_info of the analyzer.
        """
        if isinstance(value, str):
            value = value.lower() == "true"
        self._requeries_additionnal_info = value

    @property
    def description(self) -> str:
        """
        Get the description of the analyzer.
        :return: Description of the analyzer.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Set the description of the analyzer.
        :param value: Description of the analyzer.
        """
        self._description = value
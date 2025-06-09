from typing import Union, Optional


class AnalyzerBaseField:
    """
    Classe représentant un champ de configuration pour un analyseur linguistique.
    """

    def __init__(self, doc: Optional[dict] = None) -> None:
        self._name: Optional[str] = None
        self._language: str = 'english'
        self._tokenization: str = 'standard'
        self._stopwords: bool = False
        self._stemming: bool = False
        self._description: str = ''
        if doc:
            self.set_from_doc(doc)

    def set_from_doc(self, doc: dict) -> None:
        """
        Initialise les attributs à partir d'un dictionnaire.
        """
        self.name = doc.get('name')
        self.language = doc.get('language', 'english')
        self.tokenization = doc.get('tokenization', 'standard')
        self.stopwords = doc.get('stopwords', False)
        self.stemming = doc.get('stemming', False)
        self.description = doc.get('description', '')

    @property
    def name(self) -> Optional[str]:
        """Nom de l’analyseur."""
        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self._name = value

    @property
    def language(self) -> str:
        """Langue utilisée pour l’analyse."""
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        self._language = value

    @property
    def tokenization(self) -> str:
        """Méthode de tokenisation utilisée."""
        return self._tokenization

    @tokenization.setter
    def tokenization(self, value: str) -> None:
        self._tokenization = value

    @property
    def stopwords(self) -> bool:
        """Utilisation ou non des stopwords."""
        return self._stopwords

    @stopwords.setter
    def stopwords(self, value: Union[bool, str, int]) -> None:
        self._stopwords = self._to_bool(value)

    @property
    def stemming(self) -> bool:
        """Utilisation ou non du stemming."""
        return self._stemming

    @stemming.setter
    def stemming(self, value: Union[bool, str, int]) -> None:
        self._stemming = self._to_bool(value)

    @property
    def description(self) -> str:
        """Description du champ."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    def to_dict(self) -> dict:
        """
        Retourne une représentation dictionnaire de l’objet.
        """
        return {
            'name': self.name,
            'language': self.language,
            'tokenization': self.tokenization,
            'stopwords': self.stopwords,
            'stemming': self.stemming,
            'description': self.description
        }

    @staticmethod
    def _to_bool(value: Union[str, bool, int, None]) -> bool:
        """
        Convertit un type primitif en booléen selon des conventions souples.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "on", "oui", "tru"}
        return False

    def __str__(self) -> str:
        """
        Retourne une représentation texte de l’objet.
        """
        return (f'AnalyserBaseField(name={self.name}, language={self.language}, '
                f'tokenization={self.tokenization}, stopwords={self.stopwords}, '
                f'stemming={self.stemming}, description={self.description})')

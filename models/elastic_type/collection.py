from models.elastic_type import EsFieldType


class EsTypes:
    """
    Class used to store the types of the fields
    """

    def __init__(self):
        self._types = {}
        self._set_from_es()

    def add_type(self, type_class: EsFieldType):
        """
        Add a type to the types list
        :param type_class:
        :return:
        """
        if type_class is None:
            print("EsTypes.add_type: type_class is None")
            return
        if not isinstance(type_class, EsFieldType):
            print("EsTypes.add_type: type_class is not EsFieldType")
            return
        if type_class.name is None:
            print("EsTypes.add_type: type_class.name is None")
            return
        if type_class.name in self._types:
            print(f"EsTypes.add_type: type_class.name already exists - {type_class.name}")
            return
        self._types[type_class.name] = type_class

    def get_type(self, name) -> EsFieldType | None:
        """
        Get the type by name
        :param name:
        :return:
        """
        return self._types.get(name)

    def all_types(self) -> dict[str, EsFieldType]:
        """
        Get all the types
        :return:
        """
        return self._types

    def list(self) -> list[EsFieldType]:
        """
        Get all the types
        :return:
        """
        list_types = []
        for name, type_class in self._types.items():
            if name is None:
                continue
            if not isinstance(type_class, EsFieldType):
                continue
            list_types.append(type_class)
        return list_types

    def get_type_names(self):
        """
        Get all the type names
        :return: List of type names
        """
        return list(self._types.keys())

    def _set_from_es(self):
        """
        Set the types from Elasticsearch
        :return:
        """
        from elastic_manager import ElasticSearchManager
        es = ElasticSearchManager()
        docs = es.get_es_types()
        self._types = {}
        if docs is None:
            print("EsTypes._set_from_es: No documents found")
            return
        if len(docs) == 0:
            print("EsTypes._set_from_es: No documents found")
            return
        self._set_types_by_doc(docs)

    def _set_types_by_doc(self, docs: list) -> None:
        """
        Initialise les types à partir des documents.
        :param docs: Liste de documents.
        :return: None
        """
        for doc in docs:
            if not doc or not self._valide_doc(doc):
                continue

            try:
                new_type = EsFieldType(
                    name=doc["name"],
                    category=doc["category"],
                    description=doc["description"]
                )
                self._types[new_type.name] = new_type
            except (KeyError, TypeError) as e:
                print(f"Erreur lors de la création du type : {e}")
                continue

    @staticmethod
    def _valide_doc(doc: dict):
        """
        Check if the document is valid
        :param doc: Document to check
        :return: True if the document is valid, False otherwise
        """
        if doc is None:
            return False
        if "name" not in doc or doc["name"] is None:
            return False
        if "category" not in doc or doc["category"] is None:
            return False
        if "description" not in doc or doc["description"] is None:
            return False
        return True

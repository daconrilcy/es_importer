from datetime import datetime, timezone
from typing import Union


class MultiDateFormater:
    """
    Classe utilitaire pour formater des dates
    """

    @staticmethod
    def to_es(value: Union[datetime, str] = None) -> str:
        """
        Formate une date au format ISO 8601 pour l'indexation Elasticsearch.
        :param value: Date au format ISO 8601 ou datetime.datetime
        :return: Date au format ISO 8601
        """

        if value is None:
            value = datetime.now(timezone.utc)

        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError(f"Format de date invalide : {value}")
        elif isinstance(value, datetime):
            dt = value
        else:
            raise TypeError("Le paramètre doit être de type str ou datetime.datetime")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def from_es_to_datetime(value: str) -> datetime:
        """
        convertit une date Elasticsearch en datetime
        :param value:
        :return:
        """
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
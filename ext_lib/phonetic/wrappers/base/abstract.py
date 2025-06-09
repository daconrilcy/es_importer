from abc import ABC, abstractmethod
from typing import List, Union


class BaseWrapperAbstract(ABC):

    @abstractmethod
    def run(self, *args) -> Union[str, List[str]]:
        NotImplementedError("La méthode 'run' doit être implémentée par une sous-classe concrète.")

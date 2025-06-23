from typing import Optional, Dict, Any

from config import Config
from models.mapping_management.request_manager.remplacement_fields_mngnt import RequestRemplacementFieldsManager
from models.mapping_management.request_manager.request_transformer import MappingRequestTransformer
from models.mapping_management.request_manager.request_validator import MappingRequestValidator
import logging

logger = logging.getLogger(__name__)

class MappingRequestManager:
    """
    Manage the validation and transformation of mapping requests.
    Follows SRP: only handles the orchestration between validation and transformation.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize the MappingRequestManager with optional config.
        :param config: Optional configuration object.
        """
        self._config: Config = config or Config()
        self._validator: MappingRequestValidator = MappingRequestValidator()
        self._transformer: MappingRequestTransformer = MappingRequestTransformer(config=self._config)

    def validate_and_transform(self, request: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate the mapping request and transform it if valid.
        :param request: The mapping request dictionary.
        :return: True if transformation succeeds, False otherwise.
        """
        if not request:
            logger.error("MappingRequestManager - La requête est vide.")
            return False
        if self._validator.validate(request):
            try:
                request = RequestRemplacementFieldsManager(self._config).check_modify_request(request)
                return self._transformer.transform(request)
            except ValueError as e:
                logger.error(f"MappingRequestManager - Erreur durant la transformation de la requête : {e}")
                # Log or handle a transformation error (add logging if needed)
                return False
            # except MappingTransformError as e:
            #     # Handle your custom error here
            #     return False
        logger.error("MappingRequestManager - La requête n'est pas valide.")
        return False

    @property
    def transformer(self) -> MappingRequestTransformer:
        """
        Getter for the request transformer.
        :return: The MappingRequestTransformer instance.
        """
        return self._transformer

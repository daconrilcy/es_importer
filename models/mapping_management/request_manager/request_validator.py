import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class MappingRequestValidator:
    """
    Validator for mapping request data structure.
    Ensures that the required keys are present and that the input is valid.
    """

    def __init__(self, required_keys: List[str] | None = None) -> None:
        """
        Initializes the validator with required keys.
        :param required_keys: List of required keys for validation. Defaults to common mapping keys.
        """
        self._required_keys = required_keys or [
            "mapping_name",
            "file_id",
            "encoded_data_filepath",
            "mapping"
        ]

    @property
    def required_keys(self) -> List[str]:
        """
        Getter for the required keys used by the validator.
        :return: List of required key names.
        """
        return self._required_keys

    def validate(self, data: Any) -> bool:
        """
        Validates the provided data against the required structure.
        Logs an error and returns False if validation fails.

        :param data: The data to validate (should be a dictionary).
        :return: True if valid, False otherwise.
        """
        if not data:
            logger.error("MappingRequestValidator: empty data")
            return False

        if not isinstance(data, dict):
            logger.error("MappingRequestValidator: data is not a dict")
            return False

        for key in self._required_keys:
            if key not in data:
                logger.error(
                    "MappingRequestValidator: missing required key '%s'", key
                )
                return False
        return True

import logging

logger = logging.getLogger(__name__)

class MultiUtils:

    @staticmethod
    def sanitaze_string(string: str, lowered=True) -> str:
        """
        Remove special characters from a string.
        :param string: String to sanitize.
        :param lowered: True if the string should be lowered, False otherwise.
        :return: Sanitized string
        """
        if string is None:
            logger.warning("utils - sanitize : String is None.")
            return ""
        result = "".join([c for c in string if c.isalnum() or c in ['.', '_', '-']])
        if lowered:
            return result.lower()
        return result

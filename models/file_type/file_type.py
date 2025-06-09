from pathlib import Path
from typing import Optional, Dict, List


class FileType:
    """
    Represents a file type with configuration for name, extensions, path, and description.
    """

    def __init__(self, doc: Optional[Dict] = None):
        self._name: Optional[str] = None
        self._accepted_extensions: Optional[List[str]] = None
        self._description: Optional[str] = None
        self._base_path: Optional[str] = None

        if doc:
            self.set_from_doc(doc)

    @property
    def name(self) -> Optional[str]:
        """Get the file type's name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def accepted_extensions(self) -> List[str]:
        """Get the list of accepted file extensions."""
        return self._accepted_extensions or []

    @accepted_extensions.setter
    def accepted_extensions(self, value: List[str]) -> None:
        self._accepted_extensions = value

    @property
    def accepted_extensions_str(self) -> str:
        """Get the accepted extensions as a comma-separated string (e.g., '.jpg,.png')."""
        return ",".join(f".{ext}" for ext in self.accepted_extensions)

    @property
    def folder_path(self) -> Optional[Path]:
        """Get the full path of the folder associated with this file type."""
        if self._base_path and self._name:
            return Path(self._base_path) / self._name
        return None

    @property
    def description(self) -> Optional[str]:
        """Get the description of the file type."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    def set_from_doc(self, doc: Dict) -> None:
        """Initialize the file type's attributes from a configuration dictionary."""
        required_keys = ["name", "accepted_extensions", "base_path"]
        self._validate_required_keys(doc, required_keys)

        self.name = doc["name"]
        self.accepted_extensions = doc.get("accepted_extensions", [])
        self._base_path = doc.get("base_path")
        self.description = doc.get("description", "")

    @staticmethod
    def _validate_required_keys(doc: Dict, keys: List[str]) -> None:
        """Validate that all required keys are present in the dictionary."""
        missing = [key for key in keys if key not in doc]
        if missing:
            raise ValueError(f"Missing keys in configuration: {', '.join(missing)}")

    def __eq__(self, other: object) -> bool:
        """Check if another FileType instance has the same name (case-insensitive)."""
        if not isinstance(other, FileType):
            return False
        return (self.name or "").lower() == (other.name or "").lower()

    def __str__(self) -> str:
        """Return a string representation of the FileType instance."""
        return (
            f"FileType(name={self.name}, extensions={self.accepted_extensions}, "
            f"folder_path={self.folder_path}, description={self.description})"
        )

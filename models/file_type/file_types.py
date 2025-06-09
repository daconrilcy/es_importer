import json
from pathlib import Path
from typing import Optional, Sequence
from .file_type import FileType


class FileTypes:
    """
    Container for categorized file types loaded from a JSON config.
    Provides access to types by name and exposes known categories.
    """

    def __init__(self, config_file_path: Optional[str] = None,
                 base_folder_path: Optional[str] = None) -> None:
        self._file_types: dict[str, FileType] = {}
        self._list: list[FileType] = []

        if config_file_path and base_folder_path:
            self._load_file_types(Path(config_file_path), Path(base_folder_path))

    def _load_file_types(self, config_path: Path, base_path: Path) -> None:
        """Load file types from JSON config and register known types."""
        if not config_path.is_file():
            raise ValueError("Fichier de configuration de types de fichier non valide")
        if not base_path.exists():
            raise ValueError("Le dossier de base n'existe pas")

        with config_path.open(encoding='utf-8') as f:
            file_types_data = json.load(f)

        for doc in file_types_data:
            doc["base_path"] = str(base_path)
            file_type = FileType(doc=doc)
            name = file_type.name.lower()
            self._file_types[name] = file_type
            self._list.append(file_type)

    def get(self, name: str) -> Optional[FileType]:
        """Retrieve a file type by its name (case-insensitive)."""
        return self._file_types.get(name.lower())

    def is_type(self, name: str) -> bool:
        """Check if a file type with the given name exists."""
        return name.lower() in self._file_types

    @property
    def list(self) -> list[FileType]:
        """List of all registered file types."""
        return self._list

    @property
    def list_names(self) -> Sequence[str]:
        """List of all registered file types."""
        return [ft.name for ft in self._list]

    @property
    def datas(self) -> Optional[FileType]:
        """Accessor for the 'datas' file type."""
        return self.get("datas")

    @property
    def mappings(self) -> Optional[FileType]:
        """Accessor for the 'mappings' file type."""
        return self.get("mappings")

    @property
    def importers(self) -> Optional[FileType]:
        """Accessor for the 'importers' file type."""
        return self.get("importers")

    @property
    def processors(self) -> Optional[FileType]:
        """Accessor for the 'processors' file type."""
        return self.get("processors")

    @property
    def bulks(self) -> Optional[FileType]:
        """Accessor for the 'bulks' file type."""
        return self.get("bulks")

    @property
    def completions(self) -> Optional[FileType]:
        """Accessor for the 'completions' file type."""
        return self.get("completions")

    def __str__(self) -> str:
        """String representation of FileTypes."""
        names = ', '.join(ft.name for ft in self._list if ft.name)
        return f"FileTypes([{names}])"

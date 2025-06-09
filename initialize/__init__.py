import logging
from pathlib import Path

from config import Config
from elastic_manager import ElasticManager
from initialize.index_details import IndexDetails
from initialize.initconfigfiles import InitConfigFiles
from initialize.test_file import TestFileFactory
from models.file_management.file_infos import FileInfos
from initialize.scan_folder import ScanFolderTools

logger = logging.getLogger(__name__)


class InitialConfig:
    """
    Orchestrates initialization and indexing for Elasticsearch.
    """

    def __init__(self):
        self.config = Config()
        self.indexes = InitConfigFiles(self.config)
        self.elastic = ElasticManager(self.config)
        self.test_file_factory = TestFileFactory(self.config)
        self.folder_scanner = ScanFolderTools()

    def _ensure_test_csv_exists(self) -> None:
        """
        Ensures the 'test.csv' file exists for initial data.
        """
        test_csv_path = Path(self.config.file_types.datas.folder_path) / "test.csv"
        if not test_csv_path.exists():
            logger.info("📊 'test.csv' not found, creating...")
            self.test_file_factory.create_datas_test_file()

    def _create_and_fill_index(self, index: IndexDetails) -> bool:
        """
        Creates and populates a single Elasticsearch index.
        """
        if not index:
            return False

        created = self.elastic.index.recreate(index.index_name, index.mapping)
        if not created:
            logger.error(f"❌ Failed to create index: {index.index_name}")
            return False

        if not index.datas:
            logger.warning(f"⚠️ No data to import for index: {index.index_name}")
            return True

        imported = self.elastic.tools.bulk_import(index.index_name, index.datas)
        return imported

    def _import_additional_files(self) -> bool:
        """
        Detects and imports new files not yet indexed in Elasticsearch.
        """
        indexed_files = self.elastic.files_obj.get_all()

        folders = []
        for file_type in self.config.file_types.list:
            folders.append(Path(file_type.folder_path))
        missing_files = self.folder_scanner.get_missing_files_by_folder(indexed_files, folders)

        files_to_import = []
        for folder_files in missing_files.values():
            for filepath in folder_files:
                files_to_import.append(FileInfos(doc={
                    "filename": filepath.name,
                    "extension": filepath.suffix,
                    "original_filename": filepath.name,
                    "front_end_filename": filepath.stem,
                    "type": filepath.parent.name
                }))

        if not files_to_import:
            logger.info("📊 No additional files to import.")
            return False

        self.elastic.files_obj.import_file_infos(files_to_import)
        logger.info(f"📊 {len(files_to_import)} new files imported into {self.config.index_files_name}.")
        return True

    def create_all_indexes(self) -> None:
        """
        Creates and fills all required Elasticsearch indexes.
        """
        logger.info("\n*********************** Start Index Creation ************************")

        index_steps = [
            ("Types", self.indexes.index_types, None),
            ("Files", self.indexes.index_files, self._import_additional_files),
            ("ES Types", self.indexes.index_es_types, None),
            ("ES Analysers", self.indexes.index_es_analysers, None),
        ]

        for label, index, post_hook in index_steps:
            success = self._create_and_fill_index(index)
            if success and post_hook:
                success = post_hook()
            logger.info(f"{'📊' if success else '❌'} {label} index {'created' if success else 'not created'}")
            logger.info("***********************************************************")

        logger.info("*************************** End *****************************\n")

    def run(self) -> None:
        """
        Runs the complete initialization routine.
        """
        self._ensure_test_csv_exists()
        self.create_all_indexes()


if __name__ == "__main__":
    ic = InitialConfig()
    ic.run()
    doc_inits = ic.elastic.files_obj.get_all()
    for doc_init in doc_inits:
        print(doc_init)

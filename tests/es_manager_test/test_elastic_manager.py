import unittest
from unittest.mock import patch

from elastic_manager import ElasticManager


class DummyConfig:
    def get_host_str(self):
        return "http://localhost:9200"

    es_username = "elastic"
    es_password = "pass"
    index_files_name = "test_index"


class TestElasticManager(unittest.TestCase):

    @patch("elastic_manager.FileInfosDocuments")
    @patch("elastic_manager.ElasticFileDocuments")
    @patch("elastic_manager.ElasticIndexManager")
    @patch("elastic_manager.ElasticSearchTools")
    def test_initialization(
            self, mock_es_tools, mock_index_manager, mock_file_docs, mock_file_infos
    ):
        config = DummyConfig()
        manager = ElasticManager(config)

        mock_es_tools.assert_called_with(
            host="http://localhost:9200",
            username="elastic",
            password="pass"
        )
        mock_index_manager.assert_called_with(mock_es_tools())
        mock_file_docs.assert_called_with(mock_es_tools(), "test_index")
        mock_file_infos.assert_called_with(mock_es_tools(), "test_index")

        self.assertEqual(manager.config, config)
        self.assertEqual(manager.tools, mock_es_tools())
        self.assertEqual(manager.index, mock_index_manager())
        self.assertEqual(manager.files, mock_file_docs())
        self.assertEqual(manager.files_obj, mock_file_infos())


if __name__ == '__main__':
    unittest.main()

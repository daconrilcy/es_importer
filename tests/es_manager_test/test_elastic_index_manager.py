import unittest
from unittest.mock import MagicMock
from elastic_manager.index_manager import ElasticIndexManager


class TestElasticIndexManager(unittest.TestCase):

    def setUp(self):
        self.mock_tools = MagicMock()
        self.index_manager = ElasticIndexManager(self.mock_tools)

    def test_recreate_index(self):
        self.mock_tools.test_connection.return_value = True
        mock_es = MagicMock()
        mock_es.indices.exists.return_value = True
        self.mock_tools.es_connection.return_value.__enter__.return_value = mock_es
        self.mock_tools.is_index_exist.return_value = True

        result = self.index_manager.recreate_index("index", {"mappings": {}})
        self.assertTrue(result)
        mock_es.indices.delete.assert_called_once()
        mock_es.indices.create.assert_called_once()

    def test_delete_index_exists(self):
        mock_es = MagicMock()
        mock_es.indices.exists.return_value = True
        self.mock_tools.es_connection.return_value.__enter__.return_value = mock_es

        result = self.index_manager.delete_index("index")
        self.assertTrue(result)
        mock_es.indices.delete.assert_called_once()

    def test_delete_index_not_exists(self):
        mock_es = MagicMock()
        mock_es.indices.exists.return_value = False
        self.mock_tools.es_connection.return_value.__enter__.return_value = mock_es

        result = self.index_manager.delete_index("index")
        self.assertFalse(result)

    def test_get_index_mapping(self):
        self.mock_tools.is_index_exist.return_value = True
        self.mock_tools.es_connection.return_value.__enter__.return_value.indices.get.return_value = {"index": {}}
        result = self.index_manager.get_index_mapping("index")
        self.assertEqual(result, {"index": {}})

    def test_get_index_mapping_index_does_not_exist(self):
        self.mock_tools.is_index_exist.return_value = False
        result = self.index_manager.get_index_mapping("index")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

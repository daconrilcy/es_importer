import unittest
from unittest.mock import MagicMock, patch
from elastic_manager.estools import ElasticSearchTools


class TestElasticSearchTools(unittest.TestCase):

    def setUp(self):
        self.tools = ElasticSearchTools("http://localhost:9200", "elastic", "El@sticse@rch2025")
        self.mock_es = MagicMock()
        self.tools._es = self.mock_es
        self.tools.connected = True

    @patch("elastic_manager.estools.Elasticsearch")
    def test_connect(self, mock_es_class):
        self.tools.connected = False
        self.tools._es = None
        self.tools.connect()
        mock_es_class.assert_called_once()

    def test_disconnect(self):
        result = self.tools.disconnect()
        self.assertTrue(result)
        self.assertIsNone(self.tools._es)
        self.assertFalse(self.tools.connected)

    @patch("elastic_manager.estools.Elasticsearch.ping", return_value=True)
    @patch("elastic_manager.estools.Elasticsearch.info", return_value={})
    def test_test_connection_success(self, _, __):
        self.tools.connected = False
        self.assertTrue(self.tools.test_connection())

    def test_is_index_exist(self):
        self.mock_es.indices.exists.return_value = True
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            self.assertTrue(self.tools.is_index_exist("test"))

    def test_search_all(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        self.mock_es.search.return_value = {
            "hits": {"hits": [{"_id": "1", "_source": {"a": 1}}]}
        }
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            results = self.tools.search_all("index")
            self.assertEqual(results[0]["a"], 1)

    def test_search_by_query(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        self.mock_es.search.return_value = {
            "hits": {"hits": [{"_id": "1", "_source": {"a": 2}}]}
        }
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            results = self.tools.search_by_query("index", {})
            self.assertEqual(results[0]["a"], 2)

    def test_get_doc_by_id(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        self.mock_es.get.return_value = {"_id": "1", "_source": {"field": "val"}}
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            result = self.tools.get_doc_by_id("index", "1")
        self.assertEqual(result["_id"], "1")

    def test_delete_doc(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            result = self.tools.delete_doc("index", "doc")
            self.assertTrue(result)

    def test_update_property(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            result = self.tools.update_property("index", ["id1"], "status", "done")
            self.assertTrue(result)

    def test_add_doc(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            result = self.tools.add_doc("index", {"field": "val"})
            self.assertTrue(result)

    def test_bulk_import(self):
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            result = self.tools.bulk_import("index", [{"field": "value"}])
            self.assertTrue(result)

    def test_update_doc(self):
        self.tools.is_index_exist = MagicMock(return_value=True)
        with patch.object(self.tools, 'es_connection') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = self.mock_es
            result = self.tools.update_doc("index", "doc", {"field": "new"})
            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

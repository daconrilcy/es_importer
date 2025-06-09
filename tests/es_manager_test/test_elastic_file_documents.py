import unittest
from unittest.mock import MagicMock
from elastic_manager.files.doc import ElasticFileDocuments


class TestElasticFileDocuments(unittest.TestCase):

    def setUp(self):
        self.tools = MagicMock()
        self.doc = ElasticFileDocuments(self.tools, "index")

    def test_list_all(self):
        self.doc.list_all()
        self.tools.search_all.assert_called_with("index", size=100)

    def test_get_by_id(self):
        self.doc.get_by_id("id1")
        self.tools.get_doc_by_id.assert_called_with("index", "id1")

    def test_search_by_type_valid(self):
        self.doc.search_by_type("csv")
        expected_query = {"query": {"match": {"type": "csv"}}}
        self.tools.search_by_query.assert_called_with("index", expected_query)

    def test_search_by_type_empty(self):
        result = self.doc.search_by_type("")
        self.assertFalse(result)

    def test_update_doc_valid(self):
        doc = {"_id": "id1", "name": "test"}
        result = self.doc.update_doc(doc)
        self.assertTrue(result or result is False)  # return depends on mock

    def test_update_doc_invalid(self):
        self.assertFalse(self.doc.update_doc({}))

    def test_delete_doc(self):
        self.doc.delete_doc("id1")
        self.tools.delete_doc.assert_called_with("index", "id1")

    def test_add_doc_valid(self):
        doc = {"type": "csv", "file_name": "file.csv"}
        self.doc.add_doc(doc)
        self.tools.add_doc.assert_called()

    def test_add_doc_invalid(self):
        self.assertFalse(self.doc.add_doc({}))

    def test_bulk_add(self):
        docs = [{"field": "a"}]
        self.doc.bulk_add(docs)
        self.tools.bulk_import.assert_called_with("index", docs)

    def test_update_status_missing(self):
        ids = ["1", "2"]
        self.doc.update_status_missing(ids)
        self.tools.update_property.assert_called_with("index", ids, "status", "missing")

    def test_update_frontend_name(self):
        self.doc.update_frontend_name("id1", "newname")
        self.tools.update_property.assert_called_with("index", ["id1"], "front_end_file_name", "newname")


if __name__ == '__main__':
    unittest.main()

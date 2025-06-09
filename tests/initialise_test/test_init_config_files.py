import unittest
from unittest.mock import MagicMock, patch

from initialize.initconfigfiles import InitConfigFiles


class TestInitConfigFiles(unittest.TestCase):

    @patch("initialize.initconfigfiles.Config")
    @patch("initialize.initconfigfiles.InfosFileReader")
    @patch("initialize.initconfigfiles.IndexDetailsBuilder")
    def test_initialization_loads_all_indexes(self, mock_builder_class, mock_reader_class, mock_config_class):
        # Mock config
        mock_config = MagicMock()
        mock_config.es_init_infos = "dummy_infos_path"
        mock_config.config_folder = "dummy_folder"
        mock_config.index_files_name = "index_files"
        mock_config.index_files_type_name = "index_types"
        mock_config.index_es_types_name = "index_es_types"
        mock_config.index_es_analysers_name = "index_es_analysers"
        mock_config_class.return_value = mock_config

        # Mock InfosFileReader
        mock_reader = MagicMock()
        mock_reader.get.side_effect = lambda key: {"index_name": f"{key}_index", "mapping_file": "map.json",
                                                   "datas_file": "data.json"}
        mock_reader_class.return_value = mock_reader

        # Mock IndexDetailsBuilder
        mock_detail = MagicMock(name="IndexDetails")
        mock_builder = MagicMock()
        mock_builder.build.return_value = mock_detail
        mock_builder_class.return_value = mock_builder

        # Test InitConfigFiles
        config_loader = InitConfigFiles()

        # Assertions : chaque clé appelée
        self.assertEqual(config_loader.index_files, mock_detail)
        self.assertEqual(config_loader.index_types, mock_detail)
        self.assertEqual(config_loader.index_es_types, mock_detail)
        self.assertEqual(config_loader.index_es_analysers, mock_detail)

        expected_keys = [
            mock_config.index_files_name,
            mock_config.index_files_type_name,
            mock_config.index_es_types_name,
            mock_config.index_es_analysers_name,
        ]
        self.assertEqual(mock_reader.get.call_count, 4)
        mock_reader.get.assert_has_calls([unittest.mock.call(k) for k in expected_keys])
        self.assertEqual(mock_builder.build.call_count, 4)


if __name__ == "__main__":
    unittest.main()

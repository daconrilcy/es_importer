"""
Script d'exécution unifiée des tests unitaires, dans l’ordre recommandé.
À lancer depuis la racine avec : `python -m tests`
"""

import unittest


def run_all_tests():
    loader = unittest.TestLoader()

    ordered_modules = [
        "test_scan_folder_tools",
        "test_infos_file_reader",
        "test_test_file_factory",
        "test_index_details",
        "test_index_details_builder",
        "test_init_config_files",
        "_test_initial_config"
    ]

    suite = unittest.TestSuite()
    for module_name in ordered_modules:
        suite.addTests(loader.loadTestsFromName(module_name))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_all_tests()

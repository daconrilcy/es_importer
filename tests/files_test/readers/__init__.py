"""
Script d'exécution unifiée des tests unitaires, dans l’ordre recommandé.
À lancer depuis la racine avec : `python -m tests`
"""

import unittest


def run_all_tests():
    loader = unittest.TestLoader()

    ordered_modules = [
        "test_csv_file_reader",
        "test_text_file_reader",
    ]

    suite = unittest.TestSuite()
    for module_name in ordered_modules:
        suite.addTests(loader.loadTestsFromName(module_name))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    run_all_tests()

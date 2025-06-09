import csv
from pathlib import Path

from config import Config


class TestFileFactory:
    def __init__(self, config: Config):
        self.config = config

    def create_datas_test_file(self):
        """
        Create the test.csv file for datas
        :param self:
        :return:
        """
        try:
            filepath = Path(self.config.file_types.datas.folder_path) / "test.csv"
            with filepath.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "name", "type", "size", "path", "date"])
                writer.writerow(["1", "test", "txt", "100", "C:/test", "2021-01-01"])
                writer.writerow(["2", "test2", "csv", "200", "C:/test2", "2021-01-02"])
                writer.writerow(["3", "test3", "json", "300", "C:/test3", "2021-01-03"])
                writer.writerow(["4", "test4", "xml", "400", "C:/test4", "2021-01-04"])
                writer.writerow(["5", "test5", "yaml", "500", "C:/test5", "2021-01-05"])
            print(f"📊 test.csv file created in {filepath}")
            return True
        except Exception as e:
            print(f"❌ CsvReader.get_separator_from_filepath: erreur lors de la lecture du fichier → {e}")
            return False
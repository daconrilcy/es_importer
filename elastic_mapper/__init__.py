import os

import pandas as pd
import secrets
import glob

from config import Config
from elastic_mapper.EsMappingProperty import EsMappingProperty
from models.elastic_type import EsFieldType
from utils import safe_load_csv, is_file_in_folder, sanitaze_string


class EsMapper:
    """
    ElasticSearch mapper class.
    list_properties: list of EsMappingProperty objects
    types_fields: list of EsFieldType objects created from the reference file
    config: Config object containing the configuration of the application based on the .env file
    """

    def __init__(self, config: Config):
        self._config = config
        self.list_properties = []
        self._types_fields = []
        self._list_sources_fields_properties = []
        self._set_types_fields_from_ref_file()
        self.temp_filepath = None
        self.bulk_doc = None

    @property
    def list_properties(self) -> list[EsMappingProperty]:
        """
        Get the list of properties.
        :return:
        """
        return self._list_properties

    @list_properties.setter
    def list_properties(self, value: list[EsMappingProperty]) -> None:
        self._list_properties = value
        self._set_sourcefields_properties_list()

    def set_list_properties_from_df(self, properties_df: pd.DataFrame) -> None:
        """
        Set the list of properties from a DataFrame.
        :param properties_df:
        :return: None
        """
        if properties_df is None:
            print("EsMapper - set_list_properties_from_df - Mapping non chargé Pas de DataFrame.")
            return
        if len(properties_df) == 0:
            print("EsMapper - set_list_properties_from_df - Mapping non chargé DataFrame vide.")
            return
        self.list_properties = []
        self._list_sources_fields_properties = []

        property_to_add = EsMappingProperty(fields_types=self.types_fields)
        headers_df = properties_df.columns
        if not property_to_add.check_fields_struct(headers_df):
            print("EsMapper - Mapping non chargé Les colonnes du fichier ne sont pas correctes.")
            return
        for _, row in properties_df.iterrows():
            # Reset the property => create a new one
            property_to_add = EsMappingProperty(fields_types=self.types_fields, row=row)
            if property_to_add is None:
                continue
            if property_to_add.to_map:
                self.add_property(property_to_add)
        self._set_sourcefields_properties_list()

    def add_property(self, property_to_add: EsMappingProperty) -> None:
        """
        Add a property to the list of properties.
        :param property_to_add:
        :return:
        """
        if property_to_add is None:
            return
        self.list_properties.append(property_to_add)

    @property
    def types_fields(self) -> list[EsFieldType]:
        """
        Get the types fields.
        :return:
        """
        return self._types_fields

    def _set_types_fields_from_ref_file(self) -> None:
        """
        Set the types fields from a DataFrame.
        :return:None
        """
        self._types_fields = []
        types_df = safe_load_csv(self._config.es_types_file_path)
        if types_df is None:
            print("EsMapper - Impossible de charger le fichier des types.")
            return
        for _, row in types_df.iterrows():
            field = EsFieldType()
            field.set_from_df_row(row)
            self.types_fields.append(field)

    @property
    def list_sources_fields_properties(self) -> list[str]:
        """
        Get the list of source fields properties.
        :return:
        """
        return self._list_sources_fields_properties

    def _set_sourcefields_properties_list(self) -> None:
        """
        Set the source fields properties list from the list of properties.
        :return:
        """
        self._list_sources_fields_properties = []

        for prop in self.list_properties:
            if prop is None:
                continue
            if prop.to_map:
                self._list_sources_fields_properties.append(prop.source_field)

    def set_properties_from_mapping_file(self, mapper_filename: str) -> None:
        """
        Set the mapper from a file.
        :param mapper_filename:
        :return:
        """
        if not is_file_in_folder(mapper_filename, self._config.mapping_folder):
            print(f"EsMapper - Le fichier {mapper_filename} n'existe pas dans le folder des mappers.")
            return
        mapper_file_path = self._config.mapping_folder + mapper_filename
        mapper_df = safe_load_csv(mapper_file_path)
        self.set_list_properties_from_df(mapper_df)

    def set_sourcefields_with_default_mapping_from_datas_df(self, dataset_df: pd.DataFrame) -> list[EsMappingProperty]:
        """
        Get the source fields with the default mapping from a datas in DataFrame.
        :param dataset_df:
        :return: list of EsMappingProperty
        """
        fields_to_map = []
        if dataset_df is None:
            print("EsMapper - Pas de DataFrame pour le mapping.")
            return fields_to_map

        for col in dataset_df.columns:
            if col is None:
                continue
            field = EsMappingProperty(self.types_fields)
            field.source_field = col
            field.name = sanitaze_string(col)
            field.to_map = True
            field.type = field.set_type_by_name("text")
            fields_to_map.append(field)

        self.list_properties = fields_to_map

        return fields_to_map

    def set_sourcefields_with_default_mapping_from_datas_file(self, filename: str) -> list[EsMappingProperty]:
        """
        Get the source fields with the default mapping from a datas in a file.
        :param filename:
        :return:
        """
        if filename is None:
            print("EsMapper - Pas de fichier pour le mapping.")
            return []
        if filename == "":
            print("EsMapper - Pas de fichier pour le mapping.")
            return []
        if not is_file_in_folder(filename, self._config.data_folder):
            print(f"EsMapper - Le fichier {filename} n'existe pas dans le folder des datas.")
            return []
        file_path = self._config.data_folder + filename
        dataset_df = safe_load_csv(file_path)
        return self.set_sourcefields_with_default_mapping_from_datas_df(dataset_df)

    def get_doc(self) -> dict:
        """
        Get the document.
        :return: dict : document elasticsearch mapping
        """
        doc = {}
        if self.list_properties is None:
            print("EsMapper - No properties to map.")
            return doc
        if len(self.list_properties) == 0:
            print("EsMapper - No properties to map.")
            return doc
        for prop in self.list_properties:
            if prop is None:
                continue
            else:
                if prop.to_map:
                    if prop.type is None:
                        print(f"EsMapper - No type for the property {prop.name}.")
                        continue
                    doc[prop.name] = {"type": prop.type.name}
                    if prop.has_analyzer:
                        doc[prop.name]["analyzer"] = prop.analyzer
        return doc

    def get_mapped_datas_from_df(self, datas: pd.DataFrame) -> pd.DataFrame:
        """
        Get the mapped datas from a DataFrame.
        :param datas:
        :return:
        """
        if datas is None:
            print("EsMapper - No datas to map.")
            return pd.DataFrame()
        if len(datas) == 0:
            print("EsMapper - No datas to map.")
            return pd.DataFrame()
        if self.list_properties is None:
            print("EsMapper - No properties to map.")
            return pd.DataFrame()
        if len(self.list_properties) == 0:
            print("EsMapper - No properties to map.")
            return pd.DataFrame()
        headers = datas.columns
        if not self._check_headers(headers):
            return datas
        return datas[self._list_sources_fields_properties]

    def set_mapped_datas_temp_from_file(self, filename: str, sep: str = None) -> str or None:
        """
        Get the mapped datas from a file.
        Filtered datas are saved in a Temp file.
        :param filename:
        :param sep: Separator of the file.
        :return: str : filepath of Temp file.
        """
        if sep is None:
            sep = self._config.default_sep
        self.temp_filepath = None
        if filename is None:
            print("EsMapper - get_mapped_datas_from_file - No file to map.")
        elif filename == "":
            print("EsMapper - get_mapped_datas_from_file - No file to map.")
        elif not is_file_in_folder(filename, self._config.data_folder):
            print(f"EsMapper - get_mapped_datas_from_file - "
                  f"Le fichier {filename} n'existe pas dans le folder des datas.")
        else:
            file_path = self._config.data_folder + filename
            start_with = "filtered_datas_"
            self._delete_temp_mapping_files(start_with)
            self.temp_filepath = self._config.temp_folder + start_with + secrets.token_hex(8) + ".csv"
            try:
                datas_chunk = pd.read_csv(file_path, chunksize=self._config.chunksize, sep=sep)
                for chunk in datas_chunk:
                    if chunk is None:
                        continue
                    mapped_chunk = self.get_mapped_datas_from_df(chunk)
                    mapped_chunk.to_csv(self.temp_filepath, mode='a', index=False, sep=",")
            except Exception as e:
                print(f"EsMapper - get_mapped_datas_from_file - Erreur lors de la lecture du fichier : {e}")
                return self.temp_filepath
        return self.temp_filepath

    def _check_headers(self, headers: list[str]) -> bool:
        """
        Check if the headers are correct.
        :param headers:
        :return:
        """
        if headers is None:
            print("EsMapper - check_headers - No headers.")
            return False
        if len(headers) == 0:
            print("EsMapper - check_headers - No headers.")
            return False
        if self._list_sources_fields_properties is None:
            print("EsMapper - check_headers - No source fields properties.")
            return False
        for sc_field in self._list_sources_fields_properties:
            if sc_field is not None:
                if sc_field not in headers:
                    print(f"EsMapper - check_headers - The source field {sc_field} is not in the headers of datas.")
                    return False
        return True

    def _delete_temp_mapping_files(self, start_with: str = "filtered") -> None:
        """
        Delete the temp mapping files.
        :return: None
        """
        start_with = start_with + "*" if start_with[-1] != "*" else start_with
        # Récupérer tous les fichiers commençant par 'filtered'
        files_to_delete = glob.glob(os.path.join(self._config.temp_folder, start_with))
        if len(files_to_delete) > 0:
            # Supprimer chaque fichier
            deleted_files = []
            for file in files_to_delete:
                os.remove(file)
                deleted_files.append(file)
            print(f"EsMapper - {len(deleted_files)} Fichiers temporaires supprimés : {deleted_files}")

    def set_bulk_doc(self) -> str or None:
        """
        Set the bulks doc.
        :return: str : filepath of bulkdoc file.
        """
        if self.temp_filepath is None:
            print("EsMapper - set_bulk_doc - No temp file.")
            return
        if not os.path.exists(self.temp_filepath):
            print(f"EsMapper - set_bulk_doc - Le fichier {self.temp_filepath} n'existe pas dans le folder des datas.")
            return
        self.bulk_doc = None
        bulk_doc_file_name = "bulk_doc_" + secrets.token_hex(8) + ".json"
        bulk_doc_file_path = self._config.bulk_folder + bulk_doc_file_name
        self.bulk_doc = bulk_doc_file_path
        bulk_doc = []
        datas_chunk = pd.read_csv(self.temp_filepath, chunksize=self._config.chunksize)
        for chunk in datas_chunk:
            if chunk is None:
                continue
            for _, row in chunk.iterrows():
                doc = {}
                for prop in self.list_properties:
                    if prop is None:
                        continue
                    if prop.to_map:
                        if prop.source_field in row:
                            doc[prop.name] = row[prop.source_field]
                    bulk_doc.append(doc)
            with open(bulk_doc_file_path, 'a') as file:
                file.write(str(bulk_doc))
        return self.bulk_doc


if __name__ == "__main__":
    config_test = Config()
    mapper_test = EsMapper(config_test)
    mapper_test.set_properties_from_mapping_file("mapping_pays.csv")
    for prop_test in mapper_test.list_properties:
        print(prop_test)
    for sc_field_test in mapper_test.list_sources_fields_properties:
        print(sc_field_test)
    print(mapper_test.get_doc())
    mapper_test.set_mapped_datas_temp_from_file("curiexplore-pays.csv", ";")
    print(mapper_test.set_bulk_doc())

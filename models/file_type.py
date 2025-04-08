import os

from config import Config


class FileType:
    """
    Define a file type : datas, mappings, importers, processors, bulks
    """

    def __init__(self, doc: dict = None, config: Config = None):
        if config is None:
            config = Config()
        self._name = None
        self._accepted_extensions = None
        self._description = None
        self._folder_path = None
        self._url = None
        self._description = None
        self._base_layout = None
        self._html_preview_layout = None
        self._base_path = config.root_folder
        self._base_templates_folder = config.base_template_files_folder
        self._base_template_preview_folder = config.base_template_files_preview_folder
        self._method_preview = None
        self._id_div_preview = None
        if doc is not None:
            self.set_from_doc(doc)

    @property
    def name(self) -> str:
        """
        Get the name of the file type
        :return: Name of the file type
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Set the name of the file type
        :param value: Name of the file type
        """
        self._name = value

    @property
    def accepted_extensions(self) -> list[str]:
        """
        Get the accepted extensions
        :return: List of accepted extensions
        """
        return self._accepted_extensions

    @accepted_extensions.setter
    def accepted_extensions(self, value: list[str]):
        """
        Set the accepted extensions
        :param value: List of accepted extensions
        """
        self._accepted_extensions = value

    @property
    def accepted_extensions_str(self) -> str:
        """
        Get the accepted extensions
        :return: List of accepted extensions
        """
        if self._accepted_extensions is None:
            return ""
        final_str = ""
        for ext in self._accepted_extensions:
            final_str += f".{ext},"
        final_str = final_str[:-1]
        return final_str

    @property
    def folder_path(self) -> str | None:
        """
        Get the folder name
        :return: Folder name
        """
        if self._folder_path is None:
            return None
        self._folder_path.replace("/", os.sep)
        return os.path.join(self._base_path, self._folder_path)

    @folder_path.setter
    def folder_path(self, value: str):
        """
        Set the folder name
        :param value: Folder name
        """
        self._folder_path = value

    @property
    def url(self) -> str:
        """
        Get the url
        :return: Url
        """
        return self._url

    @url.setter
    def url(self, value: str):
        """
        Set the url
        :param value: Url
        """
        self._url = value

    @property
    def description(self) -> str:
        """
        Get the description of the file type
        :return: Description of the file type
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Set the description of the file type
        :param value: Description of the file type
        """
        self._description = value

    @property
    def base_layout(self) -> str:
        """
        get the html layout for the landing page of this type
        :return:
        """
        return self._base_layout

    @base_layout.setter
    def base_layout(self, value: str):
        """
        set the base layout name for the landing page
        :param value:
        :return:
        """
        self._base_layout = value

    @property
    def html_preview_layout(self) -> str:
        """
        Get the html layout
        :return: Html layout
        """
        return self._html_preview_layout

    @html_preview_layout.setter
    def html_preview_layout(self, value: str):
        """
        Set the html layout
        :param value: Html layout
        """
        self._html_preview_layout = value

    @property
    def method_preview(self) -> str:
        """
        :return: type of previewer
        """
        return self._method_preview

    @method_preview.setter
    def method_preview(self, method_preview: str):
        """
        set the method preview
        :param method_preview:
        :return: None
        """
        self._method_preview = method_preview

    @property
    def id_div_preview(self):
        """
        get id of the div preview
        :return:
        """
        if self._id_div_preview is None or self._id_div_preview == "":
            self._id_div_preview = self._set_default_id_div_preview()
        return self._id_div_preview

    @id_div_preview.setter
    def id_div_preview(self, value: str):
        """
        set id of div file preview
        :param value:
        :return:
        """
        if value is None or value == "":
            value = self._set_default_id_div_preview()
        self._id_div_preview = value

    def _set_default_id_div_preview(self):
        return f"preview-{self.name}-container"

    def set_from_doc(self, doc: dict) -> None:
        """
        Set the file type from a document
        :param doc: Document
        """
        if not doc or "name" not in doc or "accepted_extensions" not in doc:
            print("❌ FileType.set_from_doc: Invalid document")
            return

        self.name = doc["name"]
        self.accepted_extensions = doc.get("accepted_extensions", [])
        self.folder_path = doc.get("folder_path", "")
        self.url = doc.get("url", "")
        self.description = doc.get("description", "")
        self.html_preview_layout = self._base_template_preview_folder + doc.get("html_preview_layout", "")
        self.method_preview = doc.get("method_preview", "")
        self.base_layout = self._base_templates_folder + doc.get("base_layout", "")
        self.id_div_preview = self._set_default_id_div_preview()

    def compare(self, file_type) -> bool:
        """
        Compare the file type with the list
        :param file_type: File type
        :return: True if the file type is in the list
        """
        if file_type is None or not isinstance(file_type, FileType):
            return False

        own_name = self.name.lower()
        other_name = file_type.name.lower()
        if own_name != other_name:
            return False

        return True

    def __str__(self):
        return (f"FileType({self.name}, {self.accepted_extensions}, {self.folder_path}, {self.url}, "
                f"{self.html_preview_layout}, {self.method_preview}, {self.description})")


class FileTypes:
    """
    Define the file types : datas, mappings, importers, processors, bulks
    """

    def __init__(self):
        self._datas = None
        self._mappings = None
        self._importers = None
        self._processors = None
        self._bulks = None
        self._excluded = ["_list", "_set_initial_file_types_list"]
        self._list = []
        self._set_initial_file_types_list()

    @property
    def datas(self) -> FileType:
        """
        Get the datas file type
        :return: Datas file type
        """
        return self._datas

    @property
    def mappings(self) -> FileType:
        """
        Get the mappings file type
        :return: Mappings file type
        """
        return self._mappings

    @property
    def importers(self) -> FileType:
        """
        Get the importers file type
        :return: Importers file type
        """
        return self._importers

    @property
    def processors(self) -> FileType:
        """
        Get the processors file type
        :return: Processors file type
        """
        return self._processors

    @property
    def bulks(self) -> FileType:
        """
        Get the bulks file type
        :return: Bulks file type
        """
        return self._bulks

    @property
    def list(self) -> list[FileType]:
        """
        Get the list of file types
        :return: List of file types
        """
        return self._list

    def _set_initial_file_types_list(self):
        """
        Set the initial list of file types
        """
        self._list = []
        from config import Config
        from elastic_manager import ElasticSearchManager
        files_types = ElasticSearchManager(Config()).get_files_types_from_es()
        for ft in files_types:
            temp_ft = FileType(ft)
            if self._attr_names_comparator(temp_ft.name):
                attr_name = "_" + temp_ft.name
                setattr(self, attr_name, temp_ft)
                self._list.append(self.__dict__.get(attr_name))

    def is_type(self, file_type: str) -> bool:
        """
        Check if the file type is in the list
        :param file_type: File type
        :return: True if the file type is in the list
        """
        for ft in self.list:
            if ft.name.lower() == file_type.lower():
                return True
        return False

    def _attr_names_comparator(self, name_type: str) -> bool:
        """
        Compare the attribute name with the excluded attributes
        :param name_type: Attribute name
        :return: True if the attribute is not excluded
        """
        for attr in self.__dict__.keys():
            attr_clean = attr.replace("_", "")
            if attr_clean in self._excluded or attr in self._excluded:
                return False
            if attr_clean == name_type or attr == name_type:
                return True
        return False

    def get_file_type_by_name(self, name: str) -> FileType | None:
        """
        Get the file type by its name
        :param name: Name of the file type
        :return: File type
        """
        for file_type in self.list:
            if file_type.name == name:
                return file_type
        return None

    def get_file_type_by_folder(self, folder_path: str) -> FileType | None:
        """
        Get the file type by its folder path
        :param folder_path: Folder path
        :return: File type
        """
        if folder_path is None:
            return None
        folder_path = folder_path.replace("/", os.sep)
        folder_path = folder_path.replace("\\", os.sep)
        if folder_path[-1] == os.sep:
            folder_path = folder_path[:-1]
        for file_type in self.list:
            if file_type.folder_path == folder_path:
                return file_type
        return None

    def __str__(self):
        return f"FileTypes({self.list})"


if __name__ == "__main__":
    # Attention: Les indexes de bases doivent etre peuplés pour que ce test fonctionne
    from elastic_manager import ElasticSearchManager
    from config import Config

    esg_test = ElasticSearchManager(Config())
    docs_files = esg_test.get_files_types_from_es()
    for df in docs_files:
        print(df)
        ft_test = FileType(df)
        print(ft_test)
        print(ft_test.folder_path)

    fts_test = FileTypes()
    print(fts_test.datas)
    for ftl_test in fts_test.list:
        print(ftl_test)
    print(fts_test.is_type("datas"))
    print(fts_test.get_file_type_by_name("mappings"))

class CsvDataPreview:
    """
    A class to preview CSV data in a structured format.
    for handling CSV data previewing in html.
    """

    def __init__(self, datas: dict,
                 front_name: str = None,
                 filename: str = None,
                 file_id: str = None,
                 file_type: str = "datas"
                 ):
        self.file_type = file_type
        self.file_id = file_id
        self.front_name = front_name
        self.filename = filename
        self.datas_dict = datas
        self.sep = datas.get("sep", ",")
        self.headers = datas.get("headers", [])
        self.first_three_rows = datas.get("first_three_rows", [])
        self.last_three_rows = datas.get("last_three_rows", [])

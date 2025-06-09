from werkzeug.datastructures import FileStorage

from config import Config
from models.file_management.file_utls import FileUtils
from models.file_management.save_management import UploadedFileSaver
from elastic_manager import ElasticManager
from models.file_management.file_infos import FileInfos


class FileUploader:
    """
    Gère l'upload de fichiers (unitaire ou multiple) pour une API Dropzone-like.
    Délègue la sauvegarde à FileSaver.
    """

    def __init__(self):
        self.file_saver = UploadedFileSaver()
        self.config = Config()

    def handle_upload(self, file: FileStorage, file_type: str) -> dict:
        """
        Gère l'upload d'un fichier unique (Dropzone envoie un fichier par requête).
        Retourne un dict avec les infos utiles pour le front, dont un objet FileInfos.
        """
        if file is None or not file_type:
            return {"success": False, "error": "Aucun fichier ou type non spécifié.", "file_infos": None}

        filetype_obj = self.config.file_types.get(file_type)
        if not filetype_obj:
            return {"success": False, "error": f"Type de fichier inconnu: {file_type}", "file_infos": None}

        success, new_filename, saved_path = self.file_saver.save(file, filetype_obj, file.filename)
        if not success:
            return {"success": False, "error": "Erreur lors de la sauvegarde.", "file_infos": None}

        # Création de FileInfos dès la sauvegarde
        file_doc = {
            "file_name": new_filename,
            "initial_file_name": file.filename,
            "type": filetype_obj.name,
            "extension": new_filename.split(".")[-1] if "." in new_filename else "",
            "separator": ",",  # valeur par défaut, sera ajustée si CSV
            "status": "uploaded"
        }
        file_infos = FileInfos(file_doc)

        # Détection automatique du séparateur si CSV
        if file_infos.extension.lower() == 'csv':
            detected_sep = FileUtils.detect_separator(file_infos.filepath)
            file_infos._separator = detected_sep

        return {
            "success": True,
            "file_infos": file_infos,
            "filepath": saved_path,
            "error": None
        }

    def handle_batch_upload(self, files: list[FileStorage], file_type: str) -> list[dict]:
        """
        Gère l'upload de plusieurs fichiers (batch Dropzone).
        Retourne une liste de dicts de résultats.
        """
        return [self.handle_upload(f, file_type) for f in files if f is not None]

    def upload_and_index_file(self, file: FileStorage, file_type: str) -> dict:
        """
        Gère l'upload, la création de FileInfos, l'indexation ES et retourne le dict FileInfos.
        """
        upload_result = self.handle_upload(file, file_type)
        if not upload_result["success"]:
            return {"success": False, "error": upload_result["error"]}

        file_infos = upload_result["file_infos"]
        es_manager = ElasticManager(self.config)
        self.add_file_to_index(file_infos, es_manager)

        # On retourne les infos de FileInfos via ses propriétés
        return {
            "success": True,
            "file_name": file_infos.file_name,
            "initial_file_name": file_infos.initial_file_name,
            "type": file_infos.type,
            "extension": file_infos.extension,
            "separator": file_infos.separator,
            "status": file_infos.status,
            "filepath": file_infos.filepath
        }

    def add_file_to_index(self, file_infos: FileInfos, es_manager: ElasticManager = None) -> bool:
        """
        Indexe un fichier dans Elasticsearch via ElasticSearchManager.
        """
        es_manager = es_manager or ElasticManager(self.config)
        return es_manager.files_obj.add(file_infos)


if __name__ == "__main__":
    from werkzeug.datastructures import FileStorage
    from io import BytesIO
    import os

    # Préparation d'un faux fichier à uploader
    content = b"col1,col2\nval1,val2\nval3,val4"
    file_stream = BytesIO(content)
    file_storage = FileStorage(
        stream=file_stream,
        filename="demo.csv",
        content_type="text/csv"
    )

    file_type_name = "datas"  # Adapter selon ta config FileTypes

    uploader = FileUploader()
    result = uploader.upload_and_index_file(file_storage, file_type_name)

    print("--- Démonstration FileUploader avec indexation ES ---")
    print(result)
    if result.get("success") and result.get("filepath") and os.path.exists(result["filepath"]):
        print(f"Le fichier a bien été sauvegardé à : {result['filepath']}")
        os.remove(result["filepath"])
        print("Fichier de démo supprimé.")
    else:
        print("La sauvegarde ou l'indexation a échoué.")

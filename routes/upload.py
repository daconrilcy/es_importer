import logging
from flask import request, jsonify, Blueprint
from config import Config
from models.file_management.uploader import FileUploader
from routes.renderer import render_page

logger = logging.getLogger(__name__)
config = Config()

upload_road = Blueprint("upload_road", __name__)

@upload_road.route('/dropzone-upload', methods=['POST'])
def dropzone_upload():
    """
    Route d'upload compatible Dropzone (un fichier par requête).
    Retourne un JSON avec le résultat de l'upload (upload, FileInfos, indexation ES, séparateur auto).
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Aucun fichier envoyé."}), 400
    file = request.files['file']
    file_type = request.form.get('filetype')
    if not file_type:
        return jsonify({"success": False, "error": "Type de fichier manquant."}), 400
    uploader = FileUploader()
    result = uploader.upload_and_index_file(file, file_type)
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@upload_road.route('/upload', methods=['GET'])
def upload():
    """
    Page d'upload de fichiers avec Dropzone et sélection du type de fichier.
    """
    return render_page('upload.html', file_types=config.file_types)
from typing import Any, Optional, Dict

from flask import Blueprint, jsonify
import logging

from config import Config
from models.file_management.deleter import FileDeleter
from routes.handle_payload import handle_json_payload

logger = logging.getLogger(__name__)
config = Config()

common_file = Blueprint("common_file", __name__)


def _validate_delete_payload(payload: Optional[Dict]) -> Optional[Dict[str, str]]:
    """
    Valide le payload reçu pour la suppression de fichier.

    Args:
        payload (Optional[Dict]): Le payload JSON reçu.

    Returns:
        Optional[Dict[str, str]]: Dictionnaire avec 'file_id' et/ou 'filename' si valides, sinon None.
    """
    if not payload:
        return None
    file_id = payload.get("file_id")
    filename = payload.get("filename")
    if not file_id and not filename:
        return None
    return {"file_id": file_id, "filename": filename}


@common_file.route("/file/delete/", methods=["POST"])
def delete_file() -> Any:
    """
    Endpoint pour supprimer un fichier selon son file_id ou son filename.

    Returns:
        Flask Response: Réponse JSON avec le statut de la suppression.
    """
    payload = handle_json_payload()
    validated = _validate_delete_payload(payload)
    if not validated:
        logger.error(
            "Requête reçue pour la suppression d'un fichier: "
            "Aucun filename ou id de fichier fourni ou payload JSON invalide"
        )
        return jsonify({"error": "JSON invalide"}), 400

    file_id = validated["file_id"]
    filename = validated["filename"]

    try:
        file_deleter = FileDeleter(config)
        deleted = file_deleter.delete(file_id=file_id, filename=filename)
        if not deleted:
            logger.error("Fichier à supprimer introuvable (file_id=%s, filename=%s)", file_id, filename)
            return jsonify({"error": "Fichier introuvable"}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(
            "Exception inattendue lors de la suppression du fichier: %s", e, exc_info=True
        )
        return jsonify({"error": "Erreur lors de la suppression du fichier"}), 500

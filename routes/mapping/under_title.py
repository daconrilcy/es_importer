# routes/under_title.py

from flask import Blueprint, render_template, abort, request, jsonify, send_from_directory
from typing import Any
from werkzeug.exceptions import BadRequest
import logging
import os

from models.elastic_specifiques import EsTypes, BasicAnalyzers
from models.file_management.completion.empty import MappingCompletionEmptyFileCreator
from models.file_management.completion.phonetic import PhoneticFileCreator
from models.file_management.file_loader import FileLoader
from models.file_management.folder_list.completions import CompletionsFolderList
from models.mapping_management import Mapping
from models.mapping_management.fields_management.creator import FieldsCreator
from config import Config
from routes.handle_payload import handle_json_payload

logger = logging.getLogger(__name__)
config = Config()

# Blueprint pour les routes de mapping "undertitle"
under_title = Blueprint("under_title", __name__)

# Mapping du type vers la template correspondante
_TEMPLATE_MAP = {
    "source": "preview_files/mapping/undertitle/dropmenu/source.html",
    "remplacement": "preview_files/mapping/undertitle/dropmenu/remplacement.html",
    "phonetic": "preview_files/mapping/undertitle/dropmenu/phonetic.html",
    "fixed_value": "preview_files/mapping/undertitle/dropmenu/fixed_value.html",
}


def _render_dropmenu(encode_filepath: str, menu_type: str) -> Any:
    """
    Charge les headers d'un fichier et affiche la bonne template.
    """
    template_path = _TEMPLATE_MAP.get(menu_type)
    if not template_path:
        logger.warning("Type de dropmenu inconnu: %s", menu_type)
        abort(404, f"Type de dropmenu inconnu: {menu_type}")

    file_loader = FileLoader()
    try:
        headers = file_loader.get_file_data_headers(encode_filepath)
    except Exception as exc:
        logger.error("Erreur lors du chargement des headers: %s", exc)
        abort(500, f"Erreur lors du chargement des headers: {exc}")

    return render_template(template_path, list_fields=headers)


@under_title.route("/file/mapping/undertitle/fixed_value", methods=["GET"])
def get_fixed_value_dropmenu() -> Any:
    """
    Renvoie le dropmenu de type "fixed_value".
    """
    return render_template(_TEMPLATE_MAP["fixed_value"])


@under_title.route("/file/mapping/undertitle/<menu_type>/<encode_filepath>", methods=["GET"])
def get_dropmenu(menu_type: str, encode_filepath: str) -> Any:
    """
    Renvoie les headers d'un fichier selon le type de dropmenu.
    """
    return _render_dropmenu(encode_filepath, menu_type)


@under_title.route('/mapping/create/mapping-field', methods=['POST'])
def create_mapping_field() -> Any:
    """
    Crée un mapping field à partir d'un JSON payload.
    Retourne deux snippets HTML (row et details) sous forme de JSON.
    """
    html_details = {
        "remplacement": "preview_files/mapping/rows_modif/row_completion.html",
        "phonetic": "preview_files/mapping/rows_modif/row_phonetic.html",
        "fixed_value": "preview_files/mapping/rows_modif/row_fixed_value.html",
        "source": "preview_files/mapping/rows_modif/row_source_field.html",
    }

    if request.is_json:
        payload = handle_json_payload()
        if not payload:
            return jsonify({"error": "JSON invalide"}), 400
    else:
        return jsonify({"error": "Payload JSON manquante"}), 400

    try:
        field_creator = FieldsCreator(payload, config)
        if not field_creator.is_valid:
            logger.warning("Payload invalide pour la création du mapping field : %s", payload)
            return jsonify({"error": "Payload invalide pour la création du mapping field"}), 400
        details_html_path = html_details.get(field_creator.field.category)
        row_html_path = "preview_files/mapping/row_preview.html"
        es_analysers = BasicAnalyzers(config).fields_names
        es_types = EsTypes(config).fields_names

    except Exception as exc:
        logger.error("Erreur lors de la création du mapping field: %s", exc, exc_info=True)
        return jsonify({"error": "Erreur lors de l'ajout du mapping field"}), 500

    row_html = render_template(row_html_path, field=field_creator.field)
    details_html = render_template(details_html_path, field=field_creator.field,
                                   es_analysers=es_analysers, es_types=es_types)

    return jsonify({
        "row_html": row_html,
        "details_html": details_html
    }), 200


@under_title.route('/file/remplacement/download/<filename>', methods=['GET'])
def download_completion_file(filename: str) -> Any:
    """
    Permet de télécharger un fichier de remplacement.
    """
    file_dir = CompletionsFolderList(config).folder_path
    try:
        # Sécurisation du nom de fichier
        safe_filename = os.path.basename(filename)
        if safe_filename != filename:
            logger.warning("Tentative de téléchargement avec nom de fichier non sécurisé : %s", filename)
            abort(400, "Nom de fichier invalide.")
        return send_from_directory(file_dir, safe_filename, as_attachment=True)
    except FileNotFoundError:
        logger.warning("Fichier non trouvé lors du téléchargement : %s", filename)
        abort(404, "Fichier non trouvé.")


@under_title.route('/file/mapping/remplacement/generate/', methods=['POST'])
def generate_remplacement_file() -> Any:
    """
    Génère un fichier de remplacement à partir d'un JSON.
    """
    logger.info("Requête reçue pour générer un fichier de remplacement.")
    try:
        payload = handle_json_payload()
        if not payload:
            return jsonify({"error": "JSON invalide"}), 400
        remplacement_creator = MappingCompletionEmptyFileCreator(payload, config)
        filename = remplacement_creator.create()
        if not filename:
            logger.error("Erreur lors de la création du fichier CSV (cf logs du service).")
            return jsonify({"error": "Erreur lors de la création du fichier CSV"}), 500
        return jsonify({"filename": filename}), 200
    except BadRequest:
        return jsonify({"error": "JSON invalide"}), 400
    except Exception as exc:
        logger.error("Exception inattendue lors de la génération du fichier de remplacement: %s", exc, exc_info=True)
        return jsonify({"error": "Erreur interne lors de la création du fichier CSV"}), 500


@under_title.route('/file/mapping/phonetic/generate/', methods=['POST'])
def generate_phonetic_file() -> Any:
    """
    Génère un fichier de remplacement à partir d'un JSON reçu en POST.
    """
    logger.info("Requête reçue pour générer un fichier de phonetic.")
    try:
        payload = handle_json_payload()
        if not payload:
            return jsonify({"error": "JSON invalide"}), 400
        phonetic_creator = PhoneticFileCreator(payload, config)
        filename = phonetic_creator.create()
        if not filename:
            logger.error("Erreur lors de la création du fichier CSV phonetic (cf logs du service).")
            return jsonify({"error": "Erreur lors de la création du fichier CSV"}), 500
        return jsonify({"filename": filename}), 200
    except BadRequest:
        return jsonify({"error": "JSON invalide"}), 400
    except Exception as exc:
        logger.error("Exception inattendue lors de la génération du fichier phonetic: %s", exc, exc_info=True)
        return jsonify({"error": "Erreur interne lors de la création du fichier CSV"}), 500


@under_title.route('/file/mapping/save/', methods=['POST'])
def save_mapping_field() -> Any:
    """
    Sauvegarde un mapping field.
    """
    try:
        payload = handle_json_payload()
        if not payload:
            return jsonify({"error": "Payload invalide"}), 400
        logger.info("Requête reçue pour sauvegarder un mapping field: %s", payload)
        mapping = Mapping(config=config)
        mapped = mapping.set_from_mapping_preview(payload)

        if not mapped:
            logger.warning("Payload invalide pour la sauvegarde du mapping field : %s", payload)
            return jsonify({"error": "Payload invalide"}), 400
        result_save, new_file = mapping.save()
        if not result_save:
            logger.error("Erreur lors de la sauvegarde du mapping field: %s", payload)
            return jsonify({"error": "Erreur lors de la sauvegarde du mapping field"}), 500
        return jsonify({"success": True, "new_file": new_file}), 200
    except BadRequest:
        return jsonify({"error": "Payload invalide"}), 400
    except Exception as exc:
        logger.error("Exception inattendue lors de la sauvegarde du mapping field: %s", exc, exc_info=True)
        return jsonify({"error": "Erreur interne lors de la sauvegarde du mapping field"}), 500

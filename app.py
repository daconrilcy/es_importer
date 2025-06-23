from flask import render_template, request, jsonify
from flask import Flask

from config import Config

from models.file_management.file_loader import FileLoader
from elastic_manager import ElasticManager
import logging

from models.insertPhonetic import PhoneticRequestInserter
from routes.base import bases_road
from routes.file_common import common_file
from routes.mapping.under_title import under_title
from routes.upload import upload_road
from routes.renderer import render_page

logger = logging.getLogger(__name__)


def create_app():
    """
    Create the Flask app with the routes
    :return:
    """
    config = Config()
    app = Flask(__name__)  # ✅ Conserve cette instance, ne la redéfinis pas plus tard
    app.config.from_object(config)
    app.secret_key = config.app_web_secret
    app.register_blueprint(bases_road)
    app.register_blueprint(under_title)
    app.register_blueprint(upload_road)
    app.register_blueprint(common_file)

    @app.route("/404")
    def not_found_page():
        return render_page("404.html")

    @app.errorhandler(404)
    def page_not_found(e):
        return not_found_page()

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_page("500.html", error_reason=e)

    @app.route('/file/update_front_name', methods=['POST'])
    def update_front_name():
        """
        Update the front name of a file
        """
        data = request.get_json()
        if not data:
            return jsonify({"error": "Données JSON manquantes"}), 400
        if "front_name" not in data:
            return jsonify({"error": "Nom de fichier manquant"}), 400
        front_end_filename = data.get("front_name")
        if not front_end_filename:
            return jsonify({"error": "Nom de fichier invalide"}), 400
        file_id = data.get("file_id")
        if not file_id:
            return jsonify({"error": "ID de fichier manquant"}), 400
        result = ElasticManager(config).files.update_front_end_filename(file_id, front_end_filename)
        if not result:
            return jsonify({"error": "Erreur lors de la mise à jour du nom de fichier"}), 500
        return jsonify({"success": True, "message": "Nom de fichier mis à jour"}), 200

    # @app.route('/modify/<type_file>', methods=['POST'])
    # def modify_page(type_file):
    #     """
    #     Modify a file
    #     """
    #     if not file_types.is_type(type_file):
    #         print("❌ app.modify_page: file_type not found")
    #         return jsonify({"error": "Type de fichier non trouvé"}), 400
    #
    #     data = request.get_json()
    #     if not data:
    #         print("❌ app.modify_page: No JSON received")
    #         return jsonify({"error": "Données JSON manquantes"}), 400
    #
    #     result = ffile_manager.modify_file(data.get("id_file", None), data.get("filename", None),
    #                                        data.get("separator", None))
    #     if not result:
    #         return jsonify({"error": "Erreur lors de la modification"}), 500
    #     return jsonify({"success": True, "message": "Document modifié"}), 200

    # @app.route("/file/delete", methods=["DELETE"])
    # def delete_file():
    #     """
    #     Supprime un fichier
    #     :return:
    #     """
    #     data = request.get_json()
    #     print(data)
    #     if "file_id" not in data:
    #         return jsonify({"error": "id de fichier manquant"}), 400
    #     file_id = data.get("file_id")
    #     if not file_id:
    #         return jsonify({"error": "id de fichier invalide"}), 400
    #
    #     if not ffile_manager.delete_file(file_id):
    #         return jsonify({"error": "Erreur lors de la suppression du fichier"}), 500
    #     return jsonify({"success": True, "message": "Fichier supprimé"})

    @app.route('/file/list-all', methods=['GET'])
    def file_list_all():
        """
        Get the list of all files
        :return:
        """
        files_by_type = ElasticManager(config).files_obj.get_all_by_type()
        return render_page("list_view_all.html", files_by_type=files_by_type)

    def _render_file_preview(file_id: str, chunk: int = 0):
        """
        Fonction utilitaire pour rendre la prévisualisation d'un fichier CSV (full ou chunk).
        """
        file_loader = FileLoader()
        try:
            preview = file_loader.get_full_preview(file_id, chunk)
        except Exception as e:
            print(e)
            return render_page("500.html", error_reason=f"Erreur lors de la prévisualisation du fichier: {e}")
        if not preview:
            return render_page("500.html", error_reason="Erreur lors de la prévisualisation du fichier")
        try:
            list_files = ElasticManager(config).files_obj.get_by_type(preview.type_name)
        except Exception as e:
            return render_page("500.html", error_reason=f"Erreur lors de la récupération des fichiers: {e}")
        if not list_files:
            return render_page("500.html", error_reason="Erreur lors de la récupération des fichiers")
        return render_page("preview_files/main_preview_layout.html", files_one_list=list_files, datas=preview)

    @app.route('/file/preview/<file_id>/', methods=['GET'])
    def file_preview_chunk_0(file_id: str):
        """
        File preview page (chunk 0)
        """
        return _render_file_preview(file_id)

    @app.route('/file/preview/<file_id>/<int:chunk>', methods=['GET'])
    def file_preview(file_id: str, chunk: int = 0):
        """
        File preview page (chunk n)
        """
        return _render_file_preview(file_id, chunk=chunk)

    @app.route('/file/preview/data-zone/<file_id>/<int:chunk>', methods=['GET'])
    def file_preview_data_zone(file_id: str, chunk: int = 0):
        """
        File preview page (data zone)
        """
        preview = FileLoader().get_full_preview(file_id, chunk)
        if not preview:
            return render_page("500.html", error_reason="Erreur lors de la prévisualisation du fichier")

        return render_template("preview_files/data_zone.html", datas=preview)

    @app.route('/file/preview-table/<file_id>/<int:chunk>', methods=['GET'])
    def file_preview_table(file_id: str, chunk: int = 0):
        """
        File preview page
        :param file_id:
        :param chunk:
        """
        file_loader = FileLoader()
        preview = file_loader.get_full_preview(chunk_index=chunk, file_id=file_id)
        return render_template("preview_files/csv/csv_datas_preview.html", datas=preview)

    @app.route('/file/preview-table-path/<encoded_file_path>/<int:chunk>', methods=['GET'])
    def file_preview_table_path(encoded_file_path: str, chunk: int = 0):
        file_loader = FileLoader()
        previewer = file_loader.get_datas_preview(encoded_file_path=encoded_file_path, chunk_index=chunk)
        return render_template("preview_files/csv/csv_table.html", datas=previewer)

    @app.route('/file/chunk-rows/<encoded_file_path>/<int:chunk>', methods=['GET'])
    def file_chunk_rows(encoded_file_path: str, chunk: int = 0):
        """
        File chunk page (rows only)
        """
        file_loader = FileLoader()
        rows = file_loader.get_rows_preview(encoded_file_path, chunk)
        return render_template("preview_files/csv/csv_rows.html", rows=rows)

    @app.route('/file/pagination-data/<int:chunk_index>/<int:num_chunks>/<int:chunk_size>', methods=['GET'])
    def file_pagination_data(chunk_index: int, num_chunks: int, chunk_size: int):
        """
        File pagination data
        """
        return render_template("preview_files/csv/table_pagination.html", chunk_index=chunk_index,
                               num_chunks=num_chunks, chunk_size=chunk_size)

    @app.route('/file/data/headers/<encode_filepath>', methods=['GET'])
    def get_headers_file_data(encode_filepath: str):
        """
        Get headers of a file
        """
        file_loader = FileLoader()
        headers = file_loader.get_file_data_headers(encode_filepath)
        return jsonify({"headers": headers}), 200

    @app.route('/file/add/phonetic/', methods=['POST'])
    def file_add_phonex():
        """ File add phonex page """
        try:
            result = PhoneticRequestInserter(config).insert(request.get_json())
        except Exception as e:
            logger.error(e)
            result = False
        if not result:
            return jsonify({"error": "Erreur lors de l'ajout des phonemes"}), 500

        return jsonify({"success": True, "message": "phonemes ajoutés"}), 200

    @app.route('/completion/create/phonetic/', methods=['POST'])
    def completion_create_phonex():
        pass

    # @app.route('/file/save', methods=['POST'])
    # def file_save():
    #     """
    #     Save a file
    #     :return:
    #     """
    #     print("app.file_save")
    #     data = request.get_json()
    #     print(data)
    #     if not data:
    #         return jsonify({"error": "Données JSON manquantes"}), 400
    #     if "type_file" not in data:
    #         return jsonify({"error": "Type de fichier manquant"}), 400
    #     if "file_id" not in data:
    #         return jsonify({"error": "ID de fichier manquant"}), 400
    #     if "filename" not in data:
    #         return jsonify({"error": "Nom de fichier manquant"}), 400
    #     if "datas" not in data:
    #         return jsonify({"error": "Données manquantes"}), 400
    #     print("app.file_save: data ok")
    #     type_file = data.get("type_file")
    #     file_id = data.get("file_id")
    #     filename = data.get("filename")
    #     datas = data.get("datas")
    #     if not file_types.is_type(type_file):
    #         return jsonify({"error": "Type de fichier invalide"}), 400
    #
    #     result = ffile_manager.save_file(type_file, data)
    #     if not result:
    #         return jsonify({"error": "Erreur lors de la sauvegarde"}), 500
    #     return jsonify({"success": True, "message": "Document sauvegardé"}), 200

    return app


if __name__ == '__main__':
    app_test = create_app()
    app_test.run(debug=True)

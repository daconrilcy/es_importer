from flask import render_template, redirect, url_for, session, send_from_directory, request, jsonify
from flask import Flask
from config import Config
from models.elastic_type.collection import EsTypes
from models.es_analyser import EsAnalysers
from models.file_type import FileTypes
from full_file_manager import FullFileManager


def create_app():
    """
    Create the Flask app with the routes
    :return:
    """
    config = Config()
    app = Flask(__name__)  # ✅ Conserve cette instance, ne la redéfinis pas plus tard
    app.config.from_object(config)
    app.secret_key = config.app_web_secret
    file_types = FileTypes()
    ffile_manager = FullFileManager(config)

    print("↪ Mise à jour de l'index au démarrage")
    ffile_manager.update_es_file_index()

    @app.before_request
    def check_authentication():
        """
        Check if the user is authenticated
        :return:
        """
        allowed_routes = ["login", "static"]
        if not session.get("logged_in") and request.endpoint not in allowed_routes:
            return redirect(url_for("login"))

    def render_page(template, **kwargs):
        """
        Render a page with the layout if the user is authenticated
        :param template:
        :param kwargs:
        :return: HTML page
        """
        if session.get('logged_in'):
            is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
            if not is_ajax:
                return render_template("layout.html")
            return render_template(template, layout=False, **kwargs)
        return render_template("login.html")

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """
        Serve static files
        :param filename:
        :return:
        """
        return send_from_directory('static', filename, cache_timeout=31536000)

    @app.route('/')
    def index():
        """
        Index page
        :return:
        """
        return render_page('home.html')

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        """
        Login page
        :return:
        """
        if request.method == 'GET':
            return render_template("login.html")

        username = request.form.get('login')
        password = request.form.get('password')

        if Config().check_app_credentials(username, password):
            session['logged_in'] = True
            return redirect("home")
        return jsonify({"error": "Identifiants invalides"}), 401

    @app.route('/logout')
    def logout():
        """
        Logout page
        :return:
        """
        session.pop('logged_in', None)
        return redirect(url_for('login'))

    @app.route('/home')
    def home():
        """
        Home page
        :return:
        """
        return render_page('home.html')

    @app.route('/import/<file_type>')
    def import_page(file_type=file_types.datas.name):
        """
        Import page block
        :return: HTML page
        """
        ffile_manager.update_es_file_index()
        file_type = file_types.get_file_type_by_name(file_type)

        if file_type is None:
            print("❌ app.import_page: file_type is None")
            return render_template("404.html", error_reason="Type de fichier non trouvé")
        files_list = ffile_manager.get_files_list_by_type(type_name=file_type.name)
        if files_list is False:
            print("❌ app.import_page: files_list is False")
            return render_template("404.html",
                                   error_reason="Erreur lors de la recuperation des fichiers")
        return render_page('import.html', data_files=files_list, file_type=file_type,
                           add_infos="")

    @app.route('/modify/<type_file>', methods=['POST'])
    def modify_page(type_file):
        """
        Modify a file
        """
        if not file_types.is_type(type_file):
            print("❌ app.modify_page: file_type not found")
            return jsonify({"error": "Type de fichier non trouvé"}), 400

        data = request.get_json()
        if not data:
            print("❌ app.modify_page: No JSON received")
            return jsonify({"error": "Données JSON manquantes"}), 400

        result = ffile_manager.modify_file(data.get("id_file", None), data.get("filename", None),
                                           data.get("separator", None))
        if not result:
            return jsonify({"error": "Erreur lors de la modification"}), 500
        return jsonify({"success": True, "message": "Document modifié"}), 200

    @app.route("/upload", methods=["POST"])
    def upload_file():
        """
        Upload a file
        :return:
        """
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier envoyé"}), 400
        if "filetype" not in request.form:
            return jsonify({"error": "Type de fichier manquant"}), 400

        file = request.files["file"]
        file_type = request.form.get("filetype")

        if not file_types.is_type(file_type):
            return jsonify({"error": "Type de fichier invalide"}), 400
        if not ffile_manager.upload_file(file, file_type):
            return jsonify({"error": "Erreur lors de l'importation du fichier"}), 500
        return jsonify({"success": True, "message": "Fichier importé"})

    @app.route("/files-list/<type_file>", methods=["GET"])
    def get_files_list(type_file):
        """
        Get the list of files
        :return:
        """
        if "add_infos" not in request.form:
            add_infos = ""
        else:
            add_infos = request.form.get("add_infos")
        if not file_types.is_type(type_file):
            return jsonify({"error": "Type de fichier invalide"}), 400
        ffile_manager.update_es_file_index()
        file_type = file_types.get_file_type_by_name(type_file)
        files_list_obj = ffile_manager.get_files_list_by_type(type_name=file_type.name)
        return render_page("list_files.html", data_files=files_list_obj, add_infos=add_infos,
                           file_type=file_type)

    @app.route("/mapping-preview-row", methods=["GET"])
    def mapping_preview_row():
        """
        Get the render of mapping preview row
        :return:
        """
        es_types = EsTypes().list()
        es_analysers = EsAnalysers().list
        list_bool = [True, False]
        source_field_name = request.args.get("source_field_name", "")
        isfixed = request.args.get("isfixed", "false")
        field_name = request.args.get("field_name", source_field_name)
        type_field = request.args.get("type_field", "text")
        is_mapped = request.args.get("is_mapped", "false")
        analyzer = request.args.get("analyzer", "standard")
        fixed_value = request.args.get("fixed_value", "")
        is_fixed = True if isfixed.lower() == "true" else False
        is_mapped = True if is_mapped.lower() == "true" else False
        if not source_field_name or source_field_name == "":
            is_fixed = True

        return render_template("preview_files/modules/row_preview_mappings.html",
                               source_field_name=source_field_name, isfixed=is_fixed, field_name=field_name,
                               type_field=type_field, is_mapped=is_mapped, analyzer=analyzer, fixed_value=fixed_value,
                               es_types=es_types, es_analysers=es_analysers, list_bool=list_bool)

    @app.route("/file/delete", methods=["DELETE"])
    def delete_file():
        """
        Supprime un fichier
        :return:
        """
        data = request.get_json()
        print(data)
        if "file_id" not in data:
            return jsonify({"error": "id de fichier manquant"}), 400
        file_id = data.get("file_id")
        if not file_id:
            return jsonify({"error": "id de fichier invalide"}), 400

        if not ffile_manager.delete_file(file_id):
            return jsonify({"error": "Erreur lors de la suppression du fichier"}), 500
        return jsonify({"success": True, "message": "Fichier supprimé"})

    @app.route('/file-preview/<file_id>', methods=['GET'])
    def file_preview(file_id):
        """
        File preview page
        :param file_id:
        :return:
        """
        if not file_id:
            return jsonify({"error": "ID de fichier manquant"}), 400
        file_preview_obj = ffile_manager.get_file_preview_by_id(file_id)
        if file_preview_obj is False or file_preview_obj is None:
            return jsonify({"error": "Erreur lors de la recuperation du fichier"}), 500
        return render_template(file_preview_obj.layout, data=file_preview_obj.datas)

    @app.route('/file/save', methods=['POST'])
    def file_save():
        """
        Save a file
        :return:
        """
        print("app.file_save")
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({"error": "Données JSON manquantes"}), 400
        if "type_file" not in data:
            return jsonify({"error": "Type de fichier manquant"}), 400
        if "file_id" not in data:
            return jsonify({"error": "ID de fichier manquant"}), 400
        if "filename" not in data:
            return jsonify({"error": "Nom de fichier manquant"}), 400
        if "datas" not in data:
            return jsonify({"error": "Données manquantes"}), 400
        print("app.file_save: data ok")
        type_file = data.get("type_file")
        file_id = data.get("file_id")
        filename = data.get("filename")
        datas = data.get("datas")
        if not file_types.is_type(type_file):
            return jsonify({"error": "Type de fichier invalide"}), 400

        result = ffile_manager.save_file(type_file, data)
        if not result:
            return jsonify({"error": "Erreur lors de la sauvegarde"}), 500
        return jsonify({"success": True, "message": "Document sauvegardé"}), 200

    return app


if __name__ == '__main__':
    app_test = create_app()
    app_test.run(debug=True)

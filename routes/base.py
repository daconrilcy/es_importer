from flask import session, request, redirect, url_for, render_template, jsonify, Blueprint

from config import Config

from routes.renderer import render_page

bases_road = Blueprint("bases_road", __name__)


@bases_road.before_request
def check_authentication():
    """
    Check if the user is authenticated
    :return:
    """
    allowed_routes = ["login", "static"]
    if not session.get("logged_in") and request.endpoint not in allowed_routes:
        return redirect(url_for("login"))
    return None


@bases_road.route('/')
def index():
    """
    Index page
    :return:
    """
    return render_page('home.html')


@bases_road.route('/home')
def home():
    """
    Home page
    :return:
    """
    return render_page('home.html')


@bases_road.route('/login', methods=['POST', 'GET'])
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


@bases_road.route('/logout')
def logout():
    """
    Logout page
    :return:
    """
    session.pop('logged_in', None)
    return redirect(url_for('login'))

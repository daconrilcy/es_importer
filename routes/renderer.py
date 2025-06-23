from flask import session, request, render_template


def render_page(template, **kwargs):
    """
    Render a page with the layout if the user is authenticated
    :param template:
    :param kwargs:
    :return: HTML page
    """
    if session.get('logged_in'):
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        return render_template(template, layout=not is_ajax, **kwargs)
    return render_template("login.html")
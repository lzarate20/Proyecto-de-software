from flask import render_template


def not_found_error(e):
    kwargs = {
        "error_name": "404 Not Found Error",
        "error_description": "La url a la que quiere acceder no existe",
    }
    return render_template("error.html", **kwargs), 404


def unauthorized_error(e):
    kwargs = {
        "error_name": "401 Unauthorized Error",
        "error_description": "No está autorizado para acceder a la url",
    }
    return render_template("error.html", **kwargs), 401

def bad_request_error(e):
    kwargs = {
        "error_name": "400 Bad Request",
        "error_description": "Se produjo un error al procesar los datos, por favor revisarlos",
    }
    return render_template("error.html", **kwargs), 400

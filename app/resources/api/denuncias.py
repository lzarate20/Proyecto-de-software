from flask import jsonify, Blueprint, request, session
from app.models.categories import Categoria
from app.models.configuration import Configuration
from app.models.denuncias import Denuncia
from app.schema.denuncias import DenunciaSchema
from app.forms.denuncias import CreateDenunciaForm
from flask_cors import CORS


denuncia_api = Blueprint("denuncias", __name__, url_prefix="/denuncias")


@denuncia_api.get("/")
def index():
    config = Configuration.get_configuration()
    if not request.args:
        denuncias_iter = Denuncia.get_by_state("en_curso")
        response = [DenunciaSchema.dump(denuncia) for denuncia in denuncias_iter]
    else:
        try:
            page = request.args.get("page")
            denuncias = Denuncia.get_by_state("en_curso")
            denuncias_iter = Denuncia.get_denuncias_paginated(
                denuncias, int(page), config
            )
            response = DenunciaSchema.dump(denuncias_iter, many=True)
        except:
            response = {
                "error_name": "400 Bad Request",
                "error_description": "Numero de pagina invalido",
            }
    return jsonify(response)


@denuncia_api.get("/<int:id>")
def by_id(id):
    response = Denuncia.get_by_id(id)
    if not response:
        response = {
            "error_name": "400 Bad Request",
            "error_description": "No existe una denuncia con dicho id",
        }
        return jsonify(response)
    response = DenunciaSchema.dump(response)
    return jsonify(response)


@denuncia_api.post("/")
def create():
    response = {}
    fields = [
        "title",
        "category",
        "description",
        "lat",
        "long",
        "firstname",
        "lastname",
        "tel",
        "email",
    ]
    if not all(field in fields for field in request.get_json().keys()):
        response = {
            "error_name": "400 Bad Request",
            "error_description": "Error en los nombres de los campos",
            "fields": [
                "title",
                "category",
                "description",
                "lat",
                "long",
                "firstname",
                "lastname",
                "tel",
                "email",
            ],
        }
        return jsonify(response), 400
    form = CreateDenunciaForm(**request.get_json())
    if form.validate_on_submit():
        if Denuncia.unique_field(form.title.data):
            response = {
                "error_name": "400 Bad Request",
                "error_description": "El titulo ya se encuentra cargado en el sistema",
            }
            return jsonify(response), 400
        response = Denuncia(
            title=form.title.data,
            description=form.description.data,
            lat=form.lat.data,
            long=form.long.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            tel=form.tel.data,
            email=form.email.data,
        )
        category = Categoria.get_category_by_id(form.category.data)
        if not category:
            return jsonify(response), 400
        category.assign_complaints(response)
        response.add_denuncia()
        response = DenunciaSchema.dump(response)
        return jsonify(response), 201
    response = {
        "error_name": "400 Bad Request",
        "error_description": form.errors,
    }
    return jsonify(response), 400

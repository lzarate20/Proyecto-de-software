from flask import jsonify,Blueprint,request,session
from werkzeug.wrappers import response
from app.models.categories import Categoria
from app.models.configuration import Configuration
from app.models.denuncias import Denuncia
from app.schema.denuncias import DenunciaSchema
from app.forms.denuncias import CreateDenunciaForm




denuncia_api = Blueprint("denuncias",__name__,url_prefix="/denuncias")


@denuncia_api.get("/")
def index():
    denuncias_iter= Denuncia.get_all()
    denuncias = [DenunciaSchema.dump(denuncia) for denuncia in denuncias_iter]
    return jsonify(denuncias)


@denuncia_api.get("/<int:page>")
def paginated(page):
    config = Configuration.get_configuration()
    denuncias_page = Denuncia.get_paginated(page=int(page),config=config)
    denuncias = DenunciaSchema.dump(denuncias_page,many=True)
    return jsonify(denuncias)


@denuncia_api.post("/")
def create():
    response = {}
    fields = ["title","category","description","lat","long","firstname","lastname","tel","email"]
    if not all(field in fields for field in request.get_json().keys()):
        response = {
            "error_name": "400 Bad Request",
            "error_description": "Error en los nombres de los campos",
            "fields":   ["title", "category","description","lat","long","firstname","lastname","tel","email"
            ]
        }
        return jsonify(response),400
    form = CreateDenunciaForm(**request.get_json())
    if form.validate_on_submit():
        if Denuncia.unique_field(form.title.data):
            response = {
                "error_name": "400 Bad Request",
                "error_description": "El titulo ya se encuentra cargado en el sistema",
            }
            return jsonify(response),400
        response = Denuncia(title=form.title.data,description=form.description.data,
        lat=form.lat.data,long=form.long.data,firstname=form.firstname.data,lastname=form.lastname.data,
        tel=form.tel.data,email=form.email.data)
        category = Categoria.get_category_by_id(form.category.data)
        if not category:
            return jsonify(response),400
        category.assign_complaints(response)
        response.add_denuncia()
        response = DenunciaSchema.dump(response)
        return jsonify(response),201
    response = {"error_name": "400 Bad Request",
            "error_description":form.errors,}
    return jsonify(response),400
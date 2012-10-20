from flask import Blueprint, request, g, url_for, abort
from formencode import Invalid
from werkzeug.exceptions import BadRequest

from us.database import db_session
from us.models import Project, User
from us.utils import json_response
from us.validators import Registration


api = Blueprint('api', __name__, template_folder='templates',
        static_folder='static')


def validate(input_data, validator):
    try:
        clean_data = validator.to_python(input_data)
    except Invalid, e:
        raise BadRequest(e.msg)
    return clean_data

def get_or_abort(cls, id):
    obj = cls.query.get(id)
    if (obj is None):
        abort(404)
    return obj


@api.route("/register", methods=['POST'])
def register():
    validator = Registration()
    data = validate(request.json, validator)
    user = User.create(data['email'], data['password'])
    db_session.commit()
    response = json_response(user.json_data, 201)
    response.headers['Location'] = url_for("api.profile", user_id=user.id)
    return response


@api.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_or_abort(User, user_id)
    return json_response(user.json_data)


@api.route("/profile/<int:user_id>/projects")
def user_projects(user_id):
    user = get_or_abort(User, user_id)
    projects = user.get_projects()
    data = {"projects": [p.json_data for p in projects]}
    return json_response(data)

@api.route("/projects/<int:project_id>")
def projects(project_id):
    project = get_or_abort(Project, project_id)
    return json_response(project.json_data)

@api.route("/projects/<int:project_id>/userstories")
def project_userstories(project_id):
    project = get_or_abort(Project, project_id)
    data = {"stories": [us.json_data for us in project.userstories]}
    return json_response(data)

from flask import Blueprint, request, g, url_for, abort
from formencode import Invalid
from werkzeug.exceptions import BadRequest, Unauthorized
from werkzeug.security import check_password_hash

from us.database import db_session
from us.models import Project, User, Session, UserStoryList, UserStory
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

@api.route("/login", methods=['POST'])
def login():
    data = request.json
    user = User.get_by_email(data['email'])
    if (user is None):
        abort(400)
    if (not check_password_hash(user.password, data['password'])):
        abort(400)
    session = Session(user=user)
    db_session.commit()
    response = json_response(session.json_data, 201)
    response.headers['Location'] = url_for("api.profile", user_id=user.id)
    return response

@api.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_or_abort(User, user_id)
    return json_response(user.json_data)


@api.route("/profile/<int:user_id>/projects", methods=['GET'])
def user_projects(user_id):
    user = get_or_abort(User, user_id)
    projects = user.get_projects()
    data = {"projects": [p.json_data for p in projects]}
    return json_response(data)

@api.route("/projects", methods=['POST'])
def create_project():
    p = Project.create(request.json['name'], g.user)
    response = json_response(p.json_data, 201)
    response.headers.set('Location', url_for("api.project", project_id=p.id))
    return response

@api.route("/projects/<int:project_id>")
def project(project_id):
    project = get_or_abort(Project, project_id)
    if (not g.user.can_access(project)):
        raise Unauthorized()
    return json_response(project.json_data)

@api.route("/projects/<int:project_id>/lists/<int:list_id>/stories", methods=['POST'])
def create_story(project_id, list_id):
    project = get_or_abort(Project, project_id)
    if (not g.user.can_access(project)):
        raise Unauthorized()
    list = get_or_abort(UserStoryList, list_id)
    data = request.json
    story = UserStory.create(data['title'], data['points'], list)
    response = json_response(story.json_data, 201)
    response.headers.set('Location', url_for('api.story', project_id=project_id, 
            list_id=list_id, story_id=story.id))
    return response

@api.route("/projects/<int:project_id>/lists/<int:list_id>/stories/<int:story_id>")
def story(project_id, list_id, story_id):
    return "Hallo"

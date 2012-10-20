from flask import Blueprint, jsonify, request, g, url_for, abort
from formencode import Invalid

from us.database import db_session
from us.models import User
from us.validators import Registration


api = Blueprint('api', __name__, template_folder='templates',
        static_folder='static')


def json_response(data, status_code=200):
    response = jsonify(data)
    response.status_code = status_code
    return response

def validate(input_data, validator):
    try:
        clean_data = validator.to_python(input_data)
    except Invalid, e:
        return abort(400)
    return clean_data


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
    return json_response({"user": "anders"})

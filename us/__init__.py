from datetime import datetime
from flask import Flask, request, g, url_for
from werkzeug.exceptions import Unauthorized

from us.api import api
from us.database import db_session
from us.models import Session


app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")

# Register json api error handlers
import us.error_handlers


@app.before_request
def authenticate_request():
    if request.path in [url_for(r) for r in ["api.login", "api.register"]]:
        return
    auth_token = request.headers.get('X-Auth-Token', None)
    if (auth_token is None):
        raise Unauthorized()
    session = Session.query.get(auth_token)
    if (session is None):
        raise Unauthorized()
    session.updated_at = datetime.now()
    session.save()
    db_session.commit()
    g.user = session.user

@app.teardown_request
def close_db_session(exception=None):
    db_session.remove()

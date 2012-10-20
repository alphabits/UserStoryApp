from flask import Flask

from us.api import api
from us.database import db_session


app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")


@app.teardown_request
def close_db_session(exception=None):
    db_session.remove()

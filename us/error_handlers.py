from us import app
from us.utils import json_response



def get_errorhandler(code):
    return lambda e: json_response({"error": str(e)}, code)

for code in [400, 401, 404]:
    app.errorhandler(code)(get_errorhandler(code))

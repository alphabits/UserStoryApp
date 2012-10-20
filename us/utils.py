from flask import jsonify
import random
import string



def random_string(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(length))


def json_response(data, status_code=200):
    response = jsonify(data)
    response.status_code = status_code
    return response



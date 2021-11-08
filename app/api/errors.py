from flask import jsonify
from werkzeug.exceptions import HTTPException

from app.exceptions import ValidationError
from . import blueprint


@blueprint.before_request
def before_req():
    pass


@blueprint.errorhandler(HTTPException)
def http_error_handler(e):
    response = jsonify({'error': e.code, 'message': e.description})
    response.status_code = e.code
    return response


@blueprint.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

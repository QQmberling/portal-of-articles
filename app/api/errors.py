from werkzeug.exceptions import HTTPException
from flask import jsonify, request, abort
from app.exceptions import ValidationError
from . import api


@api.before_request
def accept_only_json():
    if request.method in ['POST', 'PUT'] and (request.content_length == 0 or not request.is_json):
        return bad_request('request is not json')


@api.errorhandler(HTTPException)
def http_error_handler(e):
    response = jsonify({'error': e.description})
    response.status_code = e.code
    return response


@api.errorhandler(ValidationError)
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

from flask import render_template
from werkzeug.exceptions import HTTPException

from . import main

context = {'legend': 'Ошибка'}


@main.errorhandler(HTTPException)
def http_error_handler(e):
    context['message'] = e.description
    context['code'] = e.code
    return render_template('error.html', context=context), e.code

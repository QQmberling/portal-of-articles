from flask import render_template
from . import admin


@admin.errorhandler(404)
def page_not_found(e):
    context = {'legend': 'Ошибка'}
    return render_template('404.html', context=context), 404


@admin.errorhandler(500)
def internal_server_error(e):
    context = {'legend': 'Ошибка'}
    return render_template('500.html', context=context), 500
from os import environ

from flask import current_app


def test_config_settings(app):
    assert current_app.config['TESTING'] is True
    assert current_app.config['ENV'] == 'testing'
    # assert current_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite://'
    assert current_app.config['SQLALCHEMY_DATABASE_URI'] == environ.get(
        'TESTING_DATABASE_URL') or "postgresql://postgres:qqmberling@localhost:5432/data-test"

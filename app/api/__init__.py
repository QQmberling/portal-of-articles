from flask import Blueprint
from flask_restx import Namespace

blueprint = Blueprint('api', __name__, url_prefix='/api/v1/')
np_user = Namespace('users', description='Users')
np_art = Namespace('articles', description='Articles')
np_comm = Namespace('comments', description='Comments')

from . import users, articles, comments

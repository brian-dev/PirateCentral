from flask import Blueprint

players_bp = Blueprint('players', __name__, template_folder='templates', static_folder='static')

from . import routes
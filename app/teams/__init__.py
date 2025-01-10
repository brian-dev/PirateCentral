from flask import Blueprint

teams_bp = Blueprint('teams', __name__, template_folder='templates', static_folder='static')

from . import routes
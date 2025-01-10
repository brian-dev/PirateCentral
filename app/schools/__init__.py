from flask import Blueprint

schools_bp = Blueprint('schools', __name__, template_folder='templates', static_folder='static')

from . import routes
from flask import render_template
from . import home_bp

@home_bp.route('/')
def index():
    from app.models import Team, Player
    teams = Team.query.all()
    players = Player.query.all()
    return render_template('index.html', teams=teams, players=players)
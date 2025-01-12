from flask import render_template, flash, redirect, url_for, Blueprint

from . import teams_bp  # Import the blueprint object
from app.decorators import role_required
from ..models import Team, Game, BoxScore


@teams_bp.route('/all_teams')
def all_teams():
    from app.models import Team  # Delay import to avoid circular dependencies
    teams = Team.query.all()
    return render_template('list_teams.html', teams=teams)


@teams_bp.route('/teams/<int:team_id>')
def team(team_id):
    from app.models import Team  # Import Team model

    # Fetch the team or raise a 404 if not found
    team = Team.query.get_or_404(team_id)

    # Use the players relationship on the Team model to fetch players
    players = team.players

    # Render the template with the team and its players
    return render_template('team.html', team=team, players=players)



@teams_bp.route('/add_team', methods=['GET', 'POST'])
# @role_required(["admin", "coach"])
def add_team():
    from .forms import AddTeamForm  # Delay import
    from app.models import School, Team  # Delay import
    from app import db  # Delay import

    form = AddTeamForm()
    schools = School.query.all()
    form.school_id.choices = [(school.id, school.school_name) for school in schools]

    if form.validate_on_submit():
        grade_level = form.grade_level.data
        sport = form.sport.data
        school_id = form.school_id.data

        # Create new team object
        new_team = Team(
            grade_level=grade_level,
            sport=sport,
            school_id=school_id
        )

        # Add and commit to database
        db.session.add(new_team)
        db.session.commit()

        flash(f'Team "{sport}" added successfully!', 'success')
        return redirect(url_for('teams.add_team'))  # Use the blueprint prefix for URL

    return render_template('add_team.html', form=form)

@teams_bp.route('/roster/<int:team_id>', methods=['GET'])
def roster(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template('roster.html', team=team)

@teams_bp.route('/schedule/<int:team_id>', methods=['GET'])
def schedule(team_id):
    team = Team.query.get_or_404(team_id)
    games_with_opponents = sorted(
        [
            {
                "game": game,
                "opponent": Team.query.get(game.away_team_id)
            }
            for game in team.home_games
        ],
        key=lambda entry: entry["game"].date  # Sort by game date
    )
    return render_template('schedule.html', team=team, games_with_opponents=games_with_opponents)

@teams_bp.route('/team_stats/<int:team_id>', methods=['GET'])
def team_stats(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template('team_stats.html', team=team)

@teams_bp.route('/box_score/<int:game_id>')
def box_score(game_id):
    game = Game.query.get_or_404(game_id)
    box_scores = BoxScore.query.filter_by(game_id=game_id).all()

    return render_template('box_score.html', game=game, box_scores=box_scores)

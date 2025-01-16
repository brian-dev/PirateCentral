from datetime import datetime

from flask import render_template, flash, redirect, url_for, Blueprint, abort

from . import teams_bp  # Import the blueprint object
from app.decorators import role_required
from ..models import Team, Game, PlayerStats


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


@teams_bp.route('/schedule/<int:team_id>')
def schedule(team_id):
    team = Team.query.get_or_404(team_id)

    # Query only games for the specific team, grade level, and gender
    games = Game.query.filter(
        ((Game.home_team_id == team_id) | (Game.away_team_id == team_id)) &
        (Game.home_team.has(grade_level=team.grade_level, gender=team.gender)) &
        (Game.away_team.has(grade_level=team.grade_level, gender=team.gender))
    ).all()

    # Calculate wins and losses
    wins = 0
    losses = 0
    for game in games:
        if game.home_team_id == team_id and game.home_score > game.away_score:
            wins += 1
        elif game.away_team_id == team_id and game.away_score > game.home_score:
            wins += 1
        else:
            losses += 1

    record = {"wins": wins, "losses": losses}

    # Pass the `games` SQLAlchemy objects directly to the template
    return render_template(
        'schedule.html',
        team=team,
        schedule=games,  # Pass raw SQLAlchemy game objects
        season={"start": team.sport.season_start, "end": team.sport.season_end},
        record=record
    )


@teams_bp.route('/team_stats/<int:team_id>', methods=['GET'])
def team_stats(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template('team_stats.html', team=team)

@teams_bp.route('/game/<int:game_id>', methods=['GET'])
def game_details(game_id):
    """Display the details of a specific game."""
    # Retrieve the game object
    game = Game.query.get_or_404(game_id)

    # Retrieve player statistics for both teams
    home_team_stats = PlayerStats.query.filter_by(game_id=game.id, team_id=game.home_team_id).all()
    away_team_stats = PlayerStats.query.filter_by(game_id=game.id, team_id=game.away_team_id).all()

    # Aggregate statistics for comparison
    home_team_aggregated_stats = {}
    away_team_aggregated_stats = {}

    # Assuming stats definitions are uniform for both teams
    stats_definitions = game.home_team.sport.stats_definitions
    for stat_name in stats_definitions:
        home_team_aggregated_stats[stat_name] = sum(
            stat.stats.get(stat_name, 0) for stat in home_team_stats
        )
        away_team_aggregated_stats[stat_name] = sum(
            stat.stats.get(stat_name, 0) for stat in away_team_stats
        )

    # Pass data to the template
    game_stats = {
        "home_team": game.home_team,
        "away_team": game.away_team,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "home_team_stats": home_team_stats,
        "away_team_stats": away_team_stats,
        "home_team_aggregated_stats": home_team_aggregated_stats,
        "away_team_aggregated_stats": away_team_aggregated_stats,
    }

    return render_template('game_details.html', game=game, game_stats=game_stats)

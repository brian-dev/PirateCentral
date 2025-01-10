from flask import render_template, Blueprint, request, redirect, url_for, flash
from . import players_bp
from app.decorators import role_required

@players_bp.route('/players/<int:player_id>/add_stats', methods=["GET", "POST"])
# @role_required(["coach", "admin"])
def add_stats():
    from app.models import Stat, Player, Game  # Delay import
    from app import db  # Delay import

    if request.method == 'POST':
        player_id = request.form['player_id']
        game_id = request.form['game_id']
        touchdowns = request.form.get('touchdowns', 0)
        interceptions = request.form.get('interceptions', 0)
        passing_yards = request.form.get('passing_yards', 0)
        completions = request.form.get('completions', 0)
        attempts = request.form.get('attempts', 0)
        rushing_yards = request.form.get('rushing_yards', 0)
        receiving_yards = request.form.get('receiving_yards', 0)
        receptions = request.form.get('receptions', 0)
        tackles = request.form.get('tackles', 0)
        sacks = request.form.get('sacks', 0)
        interceptions_defense = request.form.get('interceptions_defense', 0)
        fumbles = request.form.get('fumbles', 0)
        fumble_recoveries = request.form.get('fumble_recoveries', 0)
        field_goals_made = request.form.get('field_goals_made', 0)
        field_goals_attempted = request.form.get('field_goals_attempted', 0)
        field_goal_yards = request.form.get('field_goal_yards', 0)
        extra_points_made = request.form.get('extra_points_made', 0)
        extra_points_attempted = request.form.get('extra_points_attempted', 0)
        punt_yards = request.form.get('punt_yards', 0)
        number_of_punts = request.form.get('number_of_punts', 0)
        kick_return_yards = request.form.get('kick_return_yards', 0)
        punt_return_yards = request.form.get('punt_return_yards', 0)

        stat = Stat(
            player_id=player_id,
            game_id=game_id,
            touchdowns=touchdowns,
            interceptions=interceptions,
            passing_yards=passing_yards,
            completions=completions,
            attempts=attempts,
            rushing_yards=rushing_yards,
            receiving_yards=receiving_yards,
            receptions=receptions,
            tackles=tackles,
            sacks=sacks,
            interceptions_defense=interceptions_defense,
            fumbles=fumbles,
            fumble_recoveries=fumble_recoveries,
            field_goals_made=field_goals_made,
            field_goals_attempted=field_goals_attempted,
            field_goal_yards=field_goal_yards,
            extra_points_made=extra_points_made,
            extra_points_attempted=extra_points_attempted,
            punt_yards=punt_yards,
            number_of_punts=number_of_punts,
            kick_return_yards=kick_return_yards,
            punt_return_yards=punt_return_yards,
        )
        db.session.add(stat)
        db.session.commit()
        flash("Stats added successfully!", "success")
        return redirect(url_for('home.index'))

    players = Player.query.all()
    games = Game.query.all()
    return render_template('add_stats.html', players=players, games=games)


@players_bp.route('/players/<int:player_id>')
def player_stats(player_id):
    from app.models import Stat, Player  # Delay import
    player = Player.query.get_or_404(player_id)
    stats = Stat.query.filter_by(player_id=player_id).all()
    return render_template('player_stats.html', player=player, stats=stats)


@players_bp.route('/players/add_player', methods=['GET', 'POST'])
# @role_required(["admin", "coach"])
def add_player():
    from app.models import Team, Player
    from .forms import AddPlayerForm
    from app import db

    form = AddPlayerForm()

    # Populate the team choices from the database
    form.team_ids.choices = [(team.id, team.name) for team in Team.query.all()]

    if form.validate_on_submit():
        # Create a new player
        new_player = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            position=form.position.data,
        )

        # Associate the player with the selected teams
        selected_teams = Team.query.filter(Team.id.in_(form.team_ids.data)).all()
        new_player.teams.extend(selected_teams)

        # Save the player to the database
        db.session.add(new_player)
        db.session.commit()

        flash(f'Player "{new_player.first_name} {new_player.last_name}" added successfully!', 'success')
        return redirect(url_for('players.add_player'))

    return render_template('add_player.html', form=form)


@players_bp.route('/players/edit_player/<int:player_id>')
# @role_required("admin")
def edit_player(player_id):
    from app.models import Team, Player
    from app import db
    from .forms import EditPlayerForm
    player = Player.query.get_or_404(player_id)
    form = EditPlayerForm(obj=player)
    form.team_id.choices = [(team.id, team.name) for team in Team.query.all()]

    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.position = form.position.data
        player.team_id = form.team_id.data

        db.session.commit()
        flash(f'Player "{player.first_name} {player.last_name}" edited successfully!', 'success')
        return redirect(url_for('players.edit_player', player_id=player.id))
    return render_template('edit_player.html', player=player, form=form, teams=form.team_id.choices)
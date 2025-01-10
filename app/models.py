from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), index=True, nullable=False, default='user') # user, coach, admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(80), nullable=False)
    school_name = db.Column(db.String(80), unique=False, nullable=False)
    school_mascot = db.Column(db.String(80), nullable=False)
    uil_conference = db.Column(db.String(80), nullable=False)
    uil_region = db.Column(db.String(80), nullable=False)
    uil_district = db.Column(db.String(80), nullable=False)
    primary_color = db.Column(db.String(80), nullable=False)
    secondary_color = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    street = db.Column(db.String(80), nullable=False)
    zip = db.Column(db.String(80), nullable=False)
    teams = db.relationship('Team', back_populates='school', cascade="all, delete-orphan")

    # Explicitly define players relationship
    players = db.relationship(
        'Player',
        secondary='team_players',  # Association table
        primaryjoin='School.id == Team.school_id',  # Link School to Team
        secondaryjoin='Player.id == team_players.c.player_id',  # Link Team to Player
        viewonly=True,  # Prevent accidental updates
        back_populates='schools'
    )


team_players = db.Table(
    'team_players',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True)
)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade_level = db.Column(db.String(20), nullable=False)  # Varsity, JV, etc.
    gender = db.Column(db.String(20), nullable=False)
    sport = db.Column(db.String(80), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

    school = db.relationship('School', back_populates='teams')
    players = db.relationship('Player', secondary=team_players, back_populates='teams')
    games = db.relationship('Game', back_populates='team', cascade="all, delete-orphan")


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=False)

    # Relationship for teams via a secondary table
    teams = db.relationship('Team', secondary='team_players', back_populates='players')

    # Relationship for schools via teams
    schools = db.relationship(
        'School',
        secondary='team_players',
        primaryjoin='Player.id == team_players.c.player_id',
        secondaryjoin='Team.school_id == School.id',
        viewonly=True  # Prevent accidental updates
    )

    # Add the stats relationship
    stats = db.relationship(
        'Stat',
        back_populates='player',  # Matches back_populates in Stat
        cascade="all, delete-orphan"  # Cascade deletes stats if the player is deleted
    )


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)  # Home team
    opponent_id = db.Column(db.Integer, nullable=False)  # Away team
    score_team = db.Column(db.Integer)
    score_opponent = db.Column(db.Integer)

    team = db.relationship('Team', back_populates='games')
    stats = db.relationship('Stat', back_populates='game', cascade="all, delete-orphan")
    box_scores = db.relationship('BoxScore', back_populates='game', cascade='all, delete-orphan')

class BoxScore(db.Model):
    __tablename__ = 'box_scores'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    points = db.Column(db.Integer, default=0)  # For generic stats
    stats = db.Column(JSON, nullable=True)  # JSON field for sport-specific stats

    game = db.relationship('Game', back_populates='box_scores')
    team = db.relationship('Team')

class Sport(db.Model):
    __tablename__ = 'sports'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    stats = db.Column(JSON, nullable=False)  # Store stats as a JSON field

class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    # Add the back_populates relationship
    player = db.relationship('Player', back_populates='stats')
    game = db.relationship('Game', back_populates='stats')

    # Other fields...
    touchdowns = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    passing_yards = db.Column(db.Integer, default=0)
    completions = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=0)
    rushing_yards = db.Column(db.Integer, default=0)
    receiving_yards = db.Column(db.Integer, default=0)
    receptions = db.Column(db.Integer, default=0)
    tackles = db.Column(db.Integer, default=0)
    sacks = db.Column(db.Integer, default=0)
    interceptions_defense = db.Column(db.Integer, default=0)
    fumbles = db.Column(db.Integer, default=0)
    fumble_recoveries = db.Column(db.Integer, default=0)
    field_goals_made = db.Column(db.Integer, default=0)
    field_goals_attempted = db.Column(db.Integer, default=0)
    field_goal_yards = db.Column(db.Integer, default=0)
    extra_points_made = db.Column(db.Integer, default=0)
    extra_points_attempted = db.Column(db.Integer, default=0)
    punt_yards = db.Column(db.Integer, default=0)
    number_of_punts = db.Column(db.Integer, default=0)
    kick_return_yards = db.Column(db.Integer, default=0)
    punt_return_yards = db.Column(db.Integer, default=0)

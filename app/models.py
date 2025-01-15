from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

# db = SQLAlchemy()

# User Model (unchanged)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}, Email: {self.email}>"

# School Model
class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(100), nullable=False)
    school_mascot = db.Column(db.String(50), nullable=False)
    district_name = db.Column(db.String(100), nullable=False)
    uil_conference = db.Column(db.String(100), nullable=False)
    uil_region = db.Column(db.String(100), nullable=False)
    uil_district = db.Column(db.String(100), nullable=False)
    primary_color = db.Column(db.String(100), nullable=False)
    secondary_color = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)

    # Relationships
    teams = db.relationship('Team', back_populates='school', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<School {self.school_name}, Mascot: {self.school_mascot}>"

# Sport Model
class Sport(db.Model):
    __tablename__ = 'sports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    stats_definitions = db.Column(db.JSON, nullable=False)  # Dynamic stats structure
    season_start = db.Column(db.DateTime, nullable=False)
    season_end = db.Column(db.DateTime, nullable=False)

    teams = db.relationship('Team', back_populates='sport')

    def __repr__(self):
        return f"<Sport {self.name}>"

# Team Model
class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    # Relationships
    school = db.relationship('School', back_populates='teams')
    sport = db.relationship('Sport')
    players = db.relationship('Player', back_populates='team', cascade='all, delete-orphan')
    home_games = db.relationship('Game', foreign_keys='Game.home_team_id', back_populates='home_team')
    away_games = db.relationship('Game', foreign_keys='Game.away_team_id', back_populates='away_team')

    def __repr__(self):
        return f"<Team {self.sport.name} ({self.grade_level}, {self.gender}), School: {self.school.school_name}>"

# Game Model
class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)

    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    stats = db.relationship('GameStats', back_populates='game', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Game {self.home_team.school.school_name} vs {self.away_team.school.school_name} on {self.date}>"

# GameStats Model
class GameStats(db.Model):
    __tablename__ = 'game_stats'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    stats = db.Column(db.JSON, nullable=False)  # Store all stats for the game in a JSON format

    # Relationships
    game = db.relationship('Game', back_populates='stats')
    team = db.relationship('Team')

    def __repr__(self):
        return f"<GameStats Game ID: {self.game_id}, Team: {self.team_id}>"

# Player Model
class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    # Relationships
    team = db.relationship('Team', back_populates='players')
    player_stats = db.relationship('PlayerStats', back_populates='player', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Player {self.first_name} {self.last_name}, Position: {self.position}, Team: {self.team_id}>"

# PlayerStats Model
class PlayerStats(db.Model):
    __tablename__ = 'player_stats'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    stats = db.Column(db.JSON, nullable=False)  # Store player-specific stats for the game

    # Relationships
    game = db.relationship('Game')
    player = db.relationship('Player', back_populates='player_stats')

    def __repr__(self):
        return f"<PlayerStats Player ID: {self.player_id}, Game ID: {self.game_id}>"

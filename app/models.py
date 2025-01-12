from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON
from app import db

# db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}, Email: {self.email}>"

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
    street = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(100), nullable=False)

    # Relationships
    teams = db.relationship('Team', back_populates='school', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<School {self.school_name}, Mascot: {self.school_mascot}>"

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    score_home = db.Column(db.Integer, nullable=True)
    score_away = db.Column(db.Integer, nullable=True)

    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_games')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_games')
    box_scores = db.relationship('BoxScore', back_populates='game', cascade='all, delete-orphan')
    stats = db.relationship('Stat', back_populates='game', cascade='all, delete-orphan')
    quarter_stats = db.relationship('PlayerQuarterStats', back_populates='game', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Game ID: {self.id}, Date: {self.date}, Home: {self.home_team_id}, Away: {self.away_team_id}>"

class BoxScore(db.Model):
    __tablename__ = 'box_scores'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)  # Link to the Game
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)  # Link to the Team
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)  # Opponent team
    points = db.Column(db.Integer, nullable=False)
    stat_data = db.Column(db.JSON, nullable=True)  # Flexible field for stats

    # Relationships
    game = db.relationship('Game', back_populates='box_scores')
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_box_scores')  # Explicit
    # foreign
    # key for team
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_box_scores')  # Explicit
    # foreign
    # key for opponent

    def __repr__(self):
        return f"<BoxScore Game: {self.game_id}, Team: {self.home_team_id}, Opponent: {self.away_team_id}>"

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    # Relationships
    school = db.relationship('School', back_populates='teams')
    sport = db.relationship('Sport', back_populates='teams')
    home_games = db.relationship('Game', foreign_keys='Game.home_team_id', back_populates='home_team')
    away_games = db.relationship('Game', foreign_keys='Game.away_team_id', back_populates='away_team')
    home_box_scores = db.relationship(
        'BoxScore',
        foreign_keys='BoxScore.home_team_id',
        back_populates='home_team',
        cascade='all, delete-orphan'
    )
    away_box_scores = db.relationship(
        'BoxScore',
        foreign_keys='BoxScore.away_team_id',
        back_populates='away_team',
        cascade='all, delete-orphan'
    )

    players = db.relationship('Player', secondary='team_players', back_populates='teams')

    def __repr__(self):
        return f"<Team {self.sport.name} ({self.grade_level}, {self.gender}), School: {self.school_id}>"

team_players = db.Table(
    'team_players',
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('players.id'), primary_key=True)
)

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)

    # Relationship for teams via a secondary table
    sport = db.relationship('Sport', back_populates='players')
    teams = db.relationship('Team', secondary='team_players', back_populates='players')

    # Add the stats relationship
    stats = db.relationship(
        'Stat',
        back_populates='player',  # Matches back_populates in Stat
        cascade="all, delete-orphan"  # Cascade deletes stats if the player is deleted
    )
    quarter_stats = db.relationship('PlayerQuarterStats', back_populates='player', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Player {self.first_name} {self.last_name}, Sport: {self.sport.name}>"


class Sport(db.Model):
    __tablename__ = 'sports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    stats_definitions = db.Column(db.JSON, nullable=False)  # Define stats as a JSON object

    # Relationships
    teams = db.relationship('Team', back_populates='sport', cascade='all, delete-orphan')
    players = db.relationship('Player', back_populates='sport', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Sport {self.name}>"

class Stat(db.Model):
    __tablename__ = 'stats'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    stat_data = db.Column(db.JSON, nullable=True)  # Flexible field for player stats
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='stats')
    game = db.relationship('Game', back_populates='stats')

    def __repr__(self):
        return f"<Stat Player: {self.player_id}, Game: {self.game_id}, Data: {self.stat_data}>"

class PlayerQuarterStats(db.Model):
    __tablename__ = 'player_quarter_stats'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    quarter = db.Column(db.Integer, nullable=False)  # Quarter number (1, 2, 3, 4, or overtime)
    stat_data = db.Column(db.JSON, nullable=True)  # Stats for the quarter
    sport_id = db.Column(db.Integer, db.ForeignKey('sports.id'), nullable=False)  # Link to Sport

    # Relationships
    player = db.relationship('Player', back_populates='quarter_stats')
    game = db.relationship('Game', back_populates='quarter_stats')
    sport = db.relationship('Sport')

    def __repr__(self):
        return f"<PlayerQuarterStats Player: {self.player_id}, Game: {self.game_id}, Quarter: {self.quarter}>"

import json
import os
from datetime import timedelta, datetime
from random import randint

from faker import Faker

from run import app  # Import the globally initialized app
from app.extensions import db
from app.models import Sport, Team, Player, School, Game, PlayerStats


def reset_database():
    db.drop_all()
    print("All tables dropped successfully.")
    db.create_all()
    print("All tables created successfully.")

def seed_sports():
    """Seed the database with predefined sports."""
    print("Seeding sports...")
    sports_stats = {
        "Football": ["Passing Yards", "Rushing Yards", "Receiving Yards", "Tackles", "Sacks"],
        "Basketball": ["Points", "Rebounds", "Assists", "Steals", "Blocks"],
        "Baseball": ["Runs", "Hits", "Errors", "RBIs", "Strikeouts"],
    }

    season_dates = {
        "Football": {"start": datetime(datetime.now().year, 8, 1), "end": datetime(datetime.now().year, 12, 1)},
        "Basketball": {"start": datetime(datetime.now().year, 11, 1), "end": datetime(datetime.now().year + 1, 3, 1)},
        "Baseball": {"start": datetime(datetime.now().year, 2, 1), "end": datetime(datetime.now().year, 6, 1)},
    }

    for sport_name, stats in sports_stats.items():
        season = season_dates.get(sport_name, {"start": datetime.now(), "end": datetime.now() + timedelta(days=120)})
        sport = Sport.query.filter_by(name=sport_name).first()
        if not sport:
            sport = Sport(
                name=sport_name,
                stats_definitions=stats,
                season_start=season["start"],
                season_end=season["end"]
            )
            db.session.add(sport)

    db.session.commit()
    print("Sports seeded successfully.")


def seed_schools():
    """Seed schools from JSON files."""
    print("Seeding schools...")
    data_dir = "data/schools"
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            with open(os.path.join(data_dir, filename), "r") as f:
                schools_data = json.load(f)

                for school_data in schools_data:
                    school = School(**school_data)
                    db.session.add(school)

    db.session.commit()
    print("Schools seeded successfully.")


def seed_teams_from_directory():
    directory_path = "data/school_teams"
    """Seed teams from all JSON files in the specified directory."""

    print(f"Seeding teams from all JSON files in {directory_path}...")

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {file_path}")

            with open(file_path, 'r') as f:
                school_teams_data = json.load(f)

            for school_name, levels in school_teams_data.items():
                # Find the school in the database
                school = School.query.filter_by(school_name=school_name).first()
                if not school:
                    print(f"School not found in the database, skipping: {school_name}")
                    continue

                for grade_level, genders in levels.items():
                    for gender, sports in genders.items():
                        for sport_name in sports:
                            # Find the sport in the database
                            sport = Sport.query.filter_by(name=sport_name).first()
                            if not sport:
                                print(f"Sport not found in the database, skipping: {sport_name}")
                                continue

                            # Check if the team already exists
                            existing_team = Team.query.filter_by(
                                school_id=school.id,
                                sport_id=sport.id,
                                grade_level=grade_level,
                                gender=gender
                            ).first()

                            if existing_team:
                                print(f"Team already exists: {school_name} - {grade_level} {gender} - {sport_name}")
                                continue

                            # Create a new team
                            new_team = Team(
                                school_id=school.id,
                                sport_id=sport.id,
                                grade_level=grade_level,
                                gender=gender
                            )
                            db.session.add(new_team)
                            print(f"Added team: {school_name} - {grade_level} {gender} - {sport_name}")

    # Commit the changes to the database
    db.session.commit()
    print("All teams seeded successfully.")


def seed_players():
    """Seed players for each team."""
    print("Seeding players...")
    fake = Faker()
    teams = Team.query.all()

    for team in teams:
        positions = team.sport.stats_definitions
        for _ in range(15):  # Create 15 players per team
            # Generate names based on team gender
            if team.gender.lower() == "boys":
                first_name = fake.first_name_male()
            elif team.gender.lower() == "girls":
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name()

            last_name = fake.last_name()

            player = Player(
                first_name=first_name,
                last_name=last_name,
                position=fake.random_element(positions),
                team_id=team.id,
            )
            db.session.add(player)

    db.session.commit()
    print("Players seeded successfully.")


def seed_games():
    """Generate games and associated stats."""
    print("Seeding games...")
    teams = Team.query.all()
    season_start = datetime.now()
    season_end = season_start + timedelta(weeks=10)
    fake = Faker()

    for home_team in teams:
        opponent_teams = Team.query.filter(Team.id != home_team.id, Team.sport_id == home_team.sport_id).all()

        for away_team in opponent_teams:
            game_date = season_start + timedelta(days=randint(0, (season_end - season_start).days))
            home_score = randint(0, 50)
            away_score = randint(0, 50)

            # Create the game
            game = Game(
                date=game_date,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_score=home_score,
                away_score=away_score
            )
            db.session.add(game)
            db.session.flush()

            # Generate player stats for the game
            for player in home_team.players:
                stats = {
                    "Passing Yards": randint(0, 300),
                    "Tackles": randint(0, 15),
                    "Rushing Yards": randint(0, 200)
                }
                player_stats = PlayerStats(player_id=player.id, game_id=game.id, stats=stats, team_id=game.home_team_id)
                db.session.add(player_stats)

            for player in away_team.players:
                stats = {
                    "Passing Yards": randint(0, 300),
                    "Tackles": randint(0, 15),
                    "Rushing Yards": randint(0, 200)
                }
                player_stats = PlayerStats(player_id=player.id, game_id=game.id, stats=stats, team_id=game.away_team_id)
                db.session.add(player_stats)

    db.session.commit()
    print("Games and stats seeded successfully.")

def run_seed():
    """Master function to seed the database."""
    with app.app_context():  # Use app context for all operations
        reset_database()
        seed_sports()
        seed_schools()
        seed_teams_from_directory()
        seed_players()
        seed_games()


if __name__ == "__main__":
    run_seed()

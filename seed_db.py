import json
import os
from datetime import timedelta, datetime
from random import randint

from faker import Faker

from run import app  # Import the globally initialized app
from app.extensions import db
from app.models import Sport, Team, Player, School, Game


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
            player = Player(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                position=fake.random_element(positions),
                team_id=team.id,
            )
            db.session.add(player)

    db.session.commit()
    print("Players seeded successfully.")


def seed_games():
    """Generate games with accurate dates, enforce season rules, and restrict games to the same district."""
    print("Seeding games...")
    teams = Team.query.all()

    # Define sport-specific seasons
    sport_seasons = {
        "Football": {"start": datetime(datetime.now().year, 8, 1), "end": datetime(datetime.now().year, 12, 1)},
        "Basketball": {"start": datetime(datetime.now().year, 11, 1), "end": datetime(datetime.now().year + 1, 3, 1)},
        "Baseball": {"start": datetime(datetime.now().year, 2, 1), "end": datetime(datetime.now().year, 6, 1)},
    }

    # UIL-specific game limits
    max_games_per_team = {
        "Football": 10,
        "Basketball": 30,
        "Baseball": 20,
    }

    for home_team in teams:
        sport_name = home_team.sport.name

        # Get the sport season and game limit
        season = sport_seasons.get(sport_name)
        if not season:
            print(f"Skipping {sport_name}, as it does not have a defined season.")
            continue

        max_games = max_games_per_team.get(sport_name, 10)

        # Filter opponents by district and sport
        opponent_teams = Team.query.join(School).filter(
            Team.id != home_team.id,  # Exclude the home team
            Team.sport_id == home_team.sport_id,  # Same sport
            School.uil_district == home_team.school.uil_district  # Match UIL district
        ).all()

        # Generate up to the maximum allowed games
        generated_games = 0
        while generated_games < max_games and opponent_teams:
            # Randomly pick an opponent from the same district
            away_team = opponent_teams[randint(0, len(opponent_teams) - 1)]

            # Generate a random game date within the season
            game_date = season["start"] + timedelta(
                days=randint(0, (season["end"] - season["start"]).days)
            )

            # Check if this game already exists
            existing_game = Game.query.filter(
                ((Game.home_team_id == home_team.id) & (Game.away_team_id == away_team.id)) |
                ((Game.home_team_id == away_team.id) & (Game.away_team_id == home_team.id)),
                Game.date == game_date
            ).first()

            if not existing_game:
                # Create and add the game
                game = Game(
                    date=game_date,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    home_score=randint(0, 50),
                    away_score=randint(0, 50),
                )
                db.session.add(game)
                generated_games += 1

    db.session.commit()
    print("Games seeded successfully.")



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

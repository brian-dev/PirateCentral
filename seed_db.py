import json
import os
from datetime import datetime, timedelta
from random import randint
from faker import Faker

from run import app  # Import your Flask app instance
from app import db
from app.models import School, Team, Game, Player, BoxScore, Sport


def load_schools_from_directory(data_dir):
    """
    Load all schools from JSON files in a directory and add them to the database.
    Assumes that each JSON file has a list of school objects matching the School model fields.
    """
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):  # Process only JSON files
            file_path = os.path.join(data_dir, filename)
            with open(file_path, 'r') as f:
                schools_data = json.load(f)

            for school_data in schools_data:
                school = School(**school_data)
                db.session.add(school)

            print(f"Imported {len(schools_data)} schools from {filename}")

    db.session.commit()
    print("All schools imported successfully.")


def seed_teams_for_existing_schools():
    """
    Reads multiple JSON files from the 'data/school_teams' directory and
    seeds/upserts teams for the schools in your existing database.
    """
    directory_path = 'data/school_teams'

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)

            for school_name, levels_dict in data.items():
                school = School.query.filter_by(school_name=school_name).first()

                if not school:
                    print(f"School not found in DB, skipping: {school_name}")
                    continue

                for level, gender_dict in levels_dict.items():
                    for gender, sports in gender_dict.items():
                        for sport in sports:
                            existing_team = Team.query.filter_by(
                                grade_level=level,
                                gender=gender,
                                sport=sport,
                                school_id=school.id
                            ).first()

                            if existing_team:
                                print(f"Team already exists: {school_name} - {level} {gender} - {sport}")
                            else:
                                new_team = Team(
                                    grade_level=level,
                                    gender=gender,
                                    sport=sport,
                                    school_id=school.id
                                )
                                db.session.add(new_team)

    db.session.commit()
    print("Finished seeding teams from all files.")

def seed_sports_and_stats():
    """
    Seed the database with predefined sports and their stats.
    """
    print("Seeding sports and their stats...")

    sports_stats = {
        "Football": ["Passing Yards", "Rushing Yards", "Receiving Yards", "Tackles", "Sacks"],
        "Baseball": ["Runs", "Hits", "Errors", "RBIs", "Strikeouts"],
        "Basketball": ["Points", "Rebounds", "Assists", "Steals", "Blocks"],
        "Softball": ["Runs", "Hits", "Errors", "RBIs", "Strikeouts"],
        "Cross Country": ["Finish Time", "Placement"],
        "Golf": ["Strokes", "Par", "Birdies", "Eagles"],
        "Wrestling": ["Takedowns", "Pins", "Escapes"],
    }

    for sport_name, stats in sports_stats.items():
        # Check if the sport already exists
        existing_sport = Sport.query.filter_by(name=sport_name).first()
        if existing_sport:
            print(f"Sport '{sport_name}' already exists. Skipping...")
            continue

        # Create and add the new sport
        new_sport = Sport(name=sport_name, stats=stats)
        db.session.add(new_sport)

    db.session.commit()
    print("Sports and their stats seeded successfully.")



def generate_mock_schedule():
    """
    Generate a mock schedule for each team in the database based on UIL rules,
    along with sport-specific stats for each game.
    """
    print("Generating mock schedules...")
    teams = Team.query.all()

    season_dates = {
        "Football": {
            "start": datetime(datetime.now().year, 8, 1) + timedelta(weeks=3, days=-datetime(datetime.now().year, 8, 1).weekday() - 3),
            "end": datetime(datetime.now().year, 11, 1) + timedelta(days=(4 - datetime(datetime.now().year, 11, 1).weekday())),
        },
        # Other sports...
    }

    default_season_start = datetime.now() + timedelta(days=7)
    default_season_end = default_season_start + timedelta(weeks=16)

    for team in teams:
        sport = team.sport
        sport_stats = {sport.name: sport.stats for sport in Sport.query.all()}
        sport_dates = season_dates.get(sport, {"start": default_season_start, "end": default_season_end})
        season_start = sport_dates["start"]
        season_end = sport_dates["end"]

        if season_start >= season_end:
            print(f"Invalid date range for {sport}. Skipping schedule generation.")
            continue

        district_teams = Team.query.filter(
            Team.school_id != team.school_id,
            Team.grade_level == team.grade_level,
            Team.gender == team.gender,
            Team.sport == team.sport
        ).all()

        for opponent in district_teams:
            for is_home in [True, False]:
                game_date = season_start + timedelta(days=randint(0, (season_end - season_start).days))
                team_score = randint(40, 100)
                opponent_score = randint(40, 100)

                existing_game = Game.query.filter_by(
                    team_id=team.id if is_home else opponent.id,
                    opponent_id=opponent.id if is_home else team.id,
                    date=game_date
                ).first()

                if not existing_game:
                    new_game = Game(
                        date=game_date,
                        team_id=team.id if is_home else opponent.id,
                        opponent_id=opponent.id if is_home else team.id,
                        score_team=team_score,
                        score_opponent=opponent_score
                    )
                    db.session.add(new_game)
                    db.session.flush()

                    # Generate box scores with sport-specific stats
                    box_score_team = BoxScore(
                        game_id=new_game.id,
                        team_id=team.id,
                        points=team_score,
                        stats={stat: randint(1, 10) for stat in sport_stats},
                    )
                    box_score_opponent = BoxScore(
                        game_id=new_game.id,
                        team_id=opponent.id,
                        points=opponent_score,
                        stats={stat: randint(1, 10) for stat in sport_stats},
                    )
                    db.session.add(box_score_team)
                    db.session.add(box_score_opponent)

    db.session.commit()
    print("Mock schedules and box scores generated for all teams.")


def generate_players_for_teams():
    """
    Generate random players for each team with positions based on the sport.
    """
    print("Generating players...")
    fake = Faker()
    sport_positions = {
        "Basketball": {"positions": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
                       "average_per_position": 2},
        "Baseball": {
            "positions": ["Pitcher", "Catcher", "First Base", "Second Base", "Third Base", "Short Stop", "Right Field",
                          "Center Field", "Left Field"], "average_per_position": 3},
        "Soccer": {"positions": ["Goalkeeper", "Fullback", "Midfielder", "Forward"], "average_per_position": 4},
        "Football": {"positions": ["Quarterback", "Running Back", "Wide Receiver", "Tight End", "Offensive Line",
                                   "Defensive Line", "Linebacker", "Defensive Back", "Kicker", "Punter", "Returner"],
                     "average_per_position": 5},
        "Volleyball": {"positions": ["Setter", "Outside Hitter", "Middle Blocker", "Libero"],
                       "average_per_position": 2},
        "Track and Field": {"positions": ["Sprinter", "Distance Runner", "Thrower", "Jumper"],
                            "average_per_position": 2},
    }

    default_number_of_players = 6
    teams = Team.query.all()

    for team in teams:
        print(f"Generating players for team: {team.sport} ({team.grade_level} {team.gender})")

        sport_data = sport_positions.get(team.sport, None)

        if sport_data:
            positions = sport_data["positions"]
            average_per_position = sport_data["average_per_position"]
            number_of_players = len(positions) * average_per_position
        else:
            positions = ["Player"]
            number_of_players = default_number_of_players

        for _ in range(number_of_players):
            position = fake.random_element(positions)

            if team.gender.lower() == "boys":
                first_name = fake.first_name_male()
            elif team.gender.lower() == "girls":
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name()

            last_name = fake.last_name()

            # Ensure no duplicate player is added to the same team
            existing_player = next(
                (p for p in team.players if p.first_name == first_name and p.last_name == last_name), None
            )
            if existing_player:
                continue

            player = Player(
                first_name=first_name,
                last_name=last_name,
                position=position,
            )
            db.session.add(player)
            db.session.flush()

            team.players.append(player)

        db.session.commit()

    print("All players generated and added to the database.")


def run_seed():
    """
    Master function to run all seeding steps in one app context.
    """
    with app.app_context():
        # 1. Load schools from data/schools/*.json
        data_directory = 'data/schools'
        load_schools_from_directory(data_directory)

        # 2. Seed or upsert teams for existing schools from data/school_teams/*.json
        seed_teams_for_existing_schools()

        # 3. Generate a mock schedule for each team
        generate_mock_schedule()

        # 4. Generate players for each team
        generate_players_for_teams()

        seed_sports_and_stats()


if __name__ == "__main__":
    run_seed()

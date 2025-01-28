import json
import os
import random
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
        "Football": [
            "Passing Yards",  # Total passing yards
            "Passing Touchdowns",  # Total passing touchdowns
            "Interceptions Thrown",  # Total interceptions thrown
            "Rushing Yards",  # Total rushing yards
            "Rushing Touchdowns",  # Total rushing touchdowns
            "Receiving Yards",  # Total receiving yards
            "Receiving Touchdowns",  # Total receiving touchdowns
            "Tackles",  # Total tackles
            "Sacks",  # Total sacks
            "Interceptions",  # Defensive interceptions
            "Fumbles Recovered",  # Fumbles recovered
            "Field Goals Made",  # Kicking field goals made
            "Field Goals Attempted"  # Kicking field goals attempted
        ],
        "Basketball": [
            "Points",  # Total points scored
            "Rebounds",  # Total rebounds (offensive and defensive)
            "Assists",  # Total assists
            "Steals",  # Total steals
            "Blocks",  # Total blocks
            "Turnovers",  # Total turnovers
            "Field Goal Percentage",  # Shooting accuracy from the field
            "Three-Point Percentage",  # Shooting accuracy for three-pointers
            "Free Throw Percentage",  # Shooting accuracy for free throws
            "Minutes Played",  # Total minutes played
            "Personal Fouls"  # Number of fouls committed
        ],
        "Baseball": [
            "Runs",  # Total runs scored
            "Hits",  # Total hits
            "Home Runs",  # Total home runs
            "RBIs",  # Runs batted in
            "Stolen Bases",  # Total stolen bases
            "Caught Stealing",  # Number of times caught stealing
            "Batting Average",  # Player's batting average
            "On-Base Percentage",  # On-base percentage
            "Slugging Percentage",  # Slugging percentage
            "Errors",  # Number of fielding errors
            "Strikeouts (Pitcher)",  # Strikeouts by pitchers
            "Walks Allowed",  # Walks allowed by pitchers
            "ERA",  # Earned run average (pitchers)
            "Innings Pitched"  # Innings pitched (pitchers)
        ],
        "Soccer": [
            "Goals",  # Total goals scored
            "Assists",  # Total assists
            "Shots",  # Total shots taken
            "Shots on Target",  # Total shots on target
            "Passes Completed",  # Total successful passes
            "Pass Accuracy",  # Pass accuracy percentage
            "Tackles",  # Total tackles made
            "Interceptions",  # Total interceptions
            "Fouls Committed",  # Total fouls committed
            "Fouls Won",  # Total fouls won
            "Yellow Cards",  # Total yellow cards received
            "Red Cards",  # Total red cards received
            "Saves",  # Goalkeeper saves
            "Clean Sheets"  # Goalkeeper clean sheets
        ],
        "Volleyball": [
            "Kills",  # Total kills (successful attacks)
            "Assists",  # Total assists
            "Digs",  # Total digs (defensive saves)
            "Blocks",  # Total blocks
            "Aces",  # Total service aces
            "Service Errors",  # Total service errors
            "Hitting Percentage",  # Hitting accuracy percentage
            "Set Assists",  # Total assists as a setter
            "Reception Errors",  # Errors on receiving serves
            "Serve Percentage",  # Serve success rate
            "Total Points"  # Total points contributed
        ]
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
    """Seed players for each team with realistic position distributions."""
    print("Seeding players...")
    fake = Faker()
    teams = Team.query.all()

    # Define realistic player distributions for each sport
    sport_position_distributions = {
        "Football": {
            "Quarterback": 2,
            "Running Back": 4,
            "Wide Receiver": 5,
            "Linebacker": 6,
            "Cornerback": 4,
            "Safety": 4,
            "Tight End": 3,
            "Offensive Lineman": 10,
            "Defensive Lineman": 8,
            "Kicker": 2
        },
        "Basketball": {
            "Point Guard": 3,
            "Shooting Guard": 3,
            "Small Forward": 3,
            "Power Forward": 3,
            "Center": 3
        },
        "Baseball": {
            "Pitcher": 5,
            "Catcher": 2,
            "First Baseman": 2,
            "Second Baseman": 2,
            "Shortstop": 2,
            "Third Baseman": 2,
            "Left Fielder": 3,
            "Center Fielder": 3,
            "Right Fielder": 3
        },
        "Soccer": {
            "Goalkeeper": 2,
            "Defender": 8,
            "Midfielder": 8,
            "Forward": 4
        },
        "Volleyball": {
            "Setter": 2,
            "Outside Hitter": 4,
            "Opposite Hitter": 3,
            "Middle Blocker": 3,
            "Libero": 2,
            "Defensive Specialist": 2
        },
        "Cross Country": {
            "Runner": 8
        },
        # Add more sports and their distributions as needed
    }

    for team in teams:
        # Get position distribution for the sport or fallback to a default
        position_distribution = sport_position_distributions.get(team.sport.name, {"Player": 15})

        for position, count in position_distribution.items():
            for _ in range(count):
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
                    position=position,
                    team_id=team.id,
                )
                db.session.add(player)

    db.session.commit()
    print("Players seeded successfully.")

def seed_games():
    """Generate games and associated stats."""
    print("Seeding games...")
    teams = Team.query.all()
    sports_season_dates = {
        sport.name: (sport.season_start, sport.season_end)
        for sport in Sport.query.all()
    }
    # fake = Faker()
    # total_weeks = 10
    # total_weeks = (season_end - season_start).days // 7
    position_specific_stats = {
        "Football": {
            "Quarterback": {
                "Passing Yards": (200, 400),
                "Passing Touchdowns": (2, 5),
                "Interceptions Thrown": (0, 3),
                "Rushing Yards": (10, 50),
            },
            "Running Back": {
                "Rushing Yards": (50, 200),
                "Rushing Touchdowns": (1, 3),
                "Receiving Yards": (10, 50),
                "Tackles": (0, 1),
            },
            "Wide Receiver": {
                "Receiving Yards": (50, 200),
                "Receiving Touchdowns": (1, 3),
                "Rushing Yards": (0, 20),
            },
            "Linebacker": {
                "Tackles": (5, 15),
                "Sacks": (1, 5),
                "Interceptions": (0, 2),
            },
            "Cornerback": {
                "Tackles": (3, 10),
                "Interceptions": (0, 3),
                "Fumbles Recovered": (0, 1),
            },
            "Kicker": {
                "Field Goals Made": (1, 5),
                "Field Goals Attempted": (1, 7),
                "Extra Points": (0, 5),
            },
        },
        "Basketball": {
            "Point Guard": {
                "Points": (10, 30),
                "Assists": (5, 15),
                "Rebounds": (1, 5),
                "Steals": (1, 3),
                "Turnovers": (1, 5),
            },
            "Shooting Guard": {
                "Points": (15, 35),
                "Three-Point Percentage": (30, 50),
                "Rebounds": (2, 6),
            },
            "Small Forward": {
                "Points": (15, 25),
                "Rebounds": (5, 10),
                "Steals": (1, 3),
                "Field Goal Percentage": (40, 60),
            },
            "Power Forward": {
                "Points": (15, 25),
                "Rebounds": (8, 15),
                "Blocks": (1, 3),
                "Turnovers": (0, 2),
            },
            "Center": {
                "Points": (15, 25),
                "Rebounds": (10, 20),
                "Blocks": (1, 5),
            },
        },
        "Baseball": {
            "Pitcher": {
                "Strikeouts (Pitcher)": (5, 15),
                "ERA": (2.0, 5.0),
                "Walks Allowed": (0, 5),
                "Innings Pitched": (6, 9),
            },
            "Catcher": {
                "Hits": (1, 3),
                "RBIs": (0, 3),
                "Errors": (0, 1),
            },
            "Infielder": {
                "Hits": (1, 4),
                "RBIs": (1, 5),
                "Errors": (0, 2),
                "Runs": (1, 3),
            },
            "Outfielder": {
                "Hits": (1, 4),
                "Home Runs": (0, 2),
                "Runs": (1, 4),
            },
        },
        "Soccer": {
            "Forward": {
                "Goals": (1, 3),
                "Shots on Target": (3, 7),
                "Assists": (0, 2),
            },
            "Midfielder": {
                "Pass Accuracy": (75, 90),
                "Tackles": (1, 5),
                "Interceptions": (1, 3),
                "Assists": (1, 3),
            },
            "Defender": {
                "Tackles": (3, 8),
                "Interceptions": (2, 5),
                "Fouls Committed": (0, 3),
            },
            "Goalkeeper": {
                "Saves": (3, 10),
                "Clean Sheets": (0, 1),
                "Pass Accuracy": (50, 80),
            },
        },
        "Volleyball": {
            "Setter": {
                "Assists": (20, 50),
                "Service Errors": (0, 3),
                "Set Assists": (10, 30),
            },
            "Outside Hitter": {
                "Kills": (10, 25),
                "Blocks": (2, 6),
                "Digs": (5, 15),
            },
            "Middle Blocker": {
                "Blocks": (5, 15),
                "Kills": (5, 10),
            },
            "Libero": {
                "Digs": (15, 30),
                "Reception Errors": (0, 2),
            },
        },
    }

    for home_team in teams:
        # Get season dates for the team's sport
        sport_name = home_team.sport.name
        season_start, season_end = sports_season_dates.get(sport_name, (None, None))

        if not season_start or not season_end:
            print(f"Season dates not found for sport: {sport_name}. Skipping...")
            continue

        total_weeks = (season_end - season_start).days // 7

        # Filter potential opponents for the same sport
        opponents = [
            team for team in teams
            if team.id != home_team.id and team.sport_id == home_team.sport_id
        ]

        # Shuffle opponents to ensure randomness
        random.shuffle(opponents)

        # Assign one opponent per week
        for week in range(total_weeks):
            if not opponents:
                break  # No more opponents available

            # Select an opponent for this week
            away_team = opponents.pop(0)

            # Calculate game date for this week
            game_date = season_start + timedelta(weeks=week)
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

            # Generate stats for the home team
            position_stats = position_specific_stats.get(home_team.sport.name, {})
            for player in home_team.players:
                player_position = position_stats.get(player.position, {})
                stats = {
                    stat_name: randint(*ranges) if player_position else randint(0, 10)
                    for stat_name, ranges in player_position.items()
                }
                player_stats = PlayerStats(
                    player_id=player.id,
                    game_id=game.id,
                    stats=stats,
                    team_id=home_team.id
                )
                db.session.add(player_stats)

            # Generate stats for the away team
            for player in away_team.players:
                player_position = position_stats.get(player.position, {})
                stats = {
                    stat_name: randint(*ranges) if player_position else randint(0, 10)
                    for stat_name, ranges in player_position.items()
                }
                player_stats = PlayerStats(
                    player_id=player.id,
                    game_id=game.id,
                    stats=stats,
                    team_id=away_team.id
                )
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

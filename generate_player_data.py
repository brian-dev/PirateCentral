from faker import Faker
from app import db
from app.models import Team, Player

def generate_players_for_teams():
    """
    Generate random players for each team with positions based on the sport.
    Automatically determine the number of players based on the average per position per team.
    Assign male names for male teams and female names for female teams.
    Avoid duplicate player associations.
    """
    fake = Faker()

    # Define positions and average number of players per position for each sport
    sport_positions = {
        "Basketball": {"positions": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"], "average_per_position": 2},
        "Baseball": {"positions": ["Pitcher", "Catcher", "First Base", "Second Base", "Third Base", "Short Stop",
                                   "Right Field", "Center Field", "Left Field"], "average_per_position": 3},
        "Soccer": {"positions": ["Goalkeeper", "Fullback", "Midfielder", "Forward"], "average_per_position": 4},
        "Football": {"positions": ["Quarterback", "Running Back", "Wide Receiver", "Tight End", "Offensive Line",
                                   "Defensive Line", "Linebacker", "Defensive Back", "Kicker", "Punter", "Returner"], "average_per_position": 5},
        "Volleyball": {"positions": ["Setter", "Outside Hitter", "Middle Blocker", "Libero"], "average_per_position": 2},
        "Track and Field": {"positions": ["Sprinter", "Distance Runner", "Thrower", "Jumper"], "average_per_position": 2},
    }

    # Default number of players if no positions are defined
    default_number_of_players = 6

    # Get all teams from the database
    teams = Team.query.all()

    for team in teams:
        print(f"Generating players for team: {team.sport} ({team.grade_level} {team.gender})")

        # Get sport-specific positions and average players per position
        sport_data = sport_positions.get(team.sport, None)

        if sport_data:
            positions = sport_data["positions"]
            average_per_position = sport_data["average_per_position"]
            number_of_players = len(positions) * average_per_position
        else:
            positions = ["Player"]  # Generic position
            number_of_players = default_number_of_players

        for _ in range(number_of_players):
            # Assign positions randomly from the list
            position = fake.random_element(positions)

            # Generate a random player with gender-specific names
            if team.gender.lower() == "boys":
                first_name = fake.first_name_male()
            elif team.gender.lower() == "girls":
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name()

            last_name = fake.last_name()

            # Check if a player with the same name already exists in the team
            existing_player = (
                Player.query.join(Player.teams)
                .filter(Team.id == team.id, Player.first_name == first_name, Player.last_name == last_name)
                .first()
            )
            if existing_player:
                continue  # Skip if the player already exists for the team

            # Create a new player
            player = Player(
                first_name=first_name,
                last_name=last_name,
                position=position,
            )
            db.session.add(player)
            db.session.flush()  # Ensure player ID is generated before associating with the team

            # Associate the player with the current team
            team.players.append(player)

        # Commit after adding all players for the current team
        db.session.commit()

    print("All players generated and added to the database.")

if __name__ == "__main__":
    from app import create_app

    app = create_app()

    with app.app_context():
        generate_players_for_teams()

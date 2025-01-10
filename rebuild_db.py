from run import app
from app import db
from app.models import School, Team, Player, Game, Stat
import json

def reset_database():
    """Drops and recreates the database schema."""
    with app.app_context():  # Push the app context
        db.drop_all()
        print("All tables dropped successfully.")
        db.create_all()
        print("All tables created successfully.")

def load_schools_from_json(file_path):
    """Load schools from a JSON file and add them to the database."""
    with open('data/schools/1a_d1_schools.json', 'r') as f:
        schools_data = json.load(f)

    with app.app_context():  # Push the app context
        for school_data in schools_data:
            school = School(**school_data)  # Use unpacking to match the School model fields
            db.session.add(school)
        db.session.commit()
        print(f"Imported {len(schools_data)} schools successfully.")

if __name__ == "__main__":
    reset_database()
    # Uncomment the next line if you want to load data from a JSON file
    # load_schools_from_json('data/1a_d2_schools.json')


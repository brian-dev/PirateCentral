from run import app
from app import db
from app.models import School, Team, Player, Game
import json

def reset_database():
    """Drops and recreates the database schema."""
    with app.app_context():  # Push the app context
        db.drop_all()
        print("All tables dropped successfully.")
        db.create_all()
        print("All tables created successfully.")

if __name__ == "__main__":
    reset_database()


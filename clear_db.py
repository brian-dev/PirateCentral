from app import create_app, db
from app.models import Team, Player, Game, Stat, School  # Import your models

app = create_app()

with app.app_context():
    # Delete all rows from tables
    db.session.query(School).delete()
    db.session.query(Team).delete()
    db.session.query(Player).delete()
    db.session.query(Game).delete()
    db.session.query(Stat).delete()

    # Commit the changes
    db.session.commit()
    print("All table data cleared.")

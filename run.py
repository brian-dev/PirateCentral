from app import create_app
from app.extensions import db

app = create_app("config.DevelopmentConfig")

# Initialize the database
with app.app_context():
    db.create_all()  # Ensures tables are created

if __name__ == "__main__":
    app.run(debug=True)

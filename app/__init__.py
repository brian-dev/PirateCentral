from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sports.db'
    app.config['SECRET_KEY'] = 'this_is_my_secret_key'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = "users_bp.login"  # Use blueprint prefix
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Register blueprints
    from app.home import home_bp
    from app.players import players_bp
    from app.schools import schools_bp
    from app.teams import teams_bp
    from app.users import users_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(players_bp, url_prefix="/players")
    app.register_blueprint(schools_bp, url_prefix="/schools")
    app.register_blueprint(teams_bp, url_prefix="/teams")
    app.register_blueprint(users_bp)

    # Create database tables and configure user loader
    with app.app_context():
        from .models import User, Team, School, Player, Game, BoxScore, Sport, Stat  # Import models
        db.create_all()

        @login_manager.user_loader
        def load_user(user_id):
            """Callback to reload the user object from the user ID."""
            return User.query.get(int(user_id))

    return app

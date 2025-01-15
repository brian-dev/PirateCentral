from flask import Flask
from .extensions import db, migrate, login_manager, bootstrap
from .models import User

def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = "users_bp.login"
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

    with app.app_context():
        # Configure user loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    return app

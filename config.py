import os

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    # Ensure the instance folder exists
    INSTANCE_PATH = os.path.join(os.getcwd(), "instance")
    os.makedirs(INSTANCE_PATH, exist_ok=True)

    # Define the SQLite database URI in the instance folder
    DEFAULT_DB_PATH = f"sqlite:///{os.path.join(INSTANCE_PATH, 'sports.db')}"

    # Use environment variable DATABASE_URL if set, otherwise use the default SQLite path
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", DEFAULT_DB_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    DEBUG = False

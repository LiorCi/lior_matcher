import sqlalchemy
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from matcher.config import Config

db = SQLAlchemy()


def create_app():
    """Construct the application."""
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object('matcher.config.Config')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'matcher_secret_key'
    db.init_app(app)

    # create db 'matcher' schema if not exist
    engine = sqlalchemy.create_engine(app.config["DB_ENGINE"])
    create_str = f"CREATE DATABASE IF NOT EXISTS {app.config['DB_NAME']} ;"
    engine.execute(create_str)
    engine.execute("USE matcher")

    with app.app_context():
        # Imports
        from matcher import routes
        from matcher import models
        from matcher import model_view

        # Create tables for all models
        db.create_all()

        return app



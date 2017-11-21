import logging
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level='WARN')

# Instantiate the database
db = SQLAlchemy()


def create_app():
    # Instantiate the Flask app
    app = Flask(__name__)

    # Set the proper config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # Show us the config when debugging
    logging.debug(app.config)

    # Set up extensions
    db.init_app(app)

    # Register blueprints
    from project.api.views import users_blueprint
    app.register_blueprint(users_blueprint)

    return app

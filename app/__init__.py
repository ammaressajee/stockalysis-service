from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS (to allow communication with Angular frontend)
    CORS(app, supports_credentials=True)

    # Initialize db and migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes (ensure routes.py is correctly imported)
    from app.routes import routes
    app.register_blueprint(routes)

    return app

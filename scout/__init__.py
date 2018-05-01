from flask import Flask
from flask_jwt_extended import (JWTManager, jwt_required)
from flask_sqlalchemy import Model, SQLAlchemy

from scout.utils import compose_json_response
from config import app_config

db = SQLAlchemy()

# import models after db instantiation to avoid circular import
from scout.models import OperationException, User
from scout import api

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    JWTManager(app)
    db.init_app(app)

    # User
    @app.route('/me', methods=['GET'])
    @jwt_required
    def get_me(*args, **kwargs):
        return api.users.get_me(*args, **kwargs)

    return app
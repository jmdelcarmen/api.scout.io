from flask import Flask
from flask_jwt_extended import (JWTManager, jwt_required)
from flask_sqlalchemy import SQLAlchemy

from scout.utils import compose_json_response
from config import app_config

db = SQLAlchemy()

# import models after db instantiation to avoid circular import
from scout.models import OperationException, User, Visit
from scout.lib import YelpFusion
from scout import api

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    JWTManager(app)
    db.init_app(app)

    # Auth
    @app.route('/auth/signup', methods=['POST'])
    def signup(*args, **kwargs):
        return api.auth.signup(*args, **kwargs)

    @app.route('/auth/login', methods=['POST'])
    def login(*args, **kwargs):
        return api.auth.login(*args, **kwargs)

    @app.route('/me', methods=['GET'])
    @jwt_required
    def get_me(*args, **kwargs):
        return api.users.get_me(*args, **kwargs)

    # Trips
    @app.route('/trips', methods=['POST'])
    @jwt_required
    def create_trip(*args, **kwargs):
        return api.visit.create_trip(*args, **kwargs)


    # Test
    @app.route('/test', methods=['GET'])
    def generate_fake_data(*args, **kwargs):
        return api.test.generate_fake_data(*args, **kwargs)


    return app
from flask import Flask, request
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

    # Recommendations
    @app.route('/recommendations', methods=['GET'])
    @jwt_required
    def get_recommendations(*args, **kwargs):
        return api.users.get_recommendations(*args, **kwargs)

    @app.route('/discover', methods=['GET'])
    @jwt_required
    def get_places_to_discover(*args, **kwargs):
        return api.users.get_places_to_discover(*args, **kwargs)

    # Visits
    @app.route('/visits', methods=['GET'])
    @jwt_required
    def get_visits(*args, **kwargs):
        return api.visits.get_visits(*args, **kwargs)

    @app.route('/visits/<visit_uuid>', methods=['GET'])
    @jwt_required
    def get_visit(visit_uuid, *args, **kwargs):
        return api.visits.get_visit_with_uuid(visit_uuid, *args, **kwargs)

    @app.route('/visits', methods=['POST'])
    @jwt_required
    def create_visit(*args, **kwargs):
        return api.visits.create_visit(*args, **kwargs)

    # Search
    @app.route('/search', methods=['POST'])
    @jwt_required
    def search_businesses(*args, **kwargs):
        return api.search.search_businesses(*args, **kwargs)

    # Test
    @app.route('/test', methods=['GET'])
    def generate_fake_data(*args, **kwargs):
        return api.test.generate_fake_data(*args, **kwargs)

    return app
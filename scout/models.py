from flask_jwt_extended import get_jwt_identity
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates, load_only
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from scipy.sparse.linalg import svds
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from uuid import uuid4

from scout import db
from scout.lib import YelpFusion

class OperationException(Exception):
    def __init__(self, *args, **kwargs):
        print('Unable to execute operation', args, kwargs)


class User(db.Model):
    __tablename__ = 'users'

    # Primary
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(UUID(as_uuid=True), index=True, unique=True, default=uuid4, nullable=False)
    username = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # Contact
    email = db.Column(db.String(128), index=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    first_name = db.Column(db.String(45), nullable=True)
    last_name = db.Column(db.String(45), nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, password, first_name = None, last_name = None, phone_number = None, **kwargs):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.password = self._hash_password(password)

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        return {
            'uuid': self.uuid,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def save(self):
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            raise OperationException(self)

    # Validators
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise AssertionError('No username provided')

        if User.query.filter(User.username == username).first():
            raise AssertionError('Username already taken')

        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('No email provided')
        try:
            validate_email(email)
        except EmailNotValidError:
            raise AssertionError('Invalid email format')

        if User.query.filter(User.email == email).first():
            raise AssertionError('Email already taken')

        return email

    # Statics
    @staticmethod
    def get_user_with_uuid(uuid):
        return User.query.filter(User.uuid == uuid).first()

    @staticmethod
    def validate_password_hash(password, hash, **kwargs):
        return check_password_hash(hash, password)

    @staticmethod
    def get_current():
        return User.get_user_with_uuid(get_jwt_identity())

    @staticmethod
    def validate_credentials(username_or_email, password, **kwargs):

        user = User.query.filter(User.username == username_or_email).first() or \
               User.query.filter(User.email == username_or_email).first()
        if user and User.validate_password_hash(password, user.password):
            return { 'valid': True, 'user': user }

        return { 'valid': False, 'user': None }

    @staticmethod
    def batch_save(records):
        try:
            for record in records:
                record.updated_at = datetime.utcnow()
            db.session.bulk_save_objects(records)
            db.session.commit()
        except:
            raise OperationException()

    # Private
    def _hash_password(self, password):
        return generate_password_hash(password)


class Visit(db.Model):
    __tablename__ = 'visits'

    # Primary
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), index=True, unique=True, default=uuid4, nullable=False)
    yelp_id = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    satisfaction = db.Column(db.Integer, nullable=False)
    attend_date =  db.Column(db.DateTime, nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, yelp_id, user_id, satisfaction, attend_date, **kwargs):
        self.yelp_id = yelp_id
        self.user_id = user_id
        self.satisfaction = satisfaction
        self.attend_date = attend_date

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        return {
            'uuid': self.uuid,
            'yelp_id': self.yelp_id,
            'user_id': self.user_id,
            'attend_date': self.attend_date,
            'satisfaction': self.satisfaction,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def save(self):
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            raise OperationException(self)

    @staticmethod
    def batch_save(records):
        try:
            for record in records:
                record.updated_at = datetime.utcnow()
            db.session.bulk_save_objects(records)
            db.session.commit()
        except:
            raise OperationException(records)

    @staticmethod
    def get_visit_with_uuid(visit_uuid):
        return Visit.query.filter(Visit.uuid == visit_uuid).first()

    @staticmethod
    def get_visits(page):
        current_user = User.get_current()
        return Visit.query.filter(Visit.user_id == current_user.id).order_by(desc("created_at")).paginate(page, 10, False).items

    @staticmethod
    def get_places_to_discover(current_coords):
        return YelpFusion.discover(current_coords)


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    # Primary
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uuid = db.Column(UUID(as_uuid=True), index=True, unique=True, default=uuid4)
    user_id = db.Column(db.Integer, nullable=False)
    yelp_id = db.Column(db.String(128), nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, yelp_id):
        self.user_id = user_id
        self.yelp_id = yelp_id

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        return {
            'uuid': self.uuid,
            'user_id': self.user_id,
            'yelp_id': self.yelp_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def save(self):
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            raise OperationException(self)

    @staticmethod
    def batch_save(records):
        try:
            for record in records:
                record.updated_at = datetime.utcnow()
            db.session.bulk_save_objects(records)
            db.session.commit()
        except:
            raise OperationException(records)

    @staticmethod
    def get_latest_5_with_user_id(user_id):
        current_date = datetime.utcnow().date()

        return Recommendation.query.filter(
            Recommendation.created_at.between(current_date, current_date + timedelta(days=1)),
            Recommendation.user_id == user_id,
        ).limit(5).all()

    @staticmethod
    def create_recommendations_for_today():
        # Get complete visit history
        visit_history = Visit.query.options(load_only('user_id', 'yelp_id', 'satisfaction')).all()
        # Maps query to [('user_id', 'yelp_id', 'satisfaction)] format
        formatted_visit_history = [(visit.user_id, visit.yelp_id, visit.satisfaction) for visit in visit_history]

        # Initialize Dataframe
        visit_history_df = pd.DataFrame(formatted_visit_history, columns=['user_id', 'yelp_id', 'satisfaction'])
        R_df = pd.pivot_table(visit_history_df, index='user_id', columns='yelp_id', values='satisfaction').fillna(0)
        R = R_df.as_matrix()
        user_satisfactions_mean = np.mean(R, axis=1)
        R_demeaned = R - user_satisfactions_mean.reshape(-1, 1)

        U, sigma, Vt = svds(R_demeaned, k=3)
        sigma = np.diag(sigma)
        all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_satisfactions_mean.reshape(-1, 1)
        predictions_df = pd.DataFrame(all_user_predicted_ratings, index=R_df.index.values, columns=R_df.columns)

        def create_recommendations_with_user_id(user_id):
            rated_by_user = np.array(visit_history_df[visit_history_df['user_id'] == user_id]['yelp_id'])
            recommendations_per_day = 5

            if len(rated_by_user) > 0:
                predictions = predictions_df.loc[user_id].sort_values(ascending=False).index.values
                yelp_ids = list(set(predictions) - set(rated_by_user))[:recommendations_per_day]

                recommendations_for_today = [Recommendation(yelp_id=yelp_id, user_id=user_id) for yelp_id in yelp_ids]
            else:
                # TODO: recommend places near user with same category, location, high satisfaction
                recommendations_for_today = []

            return recommendations_for_today

        all_recommendations = []
        for user_id in visit_history_df['user_id']:
            all_recommendations += create_recommendations_with_user_id(user_id)

        Recommendation.batch_save(all_recommendations)


from flask_jwt_extended import get_jwt_identity
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates, load_only
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from uuid import uuid4

from scout import db
from scout.lib import Recommender
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
    def get_recommendation(user_id, count = 5):
        visit_history = Visit.query.options(load_only('user_id', 'yelp_id', 'satisfaction')).all()
        # Maps query to [('user_id', 'yelp_id', 'satisfaction)] format
        formatted_visit_history = list(map(lambda visit: (visit.user_id, visit.yelp_id, visit.satisfaction), visit_history))

        recommender = Recommender(formatted_visit_history)
        return recommender.recommend_visit_with_user_id(user_id, count)

    @staticmethod
    def get_places_to_discover(current_coords):
        return YelpFusion.discover(current_coords)
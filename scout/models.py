from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from uuid import uuid4

from scout import db

class OperationException(Exception):
    def __init__(self, *args, **kwargs):
        print('Unable to execute operation', args, kwargs)

class Vendor(db.Model):
    __tablename__ = 'vendors'

    # Primary
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), index=True, unique=True, default=uuid4, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    yelp_id = db.Column(db.String(255))

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        return {}

    def save(self):
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            raise OperationException(self)

class User(db.Model):
    __tablename__ = 'users'

    # Primary
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(UUID(as_uuid=True), index=True, unique=True, default=uuid4, nullable=False)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # Contact
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, first_name, last_name, phone_number, password, **kwargs):
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
            'email': self.email,
            'username': self.username,
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
    def validate_credentials(username_or_email, password, **kwargs):

        user = User.query.filter(User.username == username_or_email).first() or \
               User.query.filter(User.email == username_or_email).first()

        if user and User.validate_password_hash(password, user.password):
            return { 'valid': True, 'user': user }

        return { 'valid': False, 'user': None }

    # Private
    def _hash_password(self, password):
        return generate_password_hash(password)

class Trip(db.Model):
    __tablename__ = 'trips'

    # Primary
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), index=True, unique=True, default=uuid4, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    user_ids = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=list)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return str(self.to_json())

    def to_json(self):
        return {}

    def save(self):
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            raise OperationException(self)

from flask import request
from flask_jwt_extended import create_access_token
from datetime import timedelta

from scout.models import OperationException, User
from scout.utils import compose_json_response

def login(*args, **kwargs):
    data = request.get_json()

    try:
        username_or_email = data['username_or_email']
        password = data['password']

        if username_or_email and password:
            auth_dict = User.validate_credentials(username_or_email, password)
            if auth_dict['valid']:
                token = create_access_token(identity=auth_dict['user'].to_json()['uuid'], expires_delta=timedelta(90))
                response = compose_json_response(success=True, data=token, message=None, code=200)
            else:
                response = compose_json_response(success=False, data=None, message='Unauthorized', code=401)
        else:
            response = compose_json_response(success=False, data=None, message='Invalid auth credentials', code=400)
    except KeyError:
        response = compose_json_response(success=False, data=None, message=None, code=400)

    print(response)
    return response

def signup(*args, **kwargs):
    data = request.get_json()

    try:
        new_user = User(username=data['username'],
                        email=data['email'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        phone_number=data['phone_number'],
                        password=data['password'])
        new_user.save()
        token = create_access_token(identity=new_user.uuid, expires_delta=timedelta(30))
        response = compose_json_response(success=True, data=token, message=None, code=200)
    except OperationException:
        response = compose_json_response(success=False, data=None, message=None, code=500)
    except KeyError:
        response = compose_json_response(success=False, data=None, message=None, code=400)
    return response

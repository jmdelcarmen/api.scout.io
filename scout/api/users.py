from flask import request
from scout.utils import execute_with_default, compose_json_response
from scout.models import User, Visit


def get_me(*args, **kwargs):
    current_user = User.get_current()
    return compose_json_response(success=True, data=current_user.to_json(), message=None, code=200)

def get_recommendations(*args, **kwargs):
    current_user = User.get_current()
    page_number = execute_with_default(int, 0)(request.args.get('page'))

    try:
        recommendations = Visit.get_recommendation(current_user.id, 5 * page_number)
        response = compose_json_response(success=True, data=recommendations, message=None, code=200)
    except:
        response = compose_json_response(success=False, data=None, message=None, code=500)
    return response

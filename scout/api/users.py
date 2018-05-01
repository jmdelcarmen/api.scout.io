from scout.utils import compose_json_response
from scout.models import User
from flask_jwt_extended import get_jwt_identity


def get_me(*args, **kwargs):
    current_user = User.get_user_with_uuid(get_jwt_identity())

    if current_user:
        return compose_json_response(success=True, data=current_user.to_json(), message=None, code=200)
    return compose_json_response(success=False, data=None, message='User not found', code=404)

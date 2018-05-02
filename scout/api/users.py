from scout.utils import compose_json_response
from scout.models import User


def get_me(*args, **kwargs):
    current_user = User.get_current()

    if current_user:
        return compose_json_response(success=True, data=current_user.to_json(), message=None, code=200)
    return compose_json_response(success=False, data=None, message='User not found', code=404)
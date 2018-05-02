from flask import request

from scout.models import OperationException, User, Visit
from scout.utils import compose_json_response


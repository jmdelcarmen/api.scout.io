from flask import request

from scout.models import OperationException, User, Visit
from scout.utils import compose_json_response, execute_with_default
from scout.lib import YelpFusion

def get_visit_with_uuid(visit_uuid, *args, **kwargs):
    visit = Visit.get_visit_with_uuid(visit_uuid)

    if visit:
        return compose_json_response(success=True, data=visit.to_json(), message=None, code=200)
    return compose_json_response(success=False, data=None, message=None, code=404)

def get_visits(*args, **kwargs):
    page_number = execute_with_default(int, 1)(request.args.get('page'))
    visits = Visit.get_visits(page=page_number)

    def map_visit_to_formatted_json(visit):
        return {**visit.to_json(), "data": YelpFusion.get_with_id(visit.yelp_id, desired_props=["id", "name"])}

    formatted_visits = list(map(map_visit_to_formatted_json, visits))

    if visits:
        return compose_json_response(success=True, data=formatted_visits, message=None, code=200)
    return compose_json_response(success=False, data=None, message=None, code=404)

def create_visit(*args, **kwargs):
    data = request.get_json()

    try:
        user_id = User.get_current().id
        yelp_id = data['yelp_id']
        attend_date = data['attend_date']
        satisfaction = data['satisfaction']

        new_visit = Visit(user_id=user_id,
                          yelp_id=yelp_id,
                          attend_date=attend_date,
                          satisfaction=satisfaction)
        new_visit.save()
        response = compose_json_response(success=True, data=None, message=None, code=200)
    except OperationException:
        response = compose_json_response(success=False, data=None, message=None, code=500)
    except KeyError:
        response = compose_json_response(success=False, data=None, message=None, code=400)
    return response

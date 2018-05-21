from flask import request
from scout.utils import execute_with_default, compose_json_response
from scout.models import User, Visit, Recommendation
from scout.lib import YelpFusion


def get_me(*args, **kwargs):
    current_user = User.get_current()
    return compose_json_response(success=True, data=current_user.to_json(), message=None, code=200)

def get_recommendations(*args, **kwargs):
    current_user = User.get_current()

    try:
        recommendations = [YelpFusion.get_with_id(id=recommendation.yelp_id, desired_props = ["id", "name", "image_url", "is_closed", "location", "url", "price"])
                           for recommendation in Recommendation.get_latest_5_with_user_id(current_user.id)]


        response = compose_json_response(success=True, data=recommendations, message=None, code=200)
    except:
        response = compose_json_response(success=False, data=None, message=None, code=500)
    return response

def get_places_to_discover(*args, **kwargs):
    current_coords = {
        'latitude': request.args.get('latitude'),
        'longitude': request.args.get('longitude')
    }

    if current_coords:
        try:
            places_to_discover = Visit.get_places_to_discover(current_coords)
            if len(places_to_discover):
                response = compose_json_response(success=True, data=places_to_discover, message=None, code=200)
            else:
                response = compose_json_response(success=False, data=None, message="No places found for current location", code=400)
        except:
            response = compose_json_response(success=False, data=None, message=None, code=500)
    else:
        response = compose_json_response(success=False, data=None, message=None, code=400)

    return response
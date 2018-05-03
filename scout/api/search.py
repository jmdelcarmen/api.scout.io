from flask import request

from scout.lib.yelp_fusion import YelpFusion
from scout.utils import compose_json_response

def search_businesses(*args, **kwargs):
    data = request.get_json()

    try:
        q = data['q']
        location = data['location']
        businesses = YelpFusion.search(term=q, location=location)

        response = compose_json_response(success=True, data=businesses, message=None, code=200)
    except KeyError:
        response = compose_json_response(success=True, data=None, message=None, code=400)
    return response
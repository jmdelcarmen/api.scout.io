from flask import request

from scout.lib.yelp_fusion import YelpFusion
from scout.utils import compose_json_response

def search_businesses(*args, **kwargs):
    params = request.args

    try:
        q = params.get('q')
        location = params.get('location')
        print(q, location)
        businesses = YelpFusion.search(term=q, location=location)

        response = compose_json_response(success=True, data=businesses, message=None, code=200)
    except KeyError:
        response = compose_json_response(success=True, data=None, message=None, code=400)
    return response
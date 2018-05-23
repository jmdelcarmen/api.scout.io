import os
import requests
from urllib.parse import quote
from urllib import request

class YelpFusionException(Exception):
    def __init__(self):
        print('HTTP request to Yelp Fusion API failed')

class YelpFusion:
    config = {
        'API_KEY': os.getenv('YELP_API_KEY') or None,
        'HOST': 'https://api.yelp.com',
        'SEARCH_PATH': '/v3/businesses/search',
        'SEARCH_LIMIT': 10,
        'BUSINESS_PATH': '/v3/businesses/',
    }

    @staticmethod
    def request(host, path, api_key, url_params=None):
        url_params = url_params or {}
        url = '{0}{1}'.format(host, quote(path.encode('utf8')))
        headers = { 'Authorization': 'Bearer {}'.format(api_key) }

        try:
            response = requests.request('GET', url, headers=headers, params=url_params)
            return response.json()
        except:
            raise YelpFusionException()

    @staticmethod
    def search(term = "", location = "", params = {}, limit = 10):
        url_params = {
            'term': term.replace(' ', '+'),
            'limit': limit or YelpFusion.config['SEARCH_LIMIT'],
            'location': location.replace(' ', '+'),
            'sort_by': 'rating',
        }

        if params:
            url_params = params

        try:
            response = YelpFusion.request(YelpFusion.config['HOST'],
                                      YelpFusion.config['SEARCH_PATH'],
                                      YelpFusion.config['API_KEY'],
                                      url_params=url_params)
            return response['businesses'] if 'businesses' in response else []
        except YelpFusionException: # Handle any HTTP errors
            return None

    @staticmethod
    def discover(current_coords, desired_props = [], **kwargs):
        get_only_desired_props = lambda place: {desired_prop: place[desired_prop] for desired_prop in desired_props}
        response = YelpFusion.search(params = {'term': '', 'limit': 10, 'sort_by': 'rating', 'open_now': True, **current_coords})

        try:
            if desired_props:
                return list(map(get_only_desired_props, response))
        except KeyError as e:
            print("KeyError. Unfound desired_prop: {}".format(e))

        return response

    @staticmethod
    def get_with_id(id, desired_props = [], **kwargs):
        try:
            response = YelpFusion.request(YelpFusion.config['HOST'],
                                          YelpFusion.config['BUSINESS_PATH'] + id,
                                          YelpFusion.config['API_KEY'])
            if desired_props:
                return {desired_prop: response[desired_prop] for desired_prop in desired_props }

            return response
        except YelpFusionException:
            return None

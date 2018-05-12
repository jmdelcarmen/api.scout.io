import os
import requests
from urllib.parse import quote

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
    def search(term, location, limit = 0):
        url_params = {
            'term': term.replace(' ', '+'),
            'limit': limit or YelpFusion.config['SEARCH_LIMIT'],
            'location': location.replace(' ', '+'),
        }

        try:
            response = YelpFusion.request(YelpFusion.config['HOST'],
                                      YelpFusion.config['SEARCH_PATH'],
                                      YelpFusion.config['API_KEY'],
                                      url_params=url_params)

            return response['businesses'] if 'businesses' in response else []
        except YelpFusionException: # Handle any HTTP errors
            return None

    @staticmethod
    def get_with_id(id):
        try:
            response = YelpFusion.request(YelpFusion.config['HOST'],
                                          YelpFusion.config['BUSINESS_PATH'] + id,
                                          YelpFusion.config['API_KEY'])
            return response
        except YelpFusionException:
            return None

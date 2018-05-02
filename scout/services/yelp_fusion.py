import os
import requests
from urllib.parse import quote

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

        response = requests.request('GET', url, headers=headers, params=url_params)

        return response.json()

    @staticmethod
    def search(term, location):
        url_params = {
            'term': term.replace(' ', '+'),
            'limit': YelpFusion.config['SEARCH_LIMIT'],
            'location': location.replace(' ', '+'),
        }

        response = YelpFusion.request(YelpFusion.config['HOST'],
                                  YelpFusion.config['SEARCH_PATH'],
                                  YelpFusion.config['API_KEY'],
                                  url_params=url_params)

        return response['businesses'] if 'businesses' in response else []

    @staticmethod
    def get_with_id(id):
        print(YelpFusion.config['BUSINESS_PATH'] + id)
        response = YelpFusion.request(YelpFusion.config['HOST'],
                                      YelpFusion.config['BUSINESS_PATH'] + id,
                                      YelpFusion.config['API_KEY'])

        return response
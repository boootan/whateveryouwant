import requests
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')

def requestRestaurants():
    headers = {'Authorization': 'Bearer {}'.format(API_KEY)}
    payload = {'location': '92683', 'categories': 'mexican'}
    r = requests.get('https://api.yelp.com/v3/businesses/search', headers = headers, params = payload)
    print(r.json())
    return r.json()


def main():
    options = requestRestaurants()
    print(options["businesses"][0])

if __name__ == '__main__':
    main()
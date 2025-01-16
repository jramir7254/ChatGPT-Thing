import requests
import random

api_key = 'qHf-A9B2T2ZfyvdfRwg2mCt_G0xlwDgSZWsI7W7Zl0FLmDASWwkBJy90ziHHcLKJo2_69cZWW13_IWFVNPeReeqUxVHuFnP82InUzKr7AQ0UwEDgZslYGq4UIJqIZ3Yx'
url = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': f'Bearer {api_key}'}

# User-provided ZIP code
user_zip = input("Enter ZIP code: ")

params = {
    'location': user_zip,
    'limit': 50,  # Maximum results
    'sort_by': 'rating',  # Sort by rating
}

response = requests.get(url, headers=headers, params=params).json()
businesses = response.get('businesses', [])

# Randomly select 10 businesses
if len(businesses) < 20:
    print("Fewer than 10 locations found.")
random_businesses = random.sample(businesses, min(10, len(businesses)))

for business in random_businesses:
    print(business['name'])

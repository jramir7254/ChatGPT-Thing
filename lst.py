from dotenv import load_dotenv
import googlemaps
import random
import json
import os
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

place_types = [
    "accounting", "airport", "amusement_park", "aquarium", "art_gallery", 
    "bakery", "bank", "bar", "beauty_salon", "bicycle_store", "book_store", 
    "bowling_alley", "cafe", "campground", "car_dealer", "car_rental", 
    "car_repair", "car_wash", "casino", "cemetery", "church", "city_hall", 
    "clothing_store", "convenience_store", "courthouse", "dentist", "department_store", 
    "doctor", "drugstore", "electrician", "electronics_store", "embassy", "fire_station", 
    "florist", "funeral_home", "furniture_store", "gas_station", "gym", "hair_care", 
    "hardware_store", "hindu_temple", "home_goods_store", "hospital", "insurance_agency", 
    "jewelry_store", "laundry", "lawyer", "library", "light_rail_station", "liquor_store", 
    "local_government_office", "lodging", "meal_delivery", "meal_takeaway", 
    "mosque", "movie_rental", "movie_theater", "moving_company", "museum", "night_club", 
    "painter", "park", "parking", "pet_store", "pharmacy", "physiotherapist", 
    "plumber", "police", "post_office", "real_estate_agency", "restaurant", 
    "roofing_contractor", "rv_park", "school", "shoe_store", "shopping_mall", 
    "spa", "stadium", "storage", "store", "subway_station", "supermarket", 
    "synagogue", "taxi_stand", "tourist_attraction", "train_station", 
    "travel_agency", "university", "veterinary_care", "zoo"
]


def get_zip_bounds(api_key, zip_code):
    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.geocode(zip_code)
    if result:
        return result[0]['geometry']['bounds']
    raise ValueError("Invalid ZIP code or no data found.")


def is_urban_area(zip_code):
    return int(zip_code[:2]) < 60  # Simplified heuristic: lower ZIPs tend to be urban


def fetch_places_for_type(api_key, location, place_type, zip_code):
    gmaps = googlemaps.Client(key=api_key)
    radius = 10_000 if is_urban_area(zip_code) else 50_000
    response = gmaps.places_nearby(location=location, radius=radius, type=place_type)
    places = []
    if "results" in response:
        for place in response["results"]:
            lat, lng = place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"]
            if "plus_code" in place and "compound_code" in place["plus_code"] and zip_code in place["plus_code"]["compound_code"]:
                places.append({"name": place.get("name"), "address": place.get("vicinity"), "location": place["geometry"]["location"], "types": place.get("types")})
            else:
                result = gmaps.reverse_geocode((lat, lng))
                if any("postal_code" in comp["types"] and comp["long_name"] == zip_code for comp in result[0]["address_components"]):
                    places.append({"name": place.get("name"), "address": place.get("vicinity"), "location": place["geometry"]["location"], "types": place.get("types")})
    return places


def search_all_place_types(api_key, bounds, zip_code):
    gmaps = googlemaps.Client(key=api_key)
    center_lat = (bounds['northeast']['lat'] + bounds['southwest']['lat']) / 2
    center_lng = (bounds['northeast']['lng'] + bounds['southwest']['lng']) / 2
    location = (center_lat, center_lng)
    random_place_types = random.sample(place_types, 10)
    places = []
    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda p: fetch_places_for_type(api_key, location, p, zip_code), random_place_types)
    for result in results:
        places.extend(result)
    return places


def generate_random_places(zip_code):
    api_key = os.getenv("GOOGLE_API_KEY")
    bounds = get_zip_bounds(api_key, zip_code)
    places = search_all_place_types(api_key, bounds, zip_code)
    with open("locations/locations.json", 'w') as file:
        json.dump(places, file, indent=4)
    random.shuffle(places)
    return places[:10]


if __name__ == "__main__":
    zip_code = input("Enter the ZIP code: ")
    try:
        random_places = generate_random_places(zip_code)
        print(f"Here are 10 random places strictly within ZIP code {zip_code}:")
        for place in random_places:
            print(f"Name: {place['name']}, Address: {place['address']}")
    except Exception as e:
        print(f"Error: {e}")

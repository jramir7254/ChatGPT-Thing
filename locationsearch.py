from dotenv import load_dotenv
import googlemaps
import random
import json
import os



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


# Function to get the geographic bounds of a ZIP code
def get_zip_bounds(api_key, zip_code):
    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.geocode(zip_code)
    if result:
        bounds = result[0]['geometry']['bounds']
        return bounds
    else:
        raise ValueError("Invalid ZIP code or no data found.")


# Function to search for businesses/landmarks within the bounds
def search_all_place_types(api_key, bounds, zip_code):
    gmaps = googlemaps.Client(key=api_key)
    all_places = []

    # Calculate the center of the bounds
    center_lat = (bounds['northeast']['lat'] + bounds['southwest']['lat']) / 2
    center_lng = (bounds['northeast']['lng'] + bounds['southwest']['lng']) / 2
    location = (center_lat, center_lng)

    random_place_types = random.sample(place_types, 10)
    print(random_place_types)

    # Loop through all place types
    for place_type in random_place_types:
        response = gmaps.places_nearby(location=location, radius=50_000, type=place_type)
        if "results" in response:
            for place in response["results"]:
                # Perform reverse geocoding to check the ZIP code
                lat = place["geometry"]["location"]["lat"]
                lng = place["geometry"]["location"]["lng"]
                result = gmaps.reverse_geocode((lat, lng))
                
                if result:
                    for component in result[0]["address_components"]:
                        if "postal_code" in component["types"] and component["long_name"] == zip_code:
                            # Avoid duplicates using a unique identifier (e.g., name and location)
                            unique_id = f"{place['name']}|{place['geometry']['location']}"
                            if not any(p['id'] == unique_id for p in all_places):
                                all_places.append({
                                    "id": unique_id,
                                    "name": place.get("name"),
                                    "address": place.get("vicinity"),
                                    "location": place["geometry"]["location"],
                                    "types": place.get("types")
                                })
                            break  # Break after finding the ZIP code match

    return all_places


# Function to verify if a location is strictly within the given ZIP code
def filter_places_by_zip(api_key, places, zip_code):
    gmaps = googlemaps.Client(key=api_key)
    filtered_places = []

    for place in places:
        lat = place["location"]["lat"]
        lng = place["location"]["lng"]

        # Reverse geocode to verify ZIP code
        result = gmaps.reverse_geocode((lat, lng))
        if result:
            for component in result[0]["address_components"]:
                if "postal_code" in component["types"] and component["long_name"] == zip_code:
                    filtered_places.append(place)
                    break

    return filtered_places



def generate_random_places(zip_code):
    api_key = os.getenv("GOOGLE_API_KEY")
    bounds = get_zip_bounds(api_key, zip_code)
    places = search_all_place_types(api_key, bounds, zip_code)
    with open("locations/locations.json", 'w') as file:
        json.dump(places, file, indent=4)
    random_places = random.sample(places, min(10, len(places)))
    return random_places


# Main function
def main():
    # Replace with your Google API Key
    api_key = os.getenv("GOOGLE_API_KEY")

    # Input ZIP code
    zip_code = input("Enter the ZIP code: ")

    try:
        # Step 1: Get the geographic bounds of the ZIP code
        bounds = get_zip_bounds(api_key, zip_code)
        print("Retrieved Bounds...")

        # Step 2: Search for businesses/landmarks in the ZIP code
        places = search_all_place_types(api_key, bounds, zip_code)
        with open("generated_locations.json", "w") as file:
            json.dump(places, file, indent=4)
        print("Searched Places...")
    
        # Step 3: Filter places strictly within the given ZIP code
        # filtered_places = filter_places_by_zip(api_key, places, zip_code)
        # print("Filtered Places...")

        # Step 4: Randomly select 10 places
        random_places = random.sample(places, min(10, len(places)))
        print("Randomizing Places...")

        # Step 5: Output the results
        if random_places:
            print(f"Here are 10 random businesses/landmarks strictly within the ZIP code: {zip_code}")
            for place in random_places:
                print(f"Name: {place['name']}, Address: {place['address']}")
        else:
            print(f"No businesses or landmarks found strictly within ZIP code {zip_code}.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
import requests

# Function to get the location based on IP address
def get_location_by_ip(ip):
    GEOLOCATION_API_URL = f'http://ip-api.com/json/{ip}'
    response = requests.get(GEOLOCATION_API_URL)
    if response.status_code == 200:
        location_data = response.json()
        city = location_data.get('city')
        region = location_data.get('regionName')
        country = location_data.get('country')
        return f"{city}, {region}, {country}"
    else:
        return None

# Replace with your actual Weather API key
WEATHER_API_KEY = 'ec7db2bbc1c24c55933201843241405'
BASE_URL = 'http://api.weatherapi.com/v1/'

def get_weather(location):
    if not location:
        print('No location determined')
        return

    params = {
        "key": WEATHER_API_KEY,
        "q": location
    }

    endpoint = 'current.json'
    response = requests.get(BASE_URL + endpoint, params=params)  # Changed to GET

    if response.status_code == 200:
        weather_data = response.json()
        loc_data = weather_data['location']
        curr_data = weather_data['current']
        data = {
            "name": loc_data.get('name'),
            "region": loc_data.get('region'),
            "country": loc_data.get('country'),
            "temp_f": curr_data.get('temp_f'),
            "is_day": curr_data.get('is_day'),
            "condition": curr_data['condition'].get('text'),
            "precip": curr_data.get('precip_in'),
            "humidity": curr_data.get('humidity')
        }

        return data
    else:
        print('Failed to fetch weather data')
        return None

# Use a known IP address for testing
test_ip = '24.42.196.226'  # Example IP address (Google Public DNS)
location = get_location_by_ip(test_ip)
weather_data = get_weather(location)
print(weather_data)

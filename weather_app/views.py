import requests
from django.shortcuts import render
from datetime import datetime
from django.templatetags.static import static

API_KEY = '90thkz01lnk8ua3587hrvqqfe9cq7i9jf7w5ij64'
OPENCAGE_API_KEY = '23debcd504e241df857f10b6ff325ef6'  # OpenCage API key

# Get weather data from the API
def get_weather_data(lat, lon):
    api_url = f'https://www.meteosource.com/api/v1/free/point?lat={lat}&lon={lon}&sections=all&timezone=UTC&language=en&units=metric&key={API_KEY}'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON data if successful
    else:
        return None  # Return None if there was an error with the API request

# Get location data from OpenCage API
def get_location_data(city):
    geocode_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={OPENCAGE_API_KEY}'
    response = requests.get(geocode_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat = data['results'][0]['geometry']['lat']
            lon = data['results'][0]['geometry']['lng']
            return lat, lon
    return None, None  # Return None if there is no valid result

def weather(request):
    # Get the city from the user input, default to Kampala
    city = request.GET.get('city', 'Kampala')

    # Get latitude and longitude for the city
    lat, lon = get_location_data(city)

    if lat is not None and lon is not None:
        # Fetch the weather data using latitude and longitude
        weather_data = get_weather_data(lat, lon)

        current_time = datetime.now().strftime("%H:%M")  # Format the current time

        if weather_data:
            # Print the entire weather data to debug
            print("Weather Data:", weather_data)  # Add this line to inspect the response

            # Get current weather data
            current_weather = weather_data.get('current', {})
            temperature = current_weather.get('temperature', 'N/A')
            condition = current_weather.get('summary', 'N/A')
            wind_speed = current_weather.get('wind', {}).get('speed', 'N/A')
            cloud_cover = current_weather.get('cloud_cover', 'N/A')

            # Get humidity and sunshine hours, if available
            humidity = current_weather.get('humidity', 'N/A')
            sunshine_hours = current_weather.get('sunshine', 'N/A')

            icon_code = current_weather.get('icon', 1)  # Default to 1 if no icon code
            print(f"Icon code: {icon_code}")

            # Map icon code to the correct file name in the static directory
            icon_mapping = {
                'sunny': '1.png',
                'mostly_sunny': '2.png',
                'partly_sunny': '3.png',
                'mostly_cloudy': '4.png',
                'cloudy': '5.png',
                'overcast': '6.png',
                'overcast_low_clouds': '7.png',
                'fog': '8.png',
                'light_rain': '9.png',
                'rain': '10.png',
                'possible_rain': '11.png',
                'rain_shower': '12.png',
                'thunderstorm': '13.png',
                'local_thunderstorms': '14.png',
                'light_snow': '15.png',
                'snow': '16.png',
                'possible_snow': '17.png',
                'snow_shower': '18.png',
                'rain_and_snow': '19.png',
                'possible_rain_and_snow': '20.png',
                'rain_and_snow': '21.png',
                'freezing_rain': '22.png',
                'possible_freezing_rain': '23.png',
                'hail': '24.png',
                'clear_night': '25.png',
                'mostly_clear_night': '26.png',
                'partly_clear_night': '27.png',
                'mostly_cloudy_night': '28.png',
                'cloudy_night': '29.png',
                'overcast_low_clouds_night': '30.png',
                'rain_shower_night': '31.png',
                'local_thunderstorms_night': '32.png',
                'snow_shower_night': '33.png',
                'rain_and_snow_night': '34.png',
                'possible_freezing_rain_night': '35.png',
            }

            icon_file = icon_mapping.get(icon_code, '1.png')  # Fallback to 'default.png' if no match

            # Build the static URL for the icon
            icon_url = static(f'weather_icons/{icon_file}')

            # Get daily forecast data
            daily_forecast = weather_data.get('daily', {}).get('data', [])
            daily_summary = []
            for day in daily_forecast:
                day_summary = {
                    'day': day.get('day', 'N/A'),
                    'summary': day.get('summary', 'N/A'),
                    'temperature_min': day.get('all_day', {}).get('temperature_min', 'N/A'),
                    'temperature_max': day.get('all_day', {}).get('temperature_max', 'N/A'),
                }
                daily_summary.append(day_summary)

            context = {
                'city': city,
                'temperature': temperature,
                'condition': condition,
                'wind_speed': wind_speed,
                'cloud_cover': cloud_cover,
                'humidity': humidity,  # Pass humidity to template
                'sunshine_hours': sunshine_hours,  # Pass sunshine hours to template
                'icon_url': icon_url,  # Pass the icon URL to the template
                'daily_summary': daily_summary,
                'current_time': current_time
            }
        else:
            context = {'error': 'Weather data could not be fetched'}
    else:
        context = {'error': 'Location could not be found'}

    return render(request, 'weather_app/home.html', context)

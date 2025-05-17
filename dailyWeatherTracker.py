import requests, csv, datetime

APPID = "1017e9154bbf1417b440db46b410de3a"

cities = [
    {"name": "Dublin", "query": {"q": "Dublin,IE"}},
    {"name": "Vatican City", "query": {"q": "Vatican City,VA"}},
    {"name": "Munich", "query": {"q": "Munich,DE"}},
    {"name": "Portland", "query": {"q": "Portland,ME,US"}},
    {"name": "Tampa", "query": {"q": "Tampa,US"}},
    {"name": "Cleveland", "query": {"q": "Cleveland,US"}},
    {"name": "Indianapolis", "query": {"q": "Indianapolis,US"}},
    {"name": "Chicago", "query": {"q": "Chicago,US"}},
    {"name": "New York", "query": {"q": "New York,US"}},
    {"name": "Grand Canyon", "query": {"q": "Grand Canyon,US"}},
    {"name": "Mt. Washington", "query": {"lat": 44.2706, "lon": -71.3033}},
]

url = "https://api.openweathermap.org/data/2.5/weather"
today = datetime.date.today().isoformat()

weather_data = []

for city in cities:
    params = city["query"].copy()
    params["appid"] = APPID
    params["units"] = "imperial"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        city_name = city["name"]
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        print(
            f"{city_name}: {temp}°F, {condition.title()}, {humidity}% humidity, Wind {wind_speed} mph"
        )
        weather_data.append([today, city_name, temp, condition, humidity, wind_speed])
    except Exception as e:
        print(f"Failed to get weather for {city['name']}: {e}")

        weather_data.append([today, city_name, temp, condition, humidity, wind_speed])
    except Exception as e:
        print(f"Failed to get weather for {city}: {e}")

import os

# Write to CSV
filename = "weather_log.csv"
write_header = not os.path.exists(filename)

with open(filename, "a", newline="") as file:
    writer = csv.writer(file)
    if write_header:
        writer.writerow(
            ["Date", "City", "Temp (F)", "Condition", "Humidity (%)", "Wind (mph)"]
        )
    writer.writerows(weather_data)

print(f"\n✅ Weather data logged to {filename}")

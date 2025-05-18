#! /usr/bin/env python3

# Chris Redmond's Weather Project

import os
import requests, csv
from tabulate import tabulate
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# Load environment variables
load_dotenv()

# Get the path to the creds file from .env
creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

APPID = "1017e9154bbf1417b440db46b410de3a"

cities = [
    {"name": "Vatican City", "query": {"q": "Vatican City,VA"}},
    {"name": "Munich", "query": {"q": "Munich,DE"}},
    {"name": "Dublin", "query": {"q": "Dublin,IE"}},
    {"name": "Portland", "query": {"q": "Portland,ME,US"}},
    {"name": "Mt. Washington", "query": {"lat": 44.2706, "lon": -71.3033}},
    {"name": "New York", "query": {"q": "New York,US"}},
    {"name": "Cleveland", "query": {"q": "Cleveland,US"}},
    {"name": "Tampa", "query": {"q": "Tampa, US"}},
    {"name": "Indianapolis", "query": {"q": "Indianapolis,US"}},
    {"name": "Chicago", "query": {"q": "Chicago,US"}},
    {"name": "Grand Canyon", "query": {"q": "Grand Canyon,US"}},
    {"name": "Redmond", "query": {"q": "Redmond,WA,US"}},
    {"name": "Anchorage", "query": {"q": "Anchorage,AK,US"}},
]

url = "https://api.openweathermap.org/data/2.5/weather"
today = date.today().isoformat()

weather_data = []
display_data = []

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
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        sunrise_unix = data["sys"]["sunrise"]
        sunset_unix = data["sys"]["sunset"]
        # Convert to readable time
        sunrise_time = datetime.fromtimestamp(sunrise_unix).strftime("%I:%M%p")
        sunset_time = datetime.fromtimestamp(sunset_unix).strftime("%I:%M%p")

        display_data.append(
            [
                city_name,
                f"{temp:.1f}°F",
                f"{feels_like:.1f}°F",
                f"{humidity}%",
                condition.title(),
                f"{wind_speed} mph",
                sunrise_time,
                sunset_time,
            ]
        )

        print(
            f"{city_name}: {temp}°F, {humidity}% humidity, {condition.title()}, Wind {wind_speed} mph, Sunrise: {sunrise_time}, Sunset: {sunset_time}"
        )
        weather_data.append(
            [
                today,
                city_name,
                temp,
                feels_like,
                humidity,
                condition,
                wind_speed,
                sunrise_time,
                sunset_time,
            ]
        )
    except Exception as e:
        print(f"Failed to get weather for {city['name']}: {e}")

        weather_data.append(
            [
                today,
                city_name,
                temp,
                feels_like,
                humidity,
                condition,
                wind_speed,
                sunrise_time,
                sunset_time,
            ]
        )
    except Exception as e:
        print(f"Failed to get weather for {city}: {e}")

print(
    tabulate(
        display_data,
        headers=[
            "City",
            "Temp",
            "Feels Like",
            "Humidity",
            "Condition",
            "Wind",
            "Sunrise",
            "Sunset",
        ],
    )
)

# Plotting temperature and wind speed side by side
cities_list = [row[0] for row in display_data]
temps = [float(row[1].replace("°F", "")) for row in display_data]
winds = [float(row[5].replace(" mph", "")) for row in display_data]
x = range(len(cities_list))

fig, ax1 = plt.subplots(figsize=(12, 6))

# Temperature bars
ax1.bar(x, temps, width=0.4, label="Temp (°F)", color="skyblue", align="center")
ax1.set_xlabel("City")
ax1.set_ylabel("Temperature (°F)", color="skyblue")
ax1.tick_params(axis="y", labelcolor="skyblue")
ax1.set_xticks(x)
ax1.set_xticklabels(cities_list, rotation=45)

# Wind speed bars (on right y-axis)
ax2 = ax1.twinx()
ax2.bar(
    [i + 0.4 for i in x],
    winds,
    width=0.4,
    label="Wind (mph)",
    color="lightcoral",
    align="center",
)
ax2.set_ylabel("Wind Speed (mph)", color="lightcoral")
ax2.tick_params(axis="y", labelcolor="lightcoral")

# Title and layout
plt.title(f"Temp & Wind Speed by City – {today}")
fig.tight_layout()
plt.savefig("weather_chart.png")
plt.show()

# Write to CSV
filename = "weather_log.csv"
write_header = not os.path.exists(filename)

with open(filename, "a", newline="") as file:
    writer = csv.writer(file)
    if write_header:
        writer.writerow(
            [
                "Date",
                "City",
                "Temp (F)",
                "Feels Like (F)",
                "Humidity (%)",
                "Condition",
                "Wind (mph)",
                "Sunrise",
                "Sunset",
            ]
        )
    writer.writerows(weather_data)

print(f"\n✅ Weather data logged to {filename}")

# --- START Google Sheets Upload ---
# Google Sheets auth and setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("weather-creds.json", scope)
client = gspread.authorize(creds)

# Open or create the spreadsheet
spreadsheet = client.open("Daily Weather Log")
print("Google Sheet URL:", spreadsheet.url)
try:
    sheet = spreadsheet.worksheet("Weather")
except gspread.exceptions.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet(title="Weather", rows="1000", cols="10")
    sheet.append_row(
        [
            "Date",
            "City",
            "Temp (°F)",
            "Feels Like (F)",
            "Humidity (%)",
            "Condition",
            "Wind (mph)",
            "Sunrise",
            "Sunset",
        ]
    )  # headers

# Append a row for each city
for row in weather_data:
    sheet.append_row(row)

print("✅ Weather data also logged to Google Sheet.")
# --- END Google Sheets Upload ---

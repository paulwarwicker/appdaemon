import requests
import time
from datetime import datetime, timedelta

def safe_request(url, params, max_retries=3, delay=5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params)
            if response.status_code == 409:
                print(f"HTTP 409 Conflict encountered. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
            else:
                return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
    return None

def get_ryanair_fares_with_retries(departure_airport, destination_airport, start_date, end_date, stay_duration, delay=5, max_retries=3):
    base_url = "https://www.ryanair.com/api/booking/v4/en-gb/availability"
    # https://desktopapps.ryanair.com/en-gb/availability?ADT=1&CHD=0&DateIn=2016-11-24&DateOut=2016-11-10&Destination=STN&FlexDaysIn=6&FlexDaysOut=6&INF=0&Origin=VLC&RoundTrip=true&TEEN=0&ToUs=AGREED
    fares = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date:
        return_date = current_date + timedelta(days=stay_duration)
        params = {
            "ADT": 2,
            "CHD": 0,
            "TEEN": 0,
            "INF": 0,
            "DateOut": current_date.strftime("%Y-%m-%d"),
            "DateIn": return_date.strftime("%Y-%m-%d"),
            "Origin": departure_airport,
            "Destination": destination_airport,
            "FlexDaysOut": 0,
            "FlexDaysIn": 0,
            "RoundTrip": "true",
            "ToUs": "AGREED"
        }

        print(params)
        response = safe_request(base_url, params, max_retries, delay)
        if response and response.status_code == 200:
            data = response.json()
            for trip in data.get("trips", []):
                for date in trip["dates"]:
                    for flight in date["flights"]:
                        fares.append({
                            "departure_date": date["dateOut"],
                            "return_date": return_date.strftime("%Y-%m-%d"),
                            "price": flight["regularFare"]["fares"][0]["amount"],
                            "flight_number": flight["flightNumber"],
                        })
        current_date += timedelta(days=1)
        time.sleep(delay)

    return fares

# Configuration
departure_airport = "STN"  # Stansted Airport
destination_airport = "ACE"  # Arrecife Airport
start_date = "2025-03-11"  # Start of the date range
end_date = "2025-03-13"  # End of the date range
stay_duration = 4  # Number of days to stay

# Get fares
fares = get_ryanair_fares_with_retries(departure_airport, destination_airport, start_date, end_date, stay_duration, 5, 3)

# Print results
if fares:
    for fare in fares:
        print(f"Departure: {fare['departure_date']}, Return: {fare['return_date']}, "
              f"Price: {fare['price']}, Flight Number: {fare['flight_number']}")
else:
    print("No fares found.")

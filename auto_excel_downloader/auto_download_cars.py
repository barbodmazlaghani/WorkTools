import os
import requests
import json
import time
from datetime import datetime, timedelta
import logging

# Configuration
API_BASE_URL = "http://130.185.77.114/api"
GET_CARS_ENDPOINT = "/get-cars/"
DOWNLOAD_HISTORY_ENDPOINT_TEMPLATE = "/history/carID/{car_id}/"

AUTH_TOKEN = "bf8f82ecff0102edca5a59936ad2dfe3690f05aa"
HEADERS = {
    "authorization": f"Token {AUTH_TOKEN}"
}

STATE_FILE = "download_state.json"
DOWNLOAD_FOLDER = "downloaded_excels"
LOG_FILE = "auto_download.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"cars": {}}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def get_car_list():
    url = f"{API_BASE_URL}{GET_CARS_ENDPOINT}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()  # Adjust based on actual API response structure

def download_excel(car_id, from_time, to_time):
    # Prepare the download URL
    download_endpoint = DOWNLOAD_HISTORY_ENDPOINT_TEMPLATE.format(car_id=car_id)
    params = {
        "fromTime": from_time,
        "toTime": to_time,
        "fields": "location,variables",
        "data_format": "excel"
    }
    url = f"{API_BASE_URL}{download_endpoint}"

    logging.info(f"Starting download for Car ID: {car_id} from {from_time} to {to_time}")
    response = requests.get(url, headers=HEADERS, params=params, stream=True)
    if response.status_code == 200:
        filename = f"{car_id}_{from_time}_{to_time}.xlsx"
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info(f"Successfully downloaded Excel for Car ID: {car_id} to {filename}")
    else:
        error_message = f"Failed to download Excel for Car ID: {car_id}, Status Code: {response.status_code}"
        logging.error(error_message)
        raise Exception(error_message)

def process_cars():
    logging.info("Process started.")
    state = load_state()
    cars_state = state.get("cars", {})

    try:
        cars = get_car_list()
        logging.info(f"Fetched {len(cars)} cars from API.")
    except Exception as e:
        logging.error(f"Error fetching car list: {e}")
        return

    current_time = int(time.time())

    for car in cars:
        car_id = car.get("carID")  # Adjust based on actual car data structure
        if not car_id:
            logging.warning("Car ID not found in car data.")
            continue

        # Get last downloaded toTime for this car
        last_to_time = cars_state.get(car_id, {}).get("last_to_time")
        if last_to_time:
            last_download_date = datetime.fromtimestamp(last_to_time)
            six_months_ago = datetime.now() - timedelta(days=180)
            if last_download_date > six_months_ago:
                logging.info(f"Six months have not passed since last download for Car ID: {car_id}. Skipping.")
                continue
            else:
                from_time = last_to_time + 1  # Start right after the last download
        else:
            # If no previous download, set from_time to six months ago
            six_months_ago = datetime.now() - timedelta(days=180)  # Approximate 6 months
            from_time = int(time.mktime(six_months_ago.timetuple()))

        # Define the new to_time as current time
        to_time = current_time

        # Check if from_time is in the future
        if from_time >= to_time:
            logging.info(f"No new data to download for Car ID: {car_id}")
            continue

        try:
            download_excel(car_id, from_time, to_time)
            # Update the last_to_time for this car
            cars_state[car_id] = {"last_to_time": to_time}
            save_state({"cars": cars_state})
        except Exception as e:
            logging.error(f"Error downloading for Car ID {car_id}: {e}")
            # Decide whether to continue with next cars or halt
            continue  # Continue with next car

    logging.info("Process completed.")

def main():
    process_cars()

if __name__ == "__main__":
    main()

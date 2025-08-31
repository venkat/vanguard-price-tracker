import json
import re
from datetime import datetime, timedelta

def get_historical_data():
    """Reads the existing JSON file or returns an empty list."""
    try:
        with open("vanguard_price.json", "r") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data_list):
    """Saves the updated data list to the JSON file."""
    with open("vanguard_price.json", "w") as json_file:
        json.dump(data_list, json_file, indent=4)
    print("Successfully saved data to vanguard_price.json")

try:
    # 1. Read the raw data fetched by wget
    with open("vanguard_raw.jsonp", "r") as raw_file:
        jsonp_data = raw_file.read()

    # 2. Extract the JSON from the JSONP response
    json_str = re.search(r'\((\{.*\})\)', jsonp_data).group(1)
    new_price_data = json.loads(json_str)

    # 3. Read existing historical data
    historical_data = get_historical_data()
    
    # 4. Check if this date already exists to avoid duplicates
    new_date = new_price_data['asOfDate']
    if any(item['asOfDate'] == new_date for item in historical_data):
        print(f"Data for {new_date} already exists. No update needed.")
    else:
        historical_data.append(new_price_data)
        print(f"Added new data for {new_date}")

    # 5. Filter data to keep only the last 30 days
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    historical_data = [
        item for item in historical_data
        if datetime.strptime(item['asOfDate'], '%m/%d/%Y') > thirty_days_ago
    ]
    
    # 6. Save the updated list
    save_data(historical_data)
    
except (IOError, json.JSONDecodeError, AttributeError, ValueError) as e:
    print(f"Error processing data: {e}")

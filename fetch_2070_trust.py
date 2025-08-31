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
    new_data = json.loads(json_str)

    # 3. Read existing historical data
    historical_data = get_historical_data()
    
    # 4. Extract new data from the nested structure
    new_historical_entries = new_data['historicalPrice']['nav'][0]['item']
    
    # 5. Process and merge new entries with existing data
    for entry in new_historical_entries:
        # Convert the date format to match the previous one
        as_of_date_obj = datetime.strptime(entry['asOfDate'], '%Y-%m-%dT%H:%M:%S%z')
        formatted_date = as_of_date_obj.strftime('%m/%d/%Y')
        
        # Prepare the new entry in the desired format
        new_entry = {
            'asOfDate': formatted_date,
            'netAssetValue': entry['price'],
            'change': None,  # Data not available in new format
            'changePercentage': None # Data not available in new format
        }

        # Check if the date already exists to avoid duplicates
        if not any(item['asOfDate'] == formatted_date for item in historical_data):
            historical_data.append(new_entry)
            print(f"Added new data for {formatted_date}")

    # 6. Filter data to keep only the last 30 days
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    filtered_data = [
        item for item in historical_data
        if datetime.strptime(item['asOfDate'], '%m/%d/%Y') > thirty_days_ago
    ]
    
    # 7. Save the updated list
    save_data(filtered_data)
    
except (IOError, json.JSONDecodeError, AttributeError, ValueError, KeyError) as e:
    print(f"Error processing data: {e}")
    exit(1)

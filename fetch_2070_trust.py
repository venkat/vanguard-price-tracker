import requests
import urllib3
import json
import re
from datetime import datetime, timedelta

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The API endpoint and headers
api_url = "https://api.vanguard.com/rs/ire/01/pe/fund/M013/price/.jsonp?callback=angular.callbacks._2&planId=093926&portId=M013"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Referer": "https://investor.vanguard.com/"
}

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
    # 1. Read existing data
    historical_data = get_historical_data()
    
    # 2. Fetch the latest daily price
    # Add verify=False to ignore SSL certificate validation
    response = requests.get(api_url, headers=headers, verify=False)
    response.raise_for_status()
    
    jsonp_data = response.text
    json_str = re.search(r'\((\{.*\})\)', jsonp_data).group(1)
    new_price_data = json.loads(json_str)
    
    # Check if this date already exists to avoid duplicates
    new_date = new_price_data['asOfDate']
    if any(item['asOfDate'] == new_date for item in historical_data):
        print(f"Data for {new_date} already exists. No update needed.")
    else:
        historical_data.append(new_price_data)
        print(f"Added new data for {new_date}")

    # 3. Filter data to keep only the last 30 days
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # Filter using a list comprehension
    historical_data = [
        item for item in historical_data
        if datetime.strptime(item['asOfDate'], '%m/%d/%Y') > thirty_days_ago
    ]
    
    # 4. Save the updated list
    save_data(historical_data)
    
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
except (json.JSONDecodeError, AttributeError, ValueError) as e:
    print(f"Error processing data: {e}")

"""
Vanguard Target Retirement 2070 Trust Price Processor

This script processes raw JSONP data fetched from Vanguard's API and maintains
a rolling window of historical NAV (Net Asset Value) prices. The output JSON
is designed for import into Portfolio Performance.

Usage:
    1. The GitHub Actions workflow fetches raw data via wget to vanguard_raw.jsonp
    2. This script processes that file and updates vanguard_target_2070_trust_prices.json
    3. The JSON is published to GitHub Pages for Portfolio Performance to consume

Portfolio Performance JSON path configuration:
    - Date path: $[*].asOfDate
    - Quote path: $[*].netAssetValue
"""

import json
import re
from datetime import datetime, timedelta

def get_historical_data():
    """Reads the existing historical price data from the JSON file.

    Returns:
        list: Existing price entries, or empty list if file doesn't exist.
    """
    try:
        with open("vanguard_target_2070_trust_prices.json", "r") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data_list):
    """Saves the price data to the output JSON file.

    Args:
        data_list: List of price entry dictionaries to save.
    """
    with open("vanguard_target_2070_trust_prices.json", "w") as json_file:
        json.dump(data_list, json_file, indent=4)
    print("Successfully saved data to vanguard_target_2070_trust_prices.json")

# Configuration
ROLLING_WINDOW_DAYS = 90  # Number of days of historical data to retain

try:
    # Step 1: Read the raw JSONP data fetched by wget (from GitHub Actions workflow)
    with open("vanguard_raw.jsonp", "r") as raw_file:
        jsonp_data = raw_file.read()

    # Step 2: Extract JSON from JSONP response
    # The API returns JSONP format: angular.callbacks._2({...})
    # We use regex to extract the JSON object inside the parentheses
    json_str = re.search(r'\((\{.*\})\)', jsonp_data).group(1)
    new_data = json.loads(json_str)

    # Step 3: Load existing historical data to merge with new entries
    historical_data = get_historical_data()

    # Step 4: Extract price entries from the Vanguard API response
    # Note: The API only returns ~10 days of data, so we accumulate over time
    new_historical_entries = new_data['historicalPrice']['nav'][0]['item']

    # Step 5: Merge new entries with existing data, avoiding duplicates
    for entry in new_historical_entries:
        # Convert ISO date format (e.g., 2025-12-26T00:00:00-05:00) to MM/DD/YYYY
        # This format is expected by Portfolio Performance for parsing
        as_of_date_obj = datetime.strptime(entry['asOfDate'], '%Y-%m-%dT%H:%M:%S%z')
        formatted_date = as_of_date_obj.strftime('%m/%d/%Y')

        # Format entry for Portfolio Performance compatibility
        new_entry = {
            'asOfDate': formatted_date,
            'netAssetValue': entry['price'],
            'change': None,  # Not provided by API
            'changePercentage': None  # Not provided by API
        }

        # Only add if this date doesn't already exist (prevent duplicates)
        if not any(item['asOfDate'] == formatted_date for item in historical_data):
            historical_data.append(new_entry)
            print(f"Added new data for {formatted_date}")

    # Step 6: Apply rolling window - keep only the last N days of data
    today = datetime.now()
    cutoff_date = today - timedelta(days=ROLLING_WINDOW_DAYS)

    filtered_data = [
        item for item in historical_data
        if datetime.strptime(item['asOfDate'], '%m/%d/%Y') > cutoff_date
    ]

    # Step 7: Save the updated data
    save_data(filtered_data)
    
except (IOError, json.JSONDecodeError, AttributeError, ValueError, KeyError) as e:
    print(f"Error processing data: {e}")
    exit(1)

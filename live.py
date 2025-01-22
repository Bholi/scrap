import requests
import json
import csv
import time
import os
from datetime import datetime

def fetch_nepse_data(max_retries=3):
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://nepalstock.com/live-market',
        'Origin': 'https://nepalstock.com',
    }

    # API endpoint URL
    url = 'https://nepalstock.com/live-market'

    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1} of {max_retries}")
            
            # Make the API request
            response = requests.get(
                url, 
                headers=headers, 
                timeout=30,
                verify=False  # Disable SSL verification
            )
            response.raise_for_status()
            
            print(f"Successfully fetched data. Status code: {response.status_code}")
            
            # Parse JSON response
            data = response.json()
            
            # Save raw JSON for debugging
            os.makedirs('data', exist_ok=True)
            debug_file = f'data/debug_response_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Check if we have the expected data structure
            if not isinstance(data.get('records', []), list):
                print("Unexpected data format")
                print("Response structure:", json.dumps(data, indent=2)[:500])
                continue
            
            if not data['records']:
                print("No records found in the response")
                continue
            
            # Define CSV headers based on the data structure
            headers = [
                'Symbol', 'LTP', 'Change %', 'High', 'Low', 'Open',
                'Qty', 'Turnover', 'Previous Closing'
            ]
            
            # Prepare rows for CSV
            rows = []
            for record in data['records']:
                row = [
                    record.get('symbol', ''),
                    record.get('ltp', ''),
                    record.get('percentChange', ''),
                    record.get('high', ''),
                    record.get('low', ''),
                    record.get('open', ''),
                    record.get('quantity', ''),
                    record.get('turnover', ''),
                    record.get('previousClose', '')
                ]
                rows.append(row)
            
            print(f"Found {len(rows)} records")
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'data/nepal_stock_data_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"Data successfully saved to '{filename}'")
            
            # Optional: Display first few records
            print("\nFirst few records:")
            for row in rows[:3]:
                print(dict(zip(headers, row)))
            
            return True
            
        except requests.RequestException as e:
            print(f"Request error: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print("Raw response:", response.text[:500])
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        print(f"Attempt {attempt + 1} failed. Waiting before retry...")
        time.sleep(5)
    
    print("All attempts failed")
    return False

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    fetch_nepse_data()

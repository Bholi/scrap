import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime

def scrape_nepse_data(max_retries=3, wait_time=5):
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    url = 'https://nepalstock.com/live-market'

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple possible table classes
            table = None
            possible_classes = [
                'table table__border table__lg table-striped table__border--bottom table-head-fixed',
                'table',
                'table table-striped'
            ]
            
            for class_name in possible_classes:
                table = soup.find('table', class_=class_name)
                if table:
                    break
            
            if not table:
                print("Table not found in the HTML")
                continue
            
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.text.strip() for th in header_row.find_all('th')]
            
            if not headers:
                print("No headers found")
                continue
            
            # Extract rows
            tbody = table.find('tbody')
            if not tbody:
                print("No table body found")
                continue
                
            rows = []
            for tr in tbody.find_all('tr'):
                row_data = [td.text.strip() for td in tr.find_all('td')]
                if row_data:  # Only add non-empty rows
                    rows.append(row_data)
            
            if not rows:
                print("No data rows found")
                continue
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'nepal_stock_data_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"Data successfully scraped and saved to '{filename}'")
            return True
            
        except requests.RequestException as e:
            print(f"Request error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
        
        print(f"Attempt {attempt + 1} failed. Waiting before retry...")
        time.sleep(wait_time)
    
    print("All attempts failed")
    return False

if __name__ == "__main__":
    scrape_nepse_data()

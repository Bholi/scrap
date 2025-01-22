from requests_html import HTMLSession
import pandas as pd
import time
from datetime import datetime
import csv

def scrape_nepse_data(max_retries=3, wait_time=10):
    session = HTMLSession()
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            
            # Configure headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            # Make the request
            url = 'https://nepalstock.com/live-market'
            print("Accessing NEPSE live market...")
            response = session.get(url, headers=headers, verify=False)
            
            # Render JavaScript
            print("Rendering JavaScript content...")
            response.html.render(timeout=30, sleep=5)
            
            # Find the table
            print("Looking for market data table...")
            table = response.html.find('table.table.table__border.table__lg', first=True)
            
            if not table:
                print("Table not found, retrying...")
                time.sleep(wait_time)
                continue
            
            # Extract headers
            headers = []
            thead = table.find('thead', first=True)
            if thead:
                headers = [th.text.strip() for th in thead.find('th')]
            
            if not headers:
                print("No headers found, retrying...")
                time.sleep(wait_time)
                continue
                
            print("Found headers:", headers)
            
            # Extract rows
            rows = []
            tbody = table.find('tbody', first=True)
            if tbody:
                for tr in tbody.find('tr'):
                    row_data = [td.text.strip() for td in tr.find('td')]
                    if row_data:  # Only add non-empty rows
                        rows.append(row_data)
            
            if not rows:
                print("No data rows found, retrying...")
                time.sleep(wait_time)
                continue
                
            print(f"Found {len(rows)} rows of data")
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'nepse_live_market_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"Data successfully scraped and saved to '{filename}'")
            
            # Close the session
            session.close()
            return True
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            time.sleep(wait_time)
            continue
        
    print("All attempts failed")
    session.close()
    return False

if __name__ == "__main__":
    scrape_nepse_data()

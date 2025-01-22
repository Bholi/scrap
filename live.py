import httpx
import csv
from datetime import datetime
import time

def scrape_nepse_data(max_retries=3, wait_time=10):
    url = 'https://nepalstock.com/live-market'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")

            # Create an HTTP client with HTTP/2 support
            with httpx.Client(http2=True, verify=True) as client:
                print("Accessing NEPSE live market...")
                response = client.get(url, headers=headers, timeout=30)

            # Check HTTP status code
            if response.status_code != 200:
                print(f"Failed with status code: {response.status_code}")
                time.sleep(wait_time)
                continue

            # Parse the response content
            print("Processing market data...")
            html_content = response.text

            # Extract the table (adjust the selector based on NEPSE's actual HTML)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', class_='table table__border table__lg')

            if not table:
                print("Market data table not found, retrying...")
                time.sleep(wait_time)
                continue

            # Extract headers
            headers = [th.text.strip() for th in table.find('thead').find_all('th')]
            print("Found headers:", headers)

            # Extract rows
            rows = []
            tbody = table.find('tbody')
            for tr in tbody.find_all('tr'):
                row_data = [td.text.strip() for td in tr.find_all('td')]
                if row_data:
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
            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(wait_time)

    print("All attempts failed")
    return False

if __name__ == "__main__":
    scrape_nepse_data()

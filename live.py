import httpx
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import csv

def scrape_nepse_data_with_httpx():
    url = 'https://nepalstock.com/live-market'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }

    try:
        # Make a request using HTTP/2
        with httpx.Client(http2=True) as client:
            print("Accessing NEPSE live market using HTTP/2...")
            response = client.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return

        print("Page fetched successfully. Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the market data table
        table = soup.find('table', class_='table table__border table__lg')
        if not table:
            print("Market data table not found.")
            return

        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        print("Headers:", headers)

        # Extract rows
        rows = [
            [td.get_text(strip=True) for td in tr.find_all('td')]
            for tr in table.find('tbody').find_all('tr')
        ]
        print(f"Found {len(rows)} rows of data.")

        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'nepse_live_market_{timestamp}.csv'

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"Data successfully saved to '{filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_nepse_data_with_httpx()

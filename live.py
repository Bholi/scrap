import requests
import warnings
from bs4 import BeautifulSoup
import csv
import time

# Suppress SSL verification warnings for testing purposes
warnings.filterwarnings('ignore', category=requests.exceptions.InsecureRequestWarning)

def get_with_retries(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            # Send an HTTP GET request to the URL, disable SSL verification for testing
            response = requests.get(url, verify=False, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All attempts failed.")
                return None

def scrape_nepalstock_floor_sheet(url):
    try:
        # Get the webpage with retries
        response = get_with_retries(url)
        if not response:
            print("Failed to fetch the URL after retries.")
            return None
        
        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the specific table by class
        table = soup.find('table', class_='table table__lg table-striped table__border table__border--bottom')
        if not table:
            print("Table not found on the page.")
            return None
        
        # Extract headers from the table
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]
        print("Headers:", headers)
        
        # Extract rows from the table
        rows = []
        tbody = table.find('tbody')
        for tr in tbody.find_all('tr'):
            row_data = [td.text.strip() for td in tr.find_all('td')]
            if row_data:  # Only add non-empty rows
                rows.append(row_data)
        
        if not rows:
            print("No rows found in the table.")
            return None
        
        # Save the data to a CSV file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f'nepal_stock_floor_sheet_{timestamp}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write headers
            writer.writerows(rows)  # Write data rows
        
        print(f"Data successfully scraped and saved to '{filename}'.")
        return filename
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    url = "https://nepalstock.com/floor-sheet"
    scrape_nepalstock_floor_sheet(url)

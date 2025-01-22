import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_nepalstock_floor_sheet(url):
    try:
        # Send an HTTP GET request to the URL, disable SSL verification for debugging
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
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
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    url = "https://nepalstock.com/floor-sheet"
    scrape_nepalstock_floor_sheet(url)

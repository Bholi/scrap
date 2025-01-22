from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-certificate-errors')  # Handle SSL issues
    chrome_options.page_load_strategy = 'eager'  # Load faster
    
    service = Service('/usr/local/bin/chromedriver')
    
    try:
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error creating WebDriver: {str(e)}")
        raise

def wait_for_table_load(driver, timeout=60):
    """Wait for the table to be fully loaded"""
    try:
        # Wait for table to be present
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
        )
        
        # Wait for rows to be loaded (adjust the path as needed)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr"))
        )
        
        # Additional wait to ensure data is populated
        time.sleep(5)
        
        return True
    except TimeoutException:
        print("Timeout waiting for table to load")
        return False

def scrape_nepse_data(max_retries=3):
    for attempt in range(max_retries):
        driver = None
        try:
            print(f"\nAttempt {attempt + 1} of {max_retries}")
            
            driver = setup_driver()
            print("WebDriver initialized successfully")
            
            # Open the webpage
            url = 'https://nepalstock.com/live-market'
            print(f"Accessing URL: {url}")
            driver.get(url)
            
            # Wait for initial page load
            print("Waiting for page to load...")
            time.sleep(10)  # Initial wait
            
            # Wait for table to be loaded
            if not wait_for_table_load(driver):
                print("Table did not load properly")
                continue
            
            print("Table appears to be loaded, extracting data...")
            
            # Get page source after JavaScript execution
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Save HTML for debugging
            debug_file = f'debug_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            # Find the table
            table = soup.find('table', class_='table')
            
            if not table:
                print("Table not found after waiting")
                continue
            
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.text.strip() for th in header_row.find_all('th')]
            
            if not headers:
                print("No headers found")
                continue
            
            print(f"Found headers: {headers}")
            
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
            
            print(f"Found {len(rows)} rows of data")
            
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'data/nepal_stock_data_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"Data successfully scraped and saved to '{filename}'")
            return True
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            
        print(f"Attempt {attempt + 1} failed. Waiting before retry...")
        time.sleep(10)  # Longer wait between attempts
    
    print("All attempts failed")
    return False

if __name__ == "__main__":
    scrape_nepse_data()

import logging
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='nepse_scraper_debug.log'
)

def setup_driver():
    try:
        # Create a unique temporary directory for Chrome user data
        user_data_dir = tempfile.mkdtemp(prefix='chrome_profile_')
        
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service('/usr/local/bin/chromedriver')
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver, user_data_dir
    except Exception as e:
        logging.error(f"Driver setup failed: {e}")
        raise

def scrape_nepse_data():
    driver = None
    user_data_dir = None
    
    try:
        # Setup driver with unique profile
        driver, user_data_dir = setup_driver()
        
        # Open the webpage
        url = 'https://nepalstock.com/live-market'
        driver.get(url)
        
        # Extended wait
        time.sleep(10)
        
        # Capture page source
        page_source = driver.page_source
        logging.info(f"Page source length: {len(page_source)}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find tables
        tables = soup.find_all('table')
        logging.info(f"Found {len(tables)} tables")
        
        if not tables:
            logging.warning("No tables found in page source")
            return False
        
        # Extract data from first table
        first_table = tables[0]
        headers = [th.text.strip() for th in first_table.find_all('th')]
        rows = []
        for tr in first_table.find_all('tr')[1:]:  # Skip header row
            row_data = [td.text.strip() for td in tr.find_all('td')]
            if row_data:
                rows.append(row_data)
        
        if not rows:
            logging.warning("No data rows found")
            return False
        
        # Save to CSV
        output_dir = 'nepse_data'
        os.makedirs(output_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f'nepal_stock_data_{timestamp}.csv')
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)
        
        logging.info(f"Data successfully scraped and saved to '{filename}'")
        return True
        
    except Exception as e:
        logging.error(f"Scraping error: {e}")
        return False
    finally:
        # Close driver and clean up temporary profile directory
        if driver:
            driver.quit()
        if user_data_dir and os.path.exists(user_data_dir):
            import shutil
            shutil.rmtree(user_data_dir)

if __name__ == "__main__":
    scrape_nepse_data()

import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import csv
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='nepse_scraper_debug.log'
)

def setup_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logging.error(f"Driver setup failed: {e}")
        logging.error(traceback.format_exc())
        raise

def scrape_nepse_data(max_retries=3, wait_time=30):
    # Ensure output directory exists
    output_dir = 'nepse_data'
    os.makedirs(output_dir, exist_ok=True)

    for attempt in range(max_retries):
        driver = None
        try:
            logging.info(f"Attempt {attempt + 1} of {max_retries}")
            
            driver = setup_driver()
            
            # Open the webpage
            url = 'https://nepalstock.com/live-market'
            driver.get(url)
            
            # Add initial wait for page load
            time.sleep(5)
            
            # Wait for table with multiple possible selectors
            table_selectors = [
                "table.table",
                "table.table__border",
                ".table-responsive table"
            ]
            
            table_found = False
            for selector in table_selectors:
                try:
                    WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    table_found = True
                    logging.info(f"Table found using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not table_found:
                logging.warning("Could not find table with any selector")
                continue
            
            # Get page source and parse
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            
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
                logging.warning("Table not found in the HTML")
                continue
            
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.text.strip() for th in header_row.find_all('th')]
            
            if not headers:
                logging.warning("No headers found")
                continue
            
            # Extract rows
            tbody = table.find('tbody')
            if not tbody:
                logging.warning("No table body found")
                continue
                
            rows = []
            for tr in tbody.find_all('tr'):
                row_data = [td.text.strip() for td in tr.find_all('td')]
                if row_data:  # Only add non-empty rows
                    rows.append(row_data)
            
            if not rows:
                logging.warning("No data rows found")
                continue
            
            # Save to CSV
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f'nepal_stock_data_{timestamp}.csv')
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            logging.info(f"Data successfully scraped and saved to '{filename}'")
            return True
            
        except WebDriverException as e:
            logging.error(f"WebDriver error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
        finally:
            if driver:
                driver.quit()
        
        logging.warning(f"Attempt {attempt + 1} failed. Waiting before retry...")
        time.sleep(5)
    
    logging.error("All attempts failed")
    return False

if __name__ == "__main__":
    try:
        success = scrape_nepse_data()
        if not success:
            logging.error("NEPSE data scraping was unsuccessful")
    except Exception as e:
        logging.critical(f"Critical error in main execution: {e}")
        logging.critical(traceback.format_exc())

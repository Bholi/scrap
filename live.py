import undetected_chromedriver as uc
import logging
import os
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
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        logging.error(f"Driver setup failed: {e}")
        raise

def scrape_nepse_data():
    driver = None
    
    try:
        driver = setup_driver()
        
        url = 'https://nepalstock.com/live-market'
        driver.get(url)
        
        time.sleep(10)
        
        page_source = driver.page_source
        logging.info(f"Page source length: {len(page_source)}")
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        tables = soup.find_all('table')
        logging.info(f"Found {len(tables)} tables")
        
        if not tables:
            logging.warning("No tables found in page source")
            return False
        
        first_table = tables[0]
        headers = [th.text.strip() for th in first_table.find_all('th')]
        rows = []
        for tr in first_table.find_all('tr')[1:]:
            row_data = [td.text.strip() for td in tr.find_all('td')]
            if row_data:
                rows.append(row_data)
        
        if not rows:
            logging.warning("No data rows found")
            return False
        
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
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_nepse_data()

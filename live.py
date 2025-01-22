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

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")  # Required for running in Docker/VPS
    chrome_options.add_argument("--disable-dev-shm-usage")  # Required for running in Docker/VPS
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Set up ChromeDriver service
    service = Service('/usr/local/bin/chromedriver')
    
    try:
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error creating WebDriver: {str(e)}")
        raise

def scrape_nepse_data(max_retries=3, wait_time=30):
    for attempt in range(max_retries):
        driver = None
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            
            driver = setup_driver()
            print("WebDriver initialized successfully")
            
            # Open the webpage
            url = 'https://nepalstock.com/live-market'
            print(f"Accessing URL: {url}")
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
                    print(f"Trying selector: {selector}")
                    WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    table_found = True
                    print(f"Table found using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not table_found:
                print("Could not find table with any selector")
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
                    print(f"Found table with class: {class_name}")
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
            
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Save to CSV
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'data/nepal_stock_data_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            
            print(f"Data successfully scraped and saved to '{filename}'")
            return True
            
        except WebDriverException as e:
            print(f"WebDriver error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"Error closing driver: {str(e)}")
        
        print(f"Attempt {attempt + 1} failed. Waiting before retry...")
        time.sleep(5)
    
    print("All attempts failed")
    return False

if __name__ == "__main__":
    scrape_nepse_data()

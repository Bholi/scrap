import time
from datetime import datetime
import logging
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def floorsheet_scraper():
    """
    Scrape floorsheet data from NEPSE and save it to a CSV file.
    Automatically stops when scraping is complete for the day.
    """
    url = "https://www.nepalstock.com/floor-sheet"
    output_file = "floorsheet_data.csv"
    driver = None

    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    logger.info("Starting the scraper...")

    try:
        # Initialize the browser
        logger.debug("Initializing the browser...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Set an explicit timeout for the driver
        driver.set_page_load_timeout(120)

        # Load the page
        logger.info("Loading the NEPSE Floorsheet page...")
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.table__asofdate span')))

        # Scrape the date
        logger.debug("Scraping the date from the page...")
        date_element = driver.find_element(By.CSS_SELECTOR, 'div.table__asofdate span')
        date_text = date_element.text.replace("As of", "").strip()
        scrape_date = datetime.strptime(date_text, "%b %d, %Y, %I:%M:%S %p").date()
        logger.info(f"Scraped Date: {scrape_date}")

        # Select 500 records per page
        logger.debug("Selecting 500 records per page...")
        wait = WebDriverWait(driver, 10)
        select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
        select_dropdown = Select(select_element)
        select_dropdown.select_by_value('500')

        # Click the Filter button
        logger.debug("Clicking the Filter button...")
        filter_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.box__filter--search')))
        filter_button.click()
        time.sleep(5)  # Wait for the data to load

        # Open the CSV file for writing
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Transaction No', 'Symbol', 'Buyer', 'Seller', 'Quantity', 'Rate', 'Amount', 'Date'])

            # Scrape table data page by page
            while True:
                logger.debug("Scraping data from the current page...")
                rows = driver.find_elements(By.CSS_SELECTOR, 'table.table__lg tbody tr')
                logger.info(f"Found {len(rows)} rows on this page.")

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 7:  # Ensure row has enough data
                        data = [
                            cells[1].text.strip(),  # Transaction No
                            cells[2].text.strip(),  # Symbol
                            cells[3].text.strip(),  # Buyer
                            cells[4].text.strip(),  # Seller
                            cells[5].text.strip(),  # Quantity
                            cells[6].text.strip(),  # Rate
                            cells[7].text.strip(),  # Amount
                            scrape_date  # Date
                        ]
                        writer.writerow(data)

                # Check for pagination (Next button)
                try:
                    next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
                    if 'disabled' in next_button.get_attribute('class'):
                        logger.info("No more pages to scrape.")
                        break  # Exit loop if 'Next' is disabled
                    next_button.click()
                    time.sleep(2)  # Wait for the next page to load
                except NoSuchElementException:
                    logger.info("Next button not found. Scraping complete.")
                    break

        logger.info(f"Successfully scraped and saved floorsheet data to {output_file}.")

    except TimeoutException:
        logger.error("Page took too long to load. Exiting.")
    except WebDriverException as e:
        logger.error(f"WebDriver error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
        logger.info("Browser closed.")

if __name__ == "__main__":
    floorsheet_scraper()

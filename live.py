import time
from datetime import datetime
import logging
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def floorsheet_scraper():
    url = "https://www.nepalstock.com/floor-sheet"
    output_file = "floorsheet_data.csv"
    driver = None

    # Set up headless Chrome
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    logger.info("Starting the scraper...")

    try:
        logger.debug("Initializing the browser...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)

        logger.info("Loading the NEPSE Floorsheet page...")
        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 20)
        date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.table__asofdate span')))
        date_text = date_element.text.replace("As of", "").strip()
        scrape_date = datetime.strptime(date_text, "%b %d, %Y, %I:%M:%S %p").date()
        logger.info(f"Scraped Date: {scrape_date}")

        logger.debug("Selecting 500 records per page...")
        select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
        Select(select_element).select_by_value('500')

        filter_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.box__filter--search')))
        filter_button.click()

        # Wait for the table to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table__lg tbody tr')))

        # Open CSV file
        file_exists = os.path.exists(output_file)
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Transaction No', 'Symbol', 'Buyer', 'Seller', 'Quantity', 'Rate', 'Amount', 'Date'])

            while True:
                rows = driver.find_elements(By.CSS_SELECTOR, 'table.table__lg tbody tr')
                logger.info(f"Found {len(rows)} rows on this page.")

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 7:
                        data = [
                            cells[1].text.strip(),
                            cells[2].text.strip(),
                            cells[3].text.strip(),
                            cells[4].text.strip(),
                            cells[5].text.strip(),
                            cells[6].text.strip(),
                            cells[7].text.strip(),
                            scrape_date
                        ]
                        writer.writerow(data)

                try:
                    next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
                    if 'disabled' in next_button.get_attribute('class'):
                        logger.info("No more pages to scrape.")
                        break
                    next_button.click()
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table__lg tbody tr')))
                except NoSuchElementException:
                    logger.info("Pagination ended.")
                    break

        logger.info(f"Successfully scraped and saved data to {output_file}.")

    except TimeoutException:
        logger.error("Page load timed out.")
    except WebDriverException as e:
        logger.error(f"WebDriver error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if driver:
            driver.quit()
        logger.info("Browser closed.")

if __name__ == "__main__":
    floorsheet_scraper()

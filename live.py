import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)

def floorsheet_scraper():
    """
    Scrape floorsheet data from NEPSE and save it to a CSV file.
    Automatically stops when scraping is complete for the day.
    """
    url = "https://www.nepalstock.com/floor-sheet"
    driver = webdriver.Chrome()  # Assumes chromedriver is in PATH

    # CSV file setup
    csv_filename = f"floorsheet_data_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['transaction_no', 'symbol', 'buyer', 'seller', 'quantity', 'rate', 'amount', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write CSV header

        try:
            # Load the page
            print("Loading the NEPSE Floorsheet page...")
            driver.get(url)
            time.sleep(5)  # Wait for the page to load

            # Scrape the date
            date_element = driver.find_element(By.CSS_SELECTOR, 'div.table__asofdate span')
            date_text = date_element.text.replace("As of", "").strip()
            scrape_date = datetime.strptime(date_text, "%b %d, %Y, %I:%M:%S %p").date()
            print(f"Scraped Date: {scrape_date}")

            # Select 500 records per page
            wait = WebDriverWait(driver, 10)  # Maximum wait time of 10 seconds
            select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
            select_dropdown = Select(select_element)
            select_dropdown.select_by_value('500')

            # Click the Filter button
            filter_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.box__filter--search')))
            filter_button.click()
            time.sleep(5)  # Wait for the data to load

            # Scrape table data page by page
            while True:
                rows = driver.find_elements(By.CSS_SELECTOR, 'table.table__lg tbody tr')
                print(f"Found {len(rows)} rows on this page.")

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 7:  # Ensure row has enough data
                        data = {
                            'transaction_no': cells[1].text.strip(),
                            'symbol': cells[2].text.strip(),
                            'buyer': cells[3].text.strip(),
                            'seller': cells[4].text.strip(),
                            'quantity': cells[5].text.strip(),
                            'rate': cells[6].text.strip(),
                            'amount': cells[7].text.strip(),
                            'date': scrape_date
                        }
                        writer.writerow(data)  # Write data to CSV file

                # Check for pagination (Next button)
                try:
                    next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
                    if 'disabled' in next_button.get_attribute('class'):
                        break  # Exit loop if 'Next' is disabled
                    next_button.click()
                    time.sleep(2)  # Wait for the next page to load
                except NoSuchElementException:
                    break

            print(f"Successfully scraped and saved floorsheet data to {csv_filename}.")

        except TimeoutException:
            print("Page took too long to load. Exiting.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()

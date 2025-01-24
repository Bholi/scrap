from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configure Chrome options
def get_chrome_options():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")  # Required for running as root in Docker or Linux
    options.add_argument("--disable-dev-shm-usage")  # Use /dev/shm to avoid limited memory issues
    options.add_argument("--disable-gpu")  # Disable GPU (required for some platforms in headless mode)
    options.add_argument("--remote-debugging-port=9222")  # Enable debugging
    options.add_argument("--window-size=1920,1080")  # Set consistent window size
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return options

# Initialize WebDriver
def initialize_driver():
    logging.debug("Initializing the Chrome WebDriver...")
    try:
        service = Service("/usr/local/bin/chromedriver")  # Path to chromedriver
        options = get_chrome_options()
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logging.error(f"Error initializing the WebDriver: {e}")
        raise

# Example scraping function
def scrape_example():
    driver = None
    try:
        # Initialize driver
        driver = initialize_driver()
        logging.debug("Driver initialized successfully.")

        # Navigate to a website (e.g., Google)
        logging.debug("Navigating to Google...")
        driver.get("https://www.google.com")
        logging.debug("Page loaded successfully.")

        # Interact with the page (example: search for 'Python')
        logging.debug("Finding the search bar and performing a search...")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Python")
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load (implicit wait recommended)
        driver.implicitly_wait(5)

        # Scrape the results
        logging.debug("Extracting search result titles...")
        results = driver.find_elements(By.CSS_SELECTOR, "h3")
        for idx, result in enumerate(results[:5], start=1):  # Top 5 results
            logging.info(f"Result {idx}: {result.text}")

    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    finally:
        # Ensure the driver is closed properly
        if driver:
            driver.quit()
            logging.debug("Driver closed successfully.")

# Run the scraper
if __name__ == "__main__":
    logging.info("Starting the scraper...")
    scrape_example()
    logging.info("Scraper finished.")

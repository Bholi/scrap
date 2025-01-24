import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configure Chrome options
def get_chrome_options():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")  # Required for running as root in Docker or Linux
    options.add_argument("--disable-dev-shm-usage")  # Avoid limited memory issues
    options.add_argument("--disable-gpu")  # Disable GPU
    options.add_argument("--remote-debugging-port=9222")  # Enable debugging
    options.add_argument("--window-size=1920,1080")  # Set consistent window size
    options.add_argument("--user-data-dir=/tmp/unique-chrome-profile")  # Use a unique user-data directory
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    return options

# Initialize the WebDriver
def initialize_webdriver():
    logging.debug("Initializing the Chrome WebDriver...")
    service = Service("/usr/local/bin/chromedriver")  # Path to your ChromeDriver
    options = get_chrome_options()

    try:
        driver = webdriver.Chrome(service=service, options=options)
        logging.debug("WebDriver successfully initialized.")
        return driver
    except WebDriverException as e:
        logging.error(f"Error initializing the WebDriver: {e}")
        raise

# Main scraping logic
def scrape():
    logging.info("Starting the scraper...")
    driver = initialize_webdriver()

    try:
        # Example URL to scrape
        url = "https://example.com"
        logging.debug(f"Navigating to {url}")
        driver.get(url)

        # Example of extracting data
        page_title = driver.title
        logging.info(f"Page title: {page_title}")

    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")

    finally:
        driver.quit()
        logging.debug("WebDriver session closed.")

# Run the scraper
if __name__ == "__main__":
    scrape()

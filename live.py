import logging
import subprocess
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='webdriver_diagnosis.log'
)

def run_system_checks():
    try:
        # Check Chrome version
        chrome_version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8').strip()
        logging.info(f"Chrome Version: {chrome_version}")

        # Check ChromeDriver version
        chromedriver_version = subprocess.check_output(['chromedriver', '--version']).decode('utf-8').strip()
        logging.info(f"ChromeDriver Version: {chromedriver_version}")

        # Check system architecture
        arch_output = subprocess.check_output(['uname', '-m']).decode('utf-8').strip()
        logging.info(f"System Architecture: {arch_output}")
    except Exception as e:
        logging.error(f"System check error: {e}")

def setup_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-level=3")

        # Try different service configurations
        service_paths = [
            '/usr/local/bin/chromedriver',
            '/usr/bin/chromedriver',
            subprocess.check_output(['which', 'chromedriver']).decode('utf-8').strip()
        ]

        last_exception = None
        for driver_path in service_paths:
            try:
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logging.info(f"Successfully created driver using path: {driver_path}")
                return driver
            except Exception as e:
                logging.error(f"Failed with path {driver_path}: {e}")
                last_exception = e

        raise last_exception if last_exception else Exception("No valid ChromeDriver path found")

    except Exception as e:
        logging.error(f"Comprehensive driver setup error: {e}")
        logging.error(traceback.format_exc())
        raise

def main():
    run_system_checks()
    
    try:
        driver = setup_driver()
        driver.get('https://nepalstock.com/live-market')
        
        # Extended diagnostic information
        logging.info(f"Current URL: {driver.current_url}")
        logging.info(f"Page Title: {driver.title}")
        
        # Save page source for inspection
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        driver.quit()
    except Exception as e:
        logging.critical(f"Diagnosis failed: {e}")
        logging.critical(traceback.format_exc())

if __name__ == "__main__":
    main()

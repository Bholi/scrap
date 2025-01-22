import requests
from bs4 import BeautifulSoup

def simple_scraper(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all <p> tags
        paragraphs = [p.text.strip() for p in soup.find_all('p')]
        print("Paragraphs:")
        for para in paragraphs:
            print(para)
        
        # Extract all <h1> tags
        headings = [h1.text.strip() for h1 in soup.find_all('h1')]
        print("\nHeadings:")
        for heading in headings:
            print(heading)
        
        return {
            "paragraphs": paragraphs,
            "headings": headings
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

if __name__ == "__main__":
    url = "https://example.com"
    result = simple_scraper(url)
    if result:
        print("\nScraping completed successfully.")

import requests
from bs4 import BeautifulSoup as bs
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())  # Automatically downloads the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def find_privacy_policy_link(url, output_file="privacy_policy_link.txt"):
    """
    Finds and saves a privacy policy link on a website, using Selenium for JavaScript-heavy sites.

    Args:
        url (str): URL of the main website (e.g., "https://stripe.com").
        output_file (str): File to save the privacy policy link.

    Returns:
        str: Privacy policy URL or None if not found.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    session = requests.Session()
    retries = Retry(total=2, backoff_factor=1, status_forcelist=[403, 429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update(headers)

    try:
        response = session.get(url, timeout=3)
        response.raise_for_status()
        soup = bs(response.text, 'html.parser')
        
        # First check all <a> tags for "privacy" in href or text
        link_url = None
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            if 'privacy' in href.lower() or 'privacy' in text:
                link_url = href
                break
        
        # Convert relative URL to absolute if necessary
        if link_url and not link_url.startswith('http'):
            link_url = requests.compat.urljoin(url, link_url)

        # If no link was found, try with Selenium for JavaScript-heavy sites
        if not link_url:
            print("Attempting with Selenium for JavaScript-rendered content...")
            driver = setup_selenium_driver()
            driver.get(url)

            try:
                # Wait for footer to load, if it exists
                WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "privacy")))
                soup = bs(driver.page_source, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text(strip=True).lower()
                    if 'privacy' in href.lower() or 'privacy' in text:
                        link_url = href
                        break
            finally:
                driver.quit()

        # Save found link or return None
        if link_url:
            if not link_url.startswith('http'):
                link_url = requests.compat.urljoin(url, link_url)
            with open(output_file, 'w') as file:
                file.write(link_url)
            print(f"Privacy policy found: {link_url}")
            return link_url
        else:
            print("Privacy policy link not found.")
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


  


# Testing `find_privacy_policy_link` function with various popular websites
# honestly think some of them aren't automatable since they are platforms that can't 
# find_privacy_policy_link("https://google.com")
# find_privacy_policy_link("https://facebook.com") // 400 bad client everytime
# find_privacy_policy_link("https://twitter.com")
# find_privacy_policy_link("https://linkedin.com")
# find_privacy_policy_link("https://amazon.com")
# find_privacy_policy_link("https://apple.com")
# find_privacy_policy_link("https://netflix.com")
# find_privacy_policy_link("https://microsoft.com")
# find_privacy_policy_link("https://adobe.com/ca") // selenium can't handle, maybe a longer wait?
# find_privacy_policy_link("https://open.spotify.com/") // selenium can't handle, maybe a longer wait?
# find_privacy_policy_link("https://zoom.us") // selenium can't handle, maybe a longer wait?
# find_privacy_policy_link("https://paypal.com")
# find_privacy_policy_link("https://salesforce.com") // selenium can't handle, maybe a longer wait?
# find_privacy_policy_link("https://dropbox.com")
# find_privacy_policy_link("https://airbnb.com") // selenium can't handle, maybe a longer wait?
# find_privacy_policy_link("https://github.com")
# find_privacy_policy_link("https://stripe.com")
# find_privacy_policy_link("https://tesla.com") // probably blocked
# find_privacy_policy_link("https://oracle.com") // selenium can't handle, maybe a longer wait?
# find_privacy_policy_link("https://uber.com")
# find_privacy_policy_link("https://openai.com/")  // probably blocked 



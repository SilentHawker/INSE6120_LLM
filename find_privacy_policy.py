from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import WebDriverException
from urllib.parse import urljoin


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-http2')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                            options=chrome_options)


def find_links_by_keywords(driver, keywords):
    """Find links containing any of the given keywords in href or text"""
    all_matching_links = []

    for keyword in keywords:
        xpath_expressions = [
            f"//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{keyword.lower()}')]",
            f"//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{keyword.lower()}')]"
        ]

        for xpath in xpath_expressions:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                href = element.get_attribute('href')
                text = element.text
                if href:
                    all_matching_links.append({
                        'href': href,
                        'text': text,
                        'keyword': keyword
                    })

    return all_matching_links


def find_privacy_policy_link(url):
    driver = None
    try:
        print(f"\nStep 1: Accessing initial URL: {url}")
        driver = setup_driver()
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(10)

        # First, find policy/privacy related links
        print("\nSearching for initial policy/privacy links...")
        initial_keywords = ['policy', 'privacy', 'legal']
        initial_links = find_links_by_keywords(driver, initial_keywords)

        if not initial_links:
            print("No initial policy links found")
            return None

        # Filter and prioritize links
        policy_page_link = None
        for link in initial_links:
            href = link['href']
            # Prioritize links that look like policy pages
            if any(x in href.lower() for x in ['/privacy', 'privacy', '_privacy', '-privacy', '/policy', '/legal']):
                policy_page_link = href
                print(f"\nFound policy page: {policy_page_link}")
                break

        if not policy_page_link:
            return None

        # Navigate to the policy page
        print(f"\nStep 2: Navigating to policy page: {policy_page_link}")
        driver.get(policy_page_link)
        # time.sleep(5)

        # Look for specific privacy policy link
        print("\nSearching for specific privacy policy link...")
        privacy_keywords = ['privacy policy',
                            'privacy statement', 'data protection']
        privacy_links = find_links_by_keywords(driver, privacy_keywords)

        # Filter for the most likely privacy policy link
        final_link = None
        for link in privacy_links:
            href = link['href']
            # Look for URLs that specifically indicate privacy policy
            if 'privacy' in href.lower() or 'privacy/policy' in href.lower() or 'privacy-policy' in href.lower() or 'privacy policy' in link['text'].lower():
                final_link = href
                print(f"\nFound specific privacy policy: {final_link}")
                break

        return final_link if final_link else policy_page_link

    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()


# Test the function
if __name__ == "__main__":
    test_urls = [
        "https://airbnb.com",
        "https://replika.com",
        "https://oracle.com",
        "https://openai.com",
        "https://salesforce.com",
        "https://www.adobe.com",
        "https://www.amazon.com",
        "https://www.facebook.com",
        "https://open.spotify.com",
        "https://tesla.com",
        "https://zoom.us",
        "https://twitter.com",
        "https://microsoft.com",
        "https://google.com",
        "https://linkedin.com",
        "https://github.com",
        "https://instagram.com",
        "https://wikipedia.org",
        "https://bbc.com",
        "https://nytimes.com",
        "https://stackoverflow.com",
        "https://reddit.com",
        "https://wordpress.com",
        "https://pinterest.com",
        "https://yahoo.com",
        "https://ebay.com",
        "https://paypal.com",
        "https://snapchat.com",
        "https://discord.com",
    ]

    for test_url in test_urls:
        print(f"\nTesting URL: {test_url}")
        result = find_privacy_policy_link(test_url)
        print(f"Final privacy policy URL: {result}")
        print("-" * 50)

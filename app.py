from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import WebDriverException
from urllib.parse import urljoin
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from bs4 import BeautifulSoup as bs
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import (
    StreamingStdOutCallbackHandler,
)

app = Flask(__name__)

# ----------------------------- Model set up ----------------------------- #


def setup_model():

    with open('prompt_template.txt', 'r') as file:
        template = file.read()

    callback_man = CallbackManager([StreamingStdOutCallbackHandler()])
    model = OllamaLLM(model="llama3.2",
                      callback_manager=callback_man, temperature=0.4, num_ctx=1024)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    return chain

# ----------------------------- Summarization process ----------------------------- #


def extract_policy_text(html):
    """
    Extracts the visible text content from the provided HTML code of a privacy policy page.

    Args:
        html (str): The HTML content as a string from which the policy text will be extracted.

    Returns:
        str: A string containing the visible text content from the HTML, separated by new lines.
    """

    soup = bs(html.content, 'html.parser')
    body = soup.find('body')
    policy_text = body.get_text(separator="\n").strip()
    return policy_text


def handle_summarization(chain, policy_text):
    """
    Handles the process of summarizing a privacy policy using a local language model (LocalLLM).

    This function prints a message indicating the start of the summarization process and invokes
    the language model to generate a summary of the provided policy text.

    Args:
        None

    Returns:
        None
    """
    print("\nStep 3: Summarizing the privacy policy...\n")
    result = chain.invoke({"policy_text": policy_text})

    return result

# ----------------------------- Policy URL finding process ----------------------------- #


def setup_driver():
    """
    Sets up and returns a headless Chrome WebDriver for browser automation.

    Configures Chrome with options to run in headless mode,
    disable unnecessary features, and use a custom user-agent.

    Args:
        None

    Returns:
        WebDriver: A configured Chrome WebDriver instance.
    """

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
    """
    Searches for links containing the specified keywords in their text or href.

    Args:
        driver (WebDriver): Selenium WebDriver to interact with the page.
        keywords (list): Keywords to search for.

    Returns:
        list: A list of dictionaries with href, text, and matching keyword.
    """

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
    """
    Finds and returns the most relevant privacy policy link from a given URL.

    Args:
        url (str): The website URL to search.

    Returns:
        str or None: The privacy policy link, or None if not found.
    """

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
            msg = "No initial policy links found"
            print("[-] "+msg)
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
                print(f"\nFound specific privacy policy: {final_link}\n")
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


@app.route('/search_privacy_policy', methods=['POST'])
def search_privacy_policy():
    data = request.json
    url = data.get('website_url', '')
    print(url)
    privacy_policy_url = find_privacy_policy_link(url)

    if not privacy_policy_url:
        return jsonify({'error': "Unable to find privacy policy page, please try another website.", })
    else:
        try:
            model_chain = setup_model()
            html_as_string = requests.get(privacy_policy_url)
            policy_text = extract_policy_text(html_as_string)
            summary = handle_summarization(model_chain, policy_text)
            return jsonify({'success': summary, })
        except Exception as e:
            print("[-]Error: "+e)
        return jsonify({'error': "Error while summarizing, please try again or try another website.", })


if __name__ == '__main__':
    app.run(port=8000)

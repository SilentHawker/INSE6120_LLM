from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def find_privacy_policy_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Search for links that likely point to a privacy policy
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if "privacy" in href and ("policy" in href or "terms" in href):
                return link['href']
        return "Privacy policy link not found."
    except Exception as e:
        return str(e)

@app.route('/search_privacy_policy', methods=['POST'])
def search_privacy_policy():
    data = request.json
    url = data.get('url', '')
    privacy_policy_url = find_privacy_policy_url(url)
    return jsonify({"privacy_policy_url": privacy_policy_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

def scrape_city_data(user_query, max_results=3):
    url = "https://www.cityofsacramento.gov/community-development"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch the webpage. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    data = []

    for link in soup.find_all('a', href=True):
        title = link.get_text(strip=True)
        href = link['href']
        full_url = urljoin(url, href)

        if not title or 'javascript:void(0);' in href:
            continue

        data.append({"title": title, "url": full_url})

    filtered_data = []
    for link in data:
        if any(word.lower() in link["title"].lower() for word in user_query.split()):
            filtered_data.append(link)

    # Limit to 3 results only
    filtered_data = filtered_data[:max_results]

    # Simple JSON response (no listSelect to reduce payload size)
    formatted_data = {
        "fulfillmentText": "Here are some links related to your query:",
        "links": [{"title": link["title"], "url": link["url"]} for link in filtered_data]
    }

    return formatted_data

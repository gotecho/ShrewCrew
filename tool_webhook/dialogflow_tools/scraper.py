from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

SOURCE_URLS = [
    "https://www.cityofsacramento.gov/community-development",
    "https://www.cityofsacramento.gov/public-works",
    "https://codelibrary.amlegal.com/codes/sacramentoca/latest/sacramento_ca/0-0-0-1"
]

def scrape_city_data(user_query, max_results=3):
    all_links = []

    # Scrape the data from the specified URLs
    for url in SOURCE_URLS:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Warning: Failed to fetch {url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                title = link.get_text(strip=True)
                href = link['href']
                full_url = urljoin(url, href)

                if not title or 'javascript:void(0);' in href:
                    continue

                all_links.append({"title": title, "url": full_url})
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    # Filter the links based on the user query
    filtered_data = [
        link for link in all_links
        if any(word.lower() in link["title"].lower() for word in user_query.split())
    ][:max_results]

    # Build the response as per Google Conversational Agent format
    response = {
        "fulfillmentText": "Here are some links related to your query:",
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Here are some links related to your query:"
                    ]
                }
            },
            {
                "listSelect": {
                    "title": "Relevant Pages",  # Optional title
                    "items": [
                        {
                            "title": link["title"],
                            "optionInfo": {
                                "key": link["url"],
                                "synonyms": [link["url"]]
                            }
                        }
                        for link in filtered_data
                    ]
                }
            }
        ]
    }

    # Return the response including both the text message and the listSelect
    return response

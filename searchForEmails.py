import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import sys
import os

########################################################
# Function to get path to resource (works for PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Scrape for websites using DuckDuckGo
def getWebsites(town, state, agencyType, numberOfWebsites):
    query = f"{town} {state} {agencyType} official website"
    base_url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    websites = []

    try:
        response = requests.post(base_url, data={"q": query}, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a", href=True)

        for link in results:
            url = link["href"]

            # DuckDuckGo sometimes wraps URLs
            if url.startswith("/"):
                url = urljoin("https://duckduckgo.com", url)

            # Skip junk links
            if "duckduckgo.com" in url:
                continue

            websites.append(url)

            if len(websites) >= numberOfWebsites:
                break

    except Exception as e:
        print("Search error:", e)

    print(f"Found {len(websites)} websites for {query}")
    return websites


# Scrape each website for emails
def getEmails(websites):
    townEmails = []
    emailURL = []

    for site in websites:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(site, headers=headers, timeout=10)
            htmlContent = response.text

            soup = BeautifulSoup(htmlContent, 'html.parser')
            text = soup.get_text()

            emailPattern = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,})')
            emailMatches = re.findall(emailPattern, text)

            for email in emailMatches:
                if email not in townEmails:
                    townEmails.append(email)
                    emailURL.append(site)

        except:
            print("     Error scraping " + site)

    return townEmails, emailURL

from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re

# Get a list of websites from the first 10 google search results
def getWebsites(town,state,agencyType,numberOfWebsites):
    websites = []
    searchTerm = " ".join([town,state,agencyType])
    
    for result in search(searchTerm, tld="co.in", num=10, stop=numberOfWebsites, pause=2):
        websites.append(result)
    return websites


# Scrape each website for emails
def getEmails(websites):
    townEmails = []

    for site in websites:
        try:
            # Get HTML content
            response = requests.get(site)
            htmlContent = response.text

            # Parse HTML data and get email addresses 
            soup = BeautifulSoup(htmlContent, 'html.parser')
            text = soup.get_text()

            emailPattern = re.compile(r'([a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-z]{2,4})')
            emailMatches = re.findall(emailPattern, text)

            for email in emailMatches:
                if email != []:
                    townEmails.append(emailMatches[0])

        except:
            print("     Error scraping " + site)

    if len(townEmails) > 1:
        townEmails = list(set(townEmails))
    return townEmails
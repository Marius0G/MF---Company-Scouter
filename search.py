import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from googlesearch import search

def extract_contact_info(html):
    # TODO: optimize regex for phone and email ( .ro and .com for best results)
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(ro|com)", html)
    phones = re.findall(r"\+?\d[\d\s\-\(\)]{8,}\d", html)
    return set(emails), set(phones)

def checkIfUrlNotSite(url):
    siteExceptionFile = open("siteExceptionFile.cfg", "r")
    siteExceptions = siteExceptionFile.readlines()
    siteExceptionFile.close()
    
    for exception in siteExceptions:
        if exception.strip() in url:
            return False
    return True

query = "burgeri bucuresti" # TO DO: make it a command line argument
results = search(query, num_results=100)

subpagesFile = open("subPages.cfg", "r")
subpages = subpagesFile.readlines()
for i in range(len(subpages)):
    subpages[i] = subpages[i].strip()


for url in results:
    if(checkIfUrlNotSite(url) == False):
        continue
    print(f"🔍 Checking: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, timeout=5, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text()
            emails, phones = extract_contact_info(text)
            if emails or phones:
                print(f"\t✅ Found contact info at {url}")
                if emails:
                    print("\t   Emails:", ", ".join(emails))
                if phones:
                    print("\t   Phones:", ", ".join(phones))
            else:
                print(f"\t❌ No contact info found at {url}")
    except Exception as e:
        print(f"❌ Error with {url}: {e}")
    for subpage in subpages:
        subpageUrl = url  + subpage
        print(f"\t➤ Checking subpage: {subpageUrl}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(subpageUrl, timeout=5, headers=headers)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text()
                emails, phones = extract_contact_info(text)
                if emails or phones:
                    print(f"\t✅ Found contact info at {subpageUrl}")
                    if emails:
                        print("\t     Emails:", ", ".join(emails))
                    if phones:
                        print("\t     Phones:", ", ".join(phones))
                else:
                    print(f"\t❌ No contact info found at {subpageUrl}")
            else:
                print(f"\t❌ Error with {subpageUrl}: Page doesn't exist")
        except Exception as e:
            print(f"\t❌ Error with {subpageUrl}: {e}")



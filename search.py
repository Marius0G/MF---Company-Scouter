import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from googlesearch import search
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

lookupSize = 200

def saveInfoToFile(filename,emails, phones, url):
    with open(filename, 'a') as file:
        file.write(f"URL: {url}\n")
        if emails:
            file.write("Emails:\n")
            for email in emails:
                file.write(f"\t{email}\n")
        if phones:
            file.write("Phones:\n")
            for phone in phones:
                file.write(f"\t{phone}\n")
        file.write("\n")


def search_with_brave(query):
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Change if installed elsewhere

    options = Options()
    options.binary_location = brave_path
    options.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    print("🔐 Solve any CAPTCHA manually if it appears.")
    time.sleep(60)  # Give time to solve CAPTCHA manually

    links = []
    search_results = driver.find_elements("css selector", 'h3')
    for result in search_results:
        parent = result.find_element("xpath", '..')
        href = parent.get_attribute('href')
        if href:
            links.append(href)

    driver.quit()
    return links

def extract_contact_info(html):
    
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(?:ro|com)", html)
    phones = re.findall(r"(?:\+4|0+4)?\d{10}|(?:\+4)0(?: |-)\d{3}(?: |-)\d{3}(?: |-)\d{3}|0\d{3}(?: |-)\d{3}(?: |-)\d{3}", html)
    return set(emails), set(phones)

def checkIfUrlNotSite(url):
    siteExceptionFile = open("siteExceptionFile.cfg", "r")
    siteExceptions = siteExceptionFile.readlines()
    siteExceptionFile.close()
    
    for exception in siteExceptions:
        if exception.strip() in url:
            return False
    return True

query = "pizza bucuresti" # TODO: make it a command line argument

try:
    results = search(query, num_results=lookupSize,sleep_interval=random.uniform(5, 15))
except Exception as e:
    results = search_with_brave(query) # Optional, in caz de rate limitation pe google


subpagesFile = open("subPages.cfg", "r")
subpages = subpagesFile.readlines()
for i in range(len(subpages)):
    subpages[i] = subpages[i].strip()

def makeSubpageUrl(url, subpage):
    parsed = urlparse(url)
    path_parts = parsed.path.rstrip('/').split('/')

    if '.' in path_parts[-1]:
        # If last part is a file (has an extension), replace it
        path_parts[-1] = subpage
    elif path_parts[-1] != '':
        # If it's a path (like "products"), replace it
        path_parts[-1] = subpage
    else:
        # URL ends with '/', just add the subpage
        path_parts.append(subpage)

    new_path = '/'.join(path_parts)
    new_parsed = parsed._replace(path=new_path)
    return urlunparse(new_parsed)

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
                saveInfoToFile("contactInfo.txt", emails, phones, url)
                print(f"\t✅ Found contact info at {url}")
                if emails:
                    print("\t   Emails:", ", ".join(emails))
                if phones:
                    print("\t   Phones:", ", ".join(phones))
                    
            else:
                print(f"\t❌ No contact info found at {url}")
    except Exception as e:
        print(f"❌ Error with {url}: {e}")
    # Check subpages
    #TODO: Subpages sa fie set cu url-ul, sa nu fie informatii duplicate
    for subpage in subpages:
        subpageUrl = makeSubpageUrl(url, subpage.strip())
        print(subpageUrl)
        print(f"\t➤ Checking subpage: {subpageUrl}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(subpageUrl, timeout=5, headers=headers)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text()
                emails, phones = extract_contact_info(text)
                if emails or phones:
                    saveInfoToFile("contactInfo.txt", emails, phones, subpageUrl)
                    print(f"\t✅ Found contact info at {subpageUrl}")
                    if emails:
                        print("\t     Emails:", ", ".join(emails))
                    if phones:
                        print("\t   Phones:", ", ".join(phones))
                else:
                    print(f"\t❌ No contact info found at {subpageUrl}")
            else:
                print(f"\t❌ Error with {subpageUrl}: Page doesn't exist")
        except Exception as e:
            print(f"\t❌ Error with {subpageUrl}: {e}")



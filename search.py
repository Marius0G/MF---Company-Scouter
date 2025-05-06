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
import gspread
from google.oauth2.service_account import Credentials

query = "apa imbuteliata" # TODO: make it a command line argument
lookupSize = 200
# TODO: Tutorial in readme so it is clear for usage
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

# Google Sheets API setup
with open("googleJsonFilePath.cfg", "r") as jsonFile:
    jsonFilePath = jsonFile.read().strip()
    jsonFile.close()
creds = Credentials.from_service_account_file(
    jsonFilePath,
    scopes=SCOPES)
client = gspread.authorize(creds)
with open("sheetName.cfg", "r") as sheetIdFile:
    sheetName = sheetIdFile.read().strip()
    sheetIdFile.close()
sheet = client.open(sheetName).sheet1


visited_urls = set()
try:
    with open("visited.txt", "r") as f:
        for line in f:
            visited_urls.add(line.strip())
except FileNotFoundError:
    pass

def saveInfoToFile(filename,emails, phones, url):
    with open(filename, 'w') as file:
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

def saveInfoToSheet(emails, phones, url):
    # Check if the sheet is empty
    if sheet.cell(1, 1).value is None:
        print("Sheet is empty, adding headers...")
        sheet.append_row(["URL", "Emails", "Phones"])

    # Append the data to the sheet
    sheet.append_row([url, "\n".join(emails), "\n".join(phones)])


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
    if url in visited_urls:
        continue
    visited_urls.add(url)
    emails_per_url = set()
    phones_per_url = set()
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
                # saveInfoToFile("contactInfo.txt", emails, phones, url)
                # saveInfoToSheet(emails, phones, url)
                emails_per_url.update(emails)
                phones_per_url.update(phones)
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
        if subpageUrl in visited_urls:
            continue
        visited_urls.add(subpageUrl)
        print(f"\t➤ Checking subpage: {subpageUrl}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(subpageUrl, timeout=5, headers=headers)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text()
                emails, phones = extract_contact_info(text)
                if emails or phones:
                    # saveInfoToFile("contactInfo.txt", emails, phones, subpageUrl)
                    # saveInfoToSheet(emails, phones, subpageUrl)
                    emails_per_url.update(emails)
                    phones_per_url.update(phones)
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
    if emails_per_url or phones_per_url:

        saveInfoToFile("contactInfo.txt", emails_per_url, phones_per_url, url)
        saveInfoToSheet(emails_per_url, phones_per_url, url)
    emails_per_url.clear()
    phones_per_url.clear()
print("✅ Finished checking all URLs.")

with open("visited.txt", "a") as f:
    for url in visited_urls:
        f.write(url + "\n")


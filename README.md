# MF - Company Scouter


This Python script automates the process of searching Google for a given query (e.g., `burgers Romania`), visiting each website from the search results, and extracting contact information like **email addresses** and **phone numbers**, including from **contact subpages**.

---

## 🚀 Features

- Uses Google Search to gather relevant websites.
- Scrapes homepages **and** subpages like `/contact`, `/about`, etc.
- Extracts:
  - 📧 Email addresses
  - 📞 Phone numbers
- Cleans and deduplicates results.
- Easy to modify for other types of scraping (Instagram links, WhatsApp, etc.).

---

## 📦 Dependencies

Make sure you have Python 3.7+ installed.

Install the required packages with:

```bash
pip install -r requirements.txt
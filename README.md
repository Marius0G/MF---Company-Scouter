# 🕵️‍♂️ MF - Company Scouter

This Python script automates the process of searching the web for a specific query (e.g., `paste București`), visiting each resulting website, and scraping for contact information such as **email addresses** and **phone numbers**, even from typical subpages like `/contact`, `/about`, etc.

---

## 🚀 Features

- 🌐 Google Search integration using `googlesearch` or optionally, automated `Brave` browser fallback for scraping results.
- 🔎 Scans main pages and custom subpages (e.g., `/contact`, `/despre-noi`) for:
  - 📧 Email addresses
  - 📞 Phone numbers
- 📋 Saves results to both:
  - A local `contactInfo.txt` file
  - A connected Google Sheet
- 📀 Maintains a list of already-visited URLs (`visited.txt`) to avoid duplicates.
- ☁️ Uses Google Drive API to push data to a Google Sheet (credentials required).
- Configurable subpages, search terms, and exception filters via `.cfg` files.

---

## 🌆 Requirements

Make sure you have **Python 3.7+** installed. Then, install the required packages:

```bash
pip install -r requirements.txt
```

---

## 🧾 Setup

### 1. Clone/download this repo.
### 2. Install dependencies:
  ```bash
    pip install -r requirements.txt
  ```
### 3. Google Cloud Service Account Setup

To allow writing to Google Sheets:

#### a. Create a Google Cloud project

1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Click **"New Project"** and name it.

#### b. Enable APIs

Go to **APIs & Services > Library** and enable:

- **Google Sheets API**
- **Google Drive API**

#### c. Create a Service Account

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > Service Account**
3. Fill in the name and create it
4. Under your service account, go to **"Keys" > "Add Key" > "Create new key"**
5. Choose **JSON** and download the file

#### d. Share your Google Sheet

1. Open your Google Sheet
2. Share it with the **service account's email** (something like `your-bot@your-project.iam.gserviceaccount.com`)
3. Give **Editor** permissions
### 4. Create and configure the following files in the same directory:
    - `googleJsonFilePath.cfg`: Contains the **file path** to your Google Cloud service account JSON.
    - `sheetName.cfg`: Name of the Google Sheet you want to write into.
    - `siteExceptionFile.cfg`: One domain or keyword per line to exclude from scraping (e.g., `facebook.com`).
    - `subPages.cfg`: One subpage name per line to append and scrape after the main page (e.g., `contact`, `despre-noi`).

### 5. (Optional) Install Brave Browser and set the correct path in the script if you want to use the Brave fallback for Google search.

---

## ▶️ Usage

Run the script from terminal:

```bash
python search.py
```

The query to be searched is hardcoded in the script as of now:
```python
query = "paste bucuresti"
```

To make the script accept command-line arguments instead, replace the query line with:

```python
import sys
query = " ".join(sys.argv[1:])
```

And run like this:

```bash
python main.py paste bucuresti
```

---

## 🧪 Example Output

- ✅ `contactInfo.txt` will contain structured contact info from all scraped pages.
- ✅ Google Sheet will be automatically updated with new results.
- ✅ `visited.txt` will prevent rechecking the same URLs across runs.

---


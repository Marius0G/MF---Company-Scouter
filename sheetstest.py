import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

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
sheet = client.open(sheetName).sheet1 # First worksheet



sheet.update('A1', [['Hello, Google Sheets!']])

# Append a row


sheet.update('A1', [['Hello, 2', 'hello vrozzz']])
import gspread
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "Stoked Capsule JSON - Google Cloud Console.json", scopes=scopes
)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1BOhvQ4tHX6jYTD-L7-vUyUmRA4dTD5xeWONrSoDlcY4"
SHEET_NAME = "Sheet1"
API_KEY = "AIzaSyBqBlePNGkZ4BGRHvjHuMcouPwkUE7qDR0"

sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)


# ! =================================
def increment(x):
    """
    Increment the value in cell C1 by one
    """
    cell = sheet.acell(x)
    cell.value = str(int(cell.value) + 1)  # Increment the value by one
    sheet.update_acell(x, cell.value)


def get_value():
    """
    Return the value in cell C1
    """
    return sheet.acell("C1").value


def reset():
    """
    Reset the value in cell C1 to 0
    """
    sheet.update_acell("C1", 0)

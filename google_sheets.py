from receipt_class import receipt
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import config

#pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

creds_drive = None
creds_drive = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DRIVE)

# The ID of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.SAMPLE_SPREADSHEET_ID
DRIVE_FOLDER = config.DRIVE_FOLDER

def upload_picture(receipt):
    file_name = receipt.picture
    mime_type = 'image/jpeg'

    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER]
    }
    media = MediaFileUpload('./photos/{0}'.format(file_name), mimetype = mime_type)

    service = build('drive', 'v3', credentials=creds_drive)
    service.files().create(
        body=file_metadata,
        media_body = media,
        fields = 'id'
    ).execute()

def upload(receipt):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="receipts!A1").execute()

    values = result.get('values', [])
    inserted_values = int(values[0][0])

    date = receipt.date.strftime('%d/%m/%Y')
    timestamp = receipt.timestamp.strftime("%d/%m/%Y, %H:%M:%S")

    aoa = [[timestamp, date, receipt.cause, receipt.purpose, receipt.user_id, receipt.username, receipt.js_name, receipt.first_name, receipt.last_name, receipt.total, receipt.picture]]

    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range="receipts!B" + str(inserted_values + 2), valueInputOption="RAW", 
                body={"values" : aoa}).execute()
    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range="receipts!A1", valueInputOption="USER_ENTERED", 
                body={"values" : [[inserted_values + 1]]}).execute()

    upload_picture(receipt)

def read(user_id):
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="receipts!A1").execute()

    values = result.get('values', [])
    inserted_values = int(values[0][0])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                    range="receipts!B2:L" + str(inserted_values + 2)).execute()
    values = result.get('values', [])
    result = []
    
    for value in values:
        if int(value[4]) == user_id:
            result.append(value)
    return result

def read_js_name(js_name):
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="receipts!A1").execute()

    values = result.get('values', [])
    inserted_values = int(values[0][0])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                    range="receipts!B2:L" + str(inserted_values + 2)).execute()
    values = result.get('values', [])
    result = []
    
    for value in values:
        if str(value[6]) == js_name:
            result.append(value)
    return result

def read_all():
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="receipts!A1").execute()

    values = result.get('values', [])
    inserted_values = int(values[0][0])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                    range="receipts!B2:L" + str(inserted_values + 2)).execute()
    values = result.get('values', [])
    return values

def main():
    user_receipt = receipt( datetime.now(), datetime(2020, 3, 2), "sgjt", "sjtj",69, "djhdhj", "dghjdghj", "dgjhdhj", 45, 'Lukas-Meier-12CHF-2021-07-16.jpg')
    upload(user_receipt)
    upload_picture(user_receipt)
    print(read(69))

if __name__ == '__main__':
    main()
from googleapiclient.discovery import build

from global_constants import YOUR_API_KEY


def get_status_from_gsheet(spreadsheet_id, range_name):
    # build the service
    service = build('sheets', 'v4', developerKey=YOUR_API_KEY)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        # Assuming the first row is the header
        header = values[0]
        data = values[1:]

        # Create a dictionary for each member with their status
        members_status = {row[header.index('gh_username')]: row[header.index('status')] for row in data if len(row) > 1}
        return members_status

import os
import json
import requests
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

GH_TOKEN = os.getenv('GH_TOKEN')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SPREADSHEET_RANGE_NAME = os.getenv('SPREADSHEET_RANGE_NAME')
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Load the event data from the GitHub Actions context
with open(os.getenv('GITHUB_EVENT_PATH')) as event_file:
    event_data = json.load(event_file)

# Extract necessary data
org = 'your_org'
repo = 'your_repo'
issue_number = event_data['issue']['number']
issue_labels = [label['name'] for label in event_data['issue']['labels']]

def get_status_from_gsheet():
    creds = Credentials.from_service_account_info(json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')), scopes=SCOPE)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.get_worksheet(0)
    records = worksheet.get(SPREADSHEET_RANGE_NAME)
    return {record[0]: record[1] for record in records}

def get_members_from_team():
    team_members = []
    # Fetch team members
    response = requests.get(f"https://api.github.com/orgs/{org}/teams/your_team/members",
                            headers={"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"})
    if response.status_code == 200:
        team_members = [member['login'] for member in response.json()]
    return team_members

def get_issues_from_past_two_months(member):
    two_months_ago = (datetime.now() - timedelta(days=60)).isoformat() + 'Z'
    issues = []
    # Fetch issues
    response = requests.get(f"https://api.github.com/repos/{org}/{repo}/issues?assignee={member}&since={two_months_ago}&state=all",
                            headers={"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"})
    if response.status_code == 200:
        issues = response.json()
    return issues

def get_total_sp(issue_labels):
    total_sp = 0
    for label in issue_labels:
        if label.startswith('sp-'):
            try:
                sp = int(label.split('-')[1])
                total_sp += sp
            except:
                pass
    return total_sp

status_dict = get_status_from_gsheet()
members = get_members_from_team()

# Filter out busy members
members = [member for member in members if status_dict.get(member) != 'busy']

member_sp_dict = {}
for member in members:
    issues = get_issues_from_past_two_months(member)
    total_sp = sum(get_total_sp(issue['labels']) for issue in issues)
    member_sp_dict[member] = total_sp

# Find member with the least total sp points
assignee = min(member_sp_dict, key=member_sp_dict.get)

# Assign the issue
payload = {"assignees": [assignee]}
requests.post(f"https://api.github.com/repos/{org}/{repo}/issues/{issue_number}", headers={"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}, json=payload)

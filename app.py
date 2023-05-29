from flask import Flask, request
import requests
from datetime import datetime, timedelta

from global_constants import SPREADSHEET_ID, RANGE_NAME
from plugins.excel_connector import get_status_from_gsheet

app = Flask(__name__)

# Your GitHub token and headers
TOKEN = 'your_token',
HEADERS = {'Authorization': f'token {TOKEN}'}

# Org, team and repo info
ORG = 'your_org'
REPO = 'your_repo'
TEAM = 'your_team'

# Restrict list
RESTRICT_LIST = ['member1', 'member2']  # add the members who should not be autoassigned


@app.route('/webhook', methods=['POST'])
def respond():
    data = request.json
    action = data['action']
    issue = data['issue']

    if action == 'opened' and issue['title'].startswith('[BUG]'):
        assignee = find_assignee(ORG, TEAM)
        if assignee:
            assign_issue(issue['number'], assignee)

    return "OK", 200


def find_assignee(org, team):
    # Find the member with the least SP points
    members = get_team_members(org, team)
    sp_points = {member: get_sp_points_for_member(member) for member in members if not is_member_busy(member)}
    if sp_points:  # if the dictionary is not empty
        min_sp_member = min(sp_points, key=sp_points.get)
        return min_sp_member
    else:
        return None


def is_member_busy(member):
    members_status = get_status_from_gsheet(SPREADSHEET_ID, RANGE_NAME)
    return members_status.get(member, 'free') == 'busy'

# def is_member_busy(member):
#     # Implement your logic to check if a member is busy
#     # For now, let's return False for all members
#     return False


def get_team_members(org, team):
    url = f'https://api.github.com/orgs/{org}/teams/{team}/members'
    response = requests.get(url, headers=HEADERS)
    members = [member['login'] for member in response.json() if member['login'] not in RESTRICT_LIST]
    return members


def get_sp_points_for_member(member):
    sp_points = 0
    two_months_ago = datetime.now() - timedelta(days=60)

    url = f'https://api.github.com/repos/{ORG}/{REPO}/issues'
    params = {'assignee': member, 'state': 'all', 'since': two_months_ago.isoformat()}
    response = requests.get(url, headers=HEADERS, params=params)
    issues = response.json()

    for issue in issues:
        created_at = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        if created_at >= two_months_ago:
            for label in issue['labels']:
                if 'sp-' in label['name']:
                    try:
                        sp_points += int(label['name'].split('-')[1])
                    except ValueError:
                        continue

    return sp_points


def assign_issue(issue_number, assignee):
    url = f'https://api.github.com/repos/{ORG}/{REPO}/issues/{issue_number}'
    data = {'assignees': [assignee]}
    response = requests.patch(url, headers=HEADERS, json=data)
    return response.status_code == 200  # return True if assignment was successful


if __name__ == "__main__":
    app.run(port=5000, debug=True)

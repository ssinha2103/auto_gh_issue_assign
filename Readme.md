# Project: GitHub Issue Auto-Assigner

## Problem Statement:

In software development, the assignment of GitHub issues is often manual and may not always consider the current workload of the team members. It becomes problematic to distribute issues fairly, especially when considering the complexity of the tasks. Our task is to develop a Python script that automatically assigns GitHub issues to team members. The following constraints need to be taken into account:

1. Only issues labeled as "BUG" should be auto-assigned.
2. Issues should be assigned to the team member with the least "story points" from the last two months, to ensure fair distribution.
3. Some team members may be busy or unavailable and should be exempt from auto-assignment.
4. All of this should be automated, running whenever a new issue is created.

## Solution:

We developed a Flask application that listens to GitHub webhooks and automatically assigns issues based on the rules above. The application uses the GitHub API to fetch team members, issues, and the related "story points". 

To keep track of team members' availability, we are maintaining a Google Sheet. It lists all the team members with their GitHub usernames, and their status (busy or free). This Google Sheet data is read using Google Sheets API to determine the availability of team members for auto-assignment.

## Architecture:

```plaintext
+-----------+      +---------------------+           +-------------------+
| GitHub    |      | Python/Flask App    |           | GitHub API        |
|           |      |                     |           |                   |
| - Issues  | <--> | - Webhook Listener  | <-------> | - Fetch issues    |
| - Webhook |      | - Issue Assigner    |           | - Assign issues   |
+-----------+      | - Member Filter     |           | - Fetch members   |
                   | - SP Point Counter  |           +-------------------+
                   +---------------------+                      ^
                                ^                             |
                                |                     +-------------------+
                                |                     | Google Sheets API |
                                +--------------------- | - Fetch status    |
                                                      +-------------------+
```

1. **GitHub**: This is where your source code resides. It sends a webhook event whenever an issue labeled as "BUG" is opened. GitHub also hosts the API our application interacts with.

2. **Python/Flask App**: This is our application which listens to the webhook events and interacts with the GitHub API and Google Sheets API.

    - **Webhook Listener**: Listens to incoming webhook events from GitHub. If the event is the creation of an issue labeled as "BUG", it triggers the Issue Assigner.
    
    - **Issue Assigner**: Assigns the newly created issue to a team member. The member is selected by the Member Filter and SP Point Counter components.
    
    - **Member Filter**: Fetches all the members from the specified GitHub team and filters out any members on the restrict list or marked as busy in the Google Sheet.
    
    - **SP Point Counter**: Counts the story points assigned to each member over the past two months using the GitHub API. Helps the Issue Assigner decide to whom the issue should be assigned.

3. **GitHub API**: Our application uses this API to fetch issues, assign issues, and fetch members of a GitHub team.

4. **Google Sheets API**: Used by our application to fetch the status of the team members. The Google Sheet contains a list of all team members with their GitHub usernames and their current status (busy or free).

This architecture diagram outlines the high-level interactions between the components of our solution. For more detailed interactions and flow, refer to the source code of the application.

## Steps to Run:

1. Clone the repository.
2. Install the dependencies using pip: `pip install -r requirements.txt`.
3. Replace the placeholders in the script with your GitHub token, organization, repository, team, and the members who should not be autoassigned.
4. Implement the logic to check if a member is busy in the `is_member_busy` function.
5. Run the Flask app: `python app.py`.

## Conclusion:

The GitHub Issue Auto-Assigner script aims to automate issue assignment in a fair and efficient manner, taking into account team members' workloads and availability. This ensures that everyone gets an equal chance to contribute to the project, and no single person is overwhelmed with too many tasks. This way, we can focus more on coding and less on administrative tasks.
from dotenv import load_dotenv
import os
import requests

class GitHubScraper:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo = "flutter/flutter"
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {"Authorization": f"Bearer {self.github_token}"}

    def get_issues(self, per_page=5):
        url = f"{self.base_url}/issues"
        params = {"per_page": per_page}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_issue_comments(self, issue_number):
        url = f"{self.base_url}/issues/{issue_number}/comments"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_issue_str(self, issue):
        if issue['user']['type'] == "Bot":
            return ""

        comments = self.get_issue_comments(issue['number'])
        comments_str = ""
        for comment in comments:
            if comment['user']['type'] == "Bot":
                continue

            comments_str += f"""
{comment['user']['login']} commented on {comment['created_at']}.
Comment description:
{comment['body']}

"""
        if(len(comments) == 0):
            comments_str = "None"

        return f"""
User {issue['user']['login']} created issue #{issue['number']} titled {issue['title']} on {issue['created_at']}.
The issue is currently {issue['state']}.

Issue description:
{issue['body']}

Issue comments:
{comments_str}
"""

    def get_pull_requests(self, per_page=5):
        url = f"{self.base_url}/pulls"
        params = {"per_page": per_page}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_pull_request_comments(self, pull_request_number):
        url = f"{self.base_url}/pulls/{pull_request_number}/comments"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_pull_request_str(self, pull_request):
        if pull_request['user']['type'] == "Bot":
            return ""

        comments = self.get_pull_request_comments(pull_request['number'])
        comments_str = ""
        for comment in comments:
            if comment['user']['type'] == "Bot":
                continue

            comments_str += f"""
{comment['user']['login']} commented on {comment['created_at']}.
Comment description:
{comment['body']}

"""
        if(len(comments) == 0):
            comments_str = "None"

        return f"""
User {pull_request['user']['login']} created pull request #{pull_request['number']} titled {pull_request['title']} on {pull_request['created_at']}.
The pull request is currently {pull_request['state']}.

Pull request description:
{pull_request['body']}

Pull request comments:
{comments_str}
"""
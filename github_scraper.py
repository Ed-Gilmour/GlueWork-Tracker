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
        comments = self.get_issue_comments(issue['number'])
        comments_str = "None"
        for comment in comments:
            comments_str += f"- [{comment['created_at']}] {comment['user']['login']}: {comment['body']}\n"

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
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import requests

class GitHubScraper:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo = "flutter/flutter"
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {"Authorization": f"Bearer {self.github_token}"}

    def get_issues_updated_since(self, days=365, per_page=100):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        since_iso = cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")

        params = {
            "per_page": per_page,
            "since": since_iso,
            "state": "all",
            "direction": "desc",
            "sort": "updated"
        }

        all_issues = []
        url = self.base_url + "/issues"

        while url:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            issues = response.json()
            all_issues.extend(issues)

            params = {}

            link = response.headers.get("Link", "")
            url = None
            if link:
                parts = link.split(",")
                for part in parts:
                    if 'rel="next"' in part:
                        url = part[part.find("<")+1:part.find(">")]
                        break

        return all_issues

    def get_issue_comments(self, issue_number):
        url = f"{self.base_url}/issues/{issue_number}/comments"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_issue_str(self, issue):
#         if issue['user']['type'] == "Bot":
#             return ""

#         comments = self.get_issue_comments(issue['number'])
        comments_str = ""
#         for comment in comments:
#             if comment['user']['type'] == "Bot":
#                 continue

#             comments_str += f"""
# {comment['user']['login']} commented on {comment['created_at']}.
# Comment description:
# {comment['body']}

# """
#         if(len(comments) == 0):
#             comments_str = "None"

        message_str = f"""
User {issue['user']['login']} created issue #{issue['number']} titled {issue['title']} on {issue['created_at']}.
The issue is currently {issue['state']}.

Issue description:
{issue['body']}
"""

#         message_str += f"""
# Issue comments:
# {comments_str}
# """

        return message_str

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

if __name__ == "__main__":
    github_scraper = GitHubScraper()
    issues = github_scraper.get_issues_updated_since()
    print(f"Fetched {len(issues)} issues updated in the past year.")